"""
Charts API router.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.chart import Chart
from app.models.dataset import Dataset
from app.models.user import User
from app.services.dashboard_generator import DashboardGeneratorService
from app.core.exceptions import NotFoundException
from app.core.logging import logger

router = APIRouter()


class FilterItem(BaseModel):
    column: str
    operator: str  # eq, neq, gt, gte, lt, lte, contains, in
    value: Any


class ChartFilterPayload(BaseModel):
    filters: List[FilterItem]


@router.post("/{id}/data")
async def get_chart_data(
    id: str,
    payload: ChartFilterPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a dynamic SQL query to fetch chart data with interactive filters applied.
    """
    # 1. Fetch Chart
    stmt = select(Chart).where(Chart.id == id, Chart.owner_id == current_user.id)
    res = await db.execute(stmt)
    chart = res.scalar_one_or_none()
    
    if not chart:
        raise NotFoundException("Chart not found")
        
    # 2. Fetch associated Dataset to get table name
    dataset_stmt = select(Dataset).where(Dataset.id == chart.dataset_id)
    dataset_res = await db.execute(dataset_stmt)
    dataset = dataset_res.scalar_one_or_none()
    
    if not dataset or not dataset.table_name:
        raise NotFoundException("Dataset or associated SQL table not found")
        
    # If no filters are provided, return the cached data immediately
    if not payload.filters:
        rows = chart.cached_data.get("rows", []) if chart.cached_data else []
        return {"rows": rows}
        
    schema_prefix = "" if settings.is_sqlite else f"{settings.user_data_schema}."
    
    # 3. Dynamically build WHERE clause
    where_clauses = []
    query_params = {}
    
    for i, f in enumerate(payload.filters):
        # Validate column name exists in schema to prevent SQL Injection in column names
        if not dataset.column_schema or f.column not in dataset.column_schema:
            continue
            
        param_name = f"val_{i}"
        op = f.operator.lower()
        
        if op == "eq":
            where_clauses.append(f"{f.column} = :{param_name}")
            query_params[param_name] = f.value
        elif op == "neq":
            where_clauses.append(f"{f.column} != :{param_name}")
            query_params[param_name] = f.value
        elif op == "gt":
            where_clauses.append(f"{f.column} > :{param_name}")
            query_params[param_name] = f.value
        elif op == "gte":
            where_clauses.append(f"{f.column} >= :{param_name}")
            query_params[param_name] = f.value
        elif op == "lt":
            where_clauses.append(f"{f.column} < :{param_name}")
            query_params[param_name] = f.value
        elif op == "lte":
            where_clauses.append(f"{f.column} <= :{param_name}")
            query_params[param_name] = f.value
        elif op == "contains":
            where_clauses.append(f"{f.column} LIKE :{param_name}")
            query_params[param_name] = f"%{f.value}%"
        elif op == "in":
            # For IN, we construct values
            if isinstance(f.value, list):
                # e.g. val_in_0_0, val_in_0_1 ...
                in_names = []
                for j, item in enumerate(f.value):
                    sub_param = f"val_{i}_{j}"
                    in_names.append(f":{sub_param}")
                    query_params[sub_param] = item
                where_clauses.append(f"{f.column} IN ({', '.join(in_names)})")
            else:
                where_clauses.append(f"{f.column} = :{param_name}")
                query_params[param_name] = f.value
                
    where_str = ""
    if where_clauses:
        where_str = f"WHERE {' AND '.join(where_clauses)}"
        
    x_col = chart.x_column
    y_col = chart.y_column
    agg = chart.aggregation
    
    # 4. Construct SQL Query based on aggregation
    if chart.chart_type == "table" or not x_col or not y_col:
        q = f"SELECT * FROM {schema_prefix}{dataset.table_name} {where_str} LIMIT 100"
    elif chart.chart_type == "scatter" or not agg:
        # For scatter, filter out nulls for X/Y
        filter_nulls = f"{'AND' if where_clauses else 'WHERE'} {x_col} IS NOT NULL AND {y_col} IS NOT NULL"
        q = f"SELECT {x_col}, {y_col} FROM {schema_prefix}{dataset.table_name} {where_str} {filter_nulls} LIMIT 500"
    else:
        filter_nulls = f"{'AND' if where_clauses else 'WHERE'} {x_col} IS NOT NULL AND {y_col} IS NOT NULL"
        q = f"""
            SELECT {x_col}, {agg.upper()}({y_col}) AS {y_col}
            FROM {schema_prefix}{dataset.table_name}
            {where_str}
            {filter_nulls}
            GROUP BY {x_col}
            ORDER BY {y_col} DESC
            LIMIT 100
        """
        
    try:
        rows = await DashboardGeneratorService.run_query(db, q, query_params)
        
        # Sort line/area chronologically on client request
        if chart.chart_type in ["line", "area"] and x_col:
            rows.sort(key=lambda r: str(r[x_col]) if r[x_col] is not None else "")
            
        return {"rows": rows}
        
    except Exception as e:
        logger.error("Failed to run filtered chart query", sql=q, error=str(e))
        raise HTTPException(status_code=400, detail=f"Database query failed: {str(e)}")
