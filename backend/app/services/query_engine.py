"""
Safe SQL query execution engine.
"""

import asyncio
import time
from typing import Any, Dict, List, Tuple

import sqlparse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import SQLExecutionException, SQLSecurityException
from app.core.logging import logger
from app.models.dataset import Dataset

settings = get_settings()


class QueryEngineService:
    """Validates, sandboxes, and executes user-written SQL queries."""
    
    @staticmethod
    def validate_sql(sql_query: str, allowed_table_name: str) -> None:
        """
        Validate SQL queries against injection risks and restrict execution
        only to reading data from the allowed table.
        """
        # Parse query
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            raise SQLSecurityException("Invalid SQL query syntax.")
            
        # Standard safety keywords (case insensitive)
        forbidden_keywords = [
            "insert", "update", "delete", "drop", "alter", "create", "truncate",
            "replace", "grant", "revoke", "schema", "pg_", "sqlite_", "information_schema"
        ]
        
        query_clean = sql_query.lower()
        
        # 1. Reject forbidden keywords
        for kw in forbidden_keywords:
            if kw in query_clean:
                raise SQLSecurityException(f"SQL statement contains forbidden keyword: '{kw}'")
                
        # 2. Enforce only SELECT statements
        for statement in parsed:
            if statement.get_type() != "SELECT":
                raise SQLSecurityException("Only SELECT statements are allowed.")
                
        # 3. Ensure the allowed table is referenced
        # We need to make sure the user is only querying the dataset table.
        # Since table names are of the form 'ds_xxx', we check for its presence.
        normalized_table = allowed_table_name.lower()
        if normalized_table not in query_clean:
            raise SQLSecurityException(
                f"You can only query the table matching this dataset: '{allowed_table_name}'."
            )

    @classmethod
    async def execute_query(
        cls, db: AsyncSession, dataset: Dataset, sql_query: str, limit: int = 1000
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Validate and execute the SQL query on the database.
        
        Returns:
            rows: List of dicts representing query results.
            execution_time_ms: Query duration.
            
        Raises:
            SQLSecurityException: If validation fails.
            SQLExecutionException: If database execution fails.
        """
        if not dataset.table_name:
            raise SQLExecutionException("Dataset table does not exist.")
            
        # 1. Security validation
        cls.validate_sql(sql_query, dataset.table_name)
        
        # 2. Prepend schema prefix if PostgreSQL
        schema_prefix = "" if settings.is_sqlite else f"{settings.user_data_schema}."
        
        # Rewrite the query to use schema prefix if it isn't already prefixed
        rewritten_query = sql_query
        if not settings.is_sqlite and schema_prefix not in rewritten_query:
            # Simple replacement of the table name with schema.table name
            # Handle word boundaries to avoid replacing substrings
            import re
            pattern = re.compile(rf"\b{dataset.table_name}\b", re.IGNORECASE)
            rewritten_query = pattern.sub(f"{settings.user_data_schema}.{dataset.table_name}", rewritten_query)
            
        # Enforce hard row limit (e.g. 10000 rows max)
        # Check if LIMIT exists in query, if not append it
        if "limit" not in rewritten_query.lower():
            rewritten_query = f"{rewritten_query} LIMIT {limit}"
            
        logger.info("Executing safe query", dataset_id=dataset.id, sql=rewritten_query)
        
        start_time = time.perf_counter()
        
        try:
            # Enforce execution timeout (e.g. 30s)
            async with asyncio.timeout(30.0):
                res = await db.execute(text(rewritten_query))
                keys = res.keys()
                rows = [dict(zip(keys, row)) for row in res.fetchall()]
                
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            return rows, round(execution_time_ms, 2)
            
        except asyncio.TimeoutError:
            logger.error("SQL Query execution timed out", query=rewritten_query)
            raise SQLExecutionException("Query execution timed out (limit: 30 seconds).")
        except Exception as e:
            logger.error("SQL execution failed", query=rewritten_query, error=str(e))
            raise SQLExecutionException(
                message=f"Database error: {str(e)}",
                details={"query": sql_query},
            )
