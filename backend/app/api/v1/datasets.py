"""
Datasets API router.
"""

import os
import shutil
import uuid
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import (
    CSVProcessingException,
    FileTooLargeException,
    InvalidFileTypeException,
    DatasetNotFoundException,
)
from app.core.logging import logger
from app.database import engine, get_db
from app.dependencies import get_current_user
from app.models.dataset import Dataset, DatasetStatus
from app.models.user import User
from app.services.csv_processor import CSVProcessorService
from app.services.dashboard_generator import DashboardGeneratorService
from app.services.table_creator import TableCreatorService

settings = get_settings()
router = APIRouter()


def format_dataset_response(dataset: Dataset) -> dict:
    """Format ORM Dataset to match frontend expected structure."""
    columns = []
    if dataset.column_schema and dataset.statistics:
        for col_name, col_meta in dataset.column_schema.items():
            col_stats = dataset.statistics.get(col_name, {})
            
            inferred_type = col_meta["inferred_type"]
            frontend_type = "string"
            if inferred_type == "numeric":
                frontend_type = "number"
            elif inferred_type == "datetime":
                frontend_type = "date"
            elif inferred_type == "boolean":
                frontend_type = "boolean"
                
            unique_cnt = col_stats.get("unique_count", 0)
            top_vals = col_stats.get("top_values", [])
            sample_vals = [x["value"] for x in top_vals] if top_vals else []
            
            stats_data = {
                "nullCount": col_stats.get("null_count", 0),
                "distinctCount": unique_cnt,
            }
            
            if inferred_type == "numeric":
                stats_data.update({
                    "min": col_stats.get("min"),
                    "max": col_stats.get("max"),
                    "mean": col_stats.get("mean"),
                    "median": col_stats.get("median"),
                    "stdDev": col_stats.get("std"),
                })
                
            columns.append({
                "name": col_name,
                "type": frontend_type,
                "nullable": col_meta.get("nullable", True),
                "uniqueCount": unique_cnt,
                "sampleValues": sample_vals,
                "stats": stats_data,
            })
            
    # Preview data formatting if sample exists
    preview_data = []
    if dataset.sample_data and "rows" in dataset.sample_data:
        preview_data = dataset.sample_data["rows"]
        
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description or "",
        "fileName": dataset.file_name,
        "fileSize": dataset.file_size_bytes,
        "fileType": "csv",  # default MVP type
        "rowCount": dataset.row_count,
        "columnCount": dataset.column_count,
        "columns": columns,
        "status": dataset.status.value,
        "createdAt": dataset.created_at.isoformat() if dataset.created_at else "",
        "updatedAt": dataset.updated_at.isoformat() if dataset.updated_at else "",
        "createdBy": dataset.owner_id,
        "tags": [],
        "previewData": preview_data,
    }


async def process_dataset_background(dataset_id: str):
    """
    Background task to clean CSV, infer types, create dynamic table,
    bulk insert records, compute KPIs, and auto-generate dashboard.
    """
    logger.info("Starting background processing of dataset", dataset_id=dataset_id)
    
    # We open a dedicated DB session since this runs outside standard request lifecycle
    from app.database import async_session_factory
    async with async_session_factory() as db:
        stmt = select(Dataset).where(Dataset.id == dataset_id)
        result = await db.execute(stmt)
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            logger.error("Dataset not found in background task", dataset_id=dataset_id)
            return
            
        try:
            dataset.status = DatasetStatus.PROCESSING
            await db.commit()
            
            # 1. Clean, infer schema, compute stats
            df, schema, stats, sample = CSVProcessorService.analyze_dataset(dataset.file_path)
            
            # Save stats onto model
            dataset.column_schema = schema
            dataset.statistics = stats
            dataset.sample_data = sample
            dataset.row_count = len(df)
            dataset.column_count = len(df.columns)
            
            # Generate a safe table name (e.g. ds_shortuuid_datasetname)
            safe_name = f"ds_{uuid.uuid4().hex[:8]}_{dataset.name}"
            safe_name = CSVProcessorService.normalize_column_name(safe_name)
            dataset.table_name = safe_name
            
            # 2. Create the dynamic SQL table in the db
            await TableCreatorService.create_dynamic_table(
                engine, safe_name, schema
            )
            
            # 3. Bulk insert dataset rows into the dynamic table
            await TableCreatorService.insert_data(
                engine, safe_name, df, schema
            )
            
            # 4. Auto-generate the Dashboard & compute KPIs
            # (DashboardGeneratorService does db commits and populates dataset.detected_kpis)
            dataset.status = DatasetStatus.READY
            await db.commit()
            
            # Generate dashboard
            await DashboardGeneratorService.generate_dashboard(db, dataset)
            
            logger.info("Successfully finished processing dataset", dataset_id=dataset_id)
            
        except Exception as e:
            logger.exception("Failed to process dataset in background", dataset_id=dataset_id)
            dataset.status = DatasetStatus.ERROR
            dataset.error_message = str(e)
            await db.commit()


