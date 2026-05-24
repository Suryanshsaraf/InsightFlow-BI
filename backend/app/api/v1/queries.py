"""
Queries and NL-to-SQL API router.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.dataset import Dataset
from app.models.query_history import QueryHistory, QueryStatus
from app.models.user import User
from app.services.nl_to_sql import NLToSQLService
from app.services.query_engine import QueryEngineService
from app.core.exceptions import NotFoundException, SQLExecutionException, SQLSecurityException

router = APIRouter()


class ExecuteQueryPayload(BaseModel):
    datasetId: str
    sqlQuery: str


class TranslateQueryPayload(BaseModel):
    datasetId: str
    question: str


def format_history_item(item: QueryHistory) -> dict:
    """Format QueryHistory ORM to match frontend representation."""
    return {
        "id": item.id,
        "naturalLanguageQuery": item.natural_language_query,
        "sqlQuery": item.generated_sql or "",
        "status": item.status.value,
        "errorMessage": item.error_message or "",
        "rowCount": item.result_row_count,
        "executionTimeMs": item.execution_time_ms or 0.0,
        "createdAt": item.created_at.isoformat() if item.created_at else "",
    }


@router.post("/execute")
async def execute_raw_sql(
    payload: ExecuteQueryPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a raw user SQL query after checking security constraints.
    Logs execution in query history.
    """
    # 1. Fetch Dataset
    stmt = select(Dataset).where(Dataset.id == payload.datasetId, Dataset.owner_id == current_user.id)
    res = await db.execute(stmt)
    dataset = res.scalar_one_or_none()
    
    if not dataset:
        raise NotFoundException("Dataset not found")
        
    # Create a pending query log
    history_item = QueryHistory(
        natural_language_query="Raw SQL Query",
        generated_sql=payload.sqlQuery,
        status=QueryStatus.RUNNING,
        user_id=current_user.id,
        dataset_id=dataset.id,
    )
    db.add(history_item)
    await db.commit()
    
    try:
        # Run query
        rows, time_ms = await QueryEngineService.execute_query(db, dataset, payload.sqlQuery)
        
        # Update log to completed
        history_item.status = QueryStatus.COMPLETED
        history_item.result_row_count = len(rows)
        history_item.execution_time_ms = time_ms
        history_item.result_data = {"rows": rows}
        await db.commit()
        await db.refresh(history_item)
        
        return {
            "queryId": history_item.id,
            "sqlQuery": payload.sqlQuery,
            "results": rows,
            "executionTimeMs": time_ms,
            "status": "success",
        }
        
    except (SQLSecurityException, SQLExecutionException) as e:
        history_item.status = QueryStatus.FAILED
        history_item.error_message = e.message
        await db.commit()
        raise e
    except Exception as e:
        history_item.status = QueryStatus.FAILED
        history_item.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/natural-language")
async def execute_natural_language_query(
    payload: TranslateQueryPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Convert a user's natural language question to a SQL query,
    execute it, and save the transaction history.
    """
    # 1. Fetch Dataset
    stmt = select(Dataset).where(Dataset.id == payload.datasetId, Dataset.owner_id == current_user.id)
    res = await db.execute(stmt)
    dataset = res.scalar_one_or_none()
    
    if not dataset or not dataset.column_schema or not dataset.statistics:
        raise NotFoundException("Dataset not found or is still processing.")
        
    # Create a pending query log
    history_item = QueryHistory(
        natural_language_query=payload.question,
        status=QueryStatus.RUNNING,
        user_id=current_user.id,
        dataset_id=dataset.id,
    )
    db.add(history_item)
    await db.commit()
    
    sql_query = None
    try:
        # Translate question to SQL using OpenAI
        sql_query = await NLToSQLService.translate_query(
            dataset.table_name,
            dataset.column_schema,
            dataset.statistics,
            payload.question,
        )
        
        history_item.generated_sql = sql_query
        
        # Execute generated SQL
        rows, time_ms = await QueryEngineService.execute_query(db, dataset, sql_query)
        
        # Update log to completed
        history_item.status = QueryStatus.COMPLETED
        history_item.result_row_count = len(rows)
        history_item.execution_time_ms = time_ms
        history_item.result_data = {"rows": rows}
        await db.commit()
        await db.refresh(history_item)
        
        return {
            "queryId": history_item.id,
            "sqlQuery": sql_query,
            "results": rows,
            "executionTimeMs": time_ms,
            "status": "success",
        }
        
    except Exception as e:
        history_item.status = QueryStatus.FAILED
        err_msg = e.message if hasattr(e, "message") else str(e)
        history_item.error_message = err_msg
        if sql_query:
            history_item.generated_sql = sql_query
        await db.commit()
        
        if isinstance(e, (SQLSecurityException, SQLExecutionException)):
            raise e
        raise HTTPException(status_code=400, detail=err_msg)


@router.get("/history")
async def get_query_history(
    datasetId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical queries executed on this dataset."""
    stmt = (
        select(QueryHistory)
        .where(
            QueryHistory.dataset_id == datasetId,
            QueryHistory.user_id == current_user.id,
        )
        .order_by(QueryHistory.created_at.desc())
        .limit(50)
    )
    res = await db.execute(stmt)
    items = res.scalars().all()
    
    return [format_history_item(item) for item in items]