@router.post("/upload")
async def upload_dataset(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a CSV dataset. Saves file to disk, creates pending record,
    and spawns background task for data profiling and ingestion.
    """
    # 1. Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != ".csv":
        raise InvalidFileTypeException("Only CSV files are supported in the MVP.")
        
    # 2. Setup path
    dataset_id = str(uuid.uuid4())
    file_name = f"{dataset_id}.csv"
    file_path = os.path.join(settings.upload_path, file_name)
    
    # 3. Stream upload file to disk and check file size
    file_size = 0
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(64 * 1024):  # 64KB chunks
                file_size += len(chunk)
                if file_size > settings.max_upload_size_bytes:
                    raise FileTooLargeException(settings.max_upload_size_mb)
                buffer.write(chunk)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        if isinstance(e, FileTooLargeException):
            raise e
        logger.exception("File save failed during upload")
        raise CSVProcessingException(f"Failed to save file: {str(e)}")
        
    # 4. Create database pending record
    dataset = Dataset(
        id=dataset_id,
        name=name,
        description=description,
        file_name=file.filename,
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=file.content_type or "text/csv",
        status=DatasetStatus.PENDING,
        owner_id=current_user.id,
    )
    
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    
    # 5. Queue background execution task
    background_tasks.add_task(process_dataset_background, dataset.id)
    
    # Format and return immediate Response
    return format_dataset_response(dataset)


@router.get("/")
async def list_datasets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all datasets owned by the current user."""
    stmt = select(Dataset).where(Dataset.owner_id == current_user.id).order_by(Dataset.created_at.desc())
    res = await db.execute(stmt)
    datasets = res.scalars().all()
    
    return [format_dataset_response(d) for d in datasets]


@router.get("/{id}")
async def get_dataset(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed metadata and schema details for a specific dataset."""
    stmt = select(Dataset).where(Dataset.id == id, Dataset.owner_id == current_user.id)
    res = await db.execute(stmt)
    dataset = res.scalar_one_or_none()
    
    if not dataset:
        raise DatasetNotFoundException()
        
    return format_dataset_response(dataset)


@router.delete("/{id}")
async def delete_dataset(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a dataset, drops its associated SQL table, and deletes file from disk."""
    stmt = select(Dataset).where(Dataset.id == id, Dataset.owner_id == current_user.id)
    res = await db.execute(stmt)
    dataset = res.scalar_one_or_none()
    
    if not dataset:
        raise DatasetNotFoundException()
        
    # Drop table from database
    if dataset.table_name:
        await TableCreatorService.drop_dynamic_table(engine, dataset.table_name)
        
    # Delete file from local storage
    if os.path.exists(dataset.file_path):
        try:
            os.remove(dataset.file_path)
        except OSError as e:
            logger.warning("Could not delete file from disk", path=dataset.file_path, error=str(e))
            
    await db.delete(dataset)
    await db.commit()
    
    return {"success": True, "message": "Dataset deleted successfully"}
