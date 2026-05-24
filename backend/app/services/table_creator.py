"""
Service for dynamic SQL table creation and bulk insertion of dataset rows.
"""

from typing import Any, Dict, List

import pandas as pd
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    MetaData,
    String,
    Table,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import get_settings
from app.core.exceptions import SQLExecutionException
from app.core.logging import logger

settings = get_settings()


class TableCreatorService:
    """Creates database tables dynamically and loads data into them."""
    
    @staticmethod
    def get_sqlalchemy_type(inferred_type: str) -> Any:
        """Map inferred type to SQLAlchemy column type."""
        if inferred_type == "numeric":
            return Float
        elif inferred_type == "datetime":
            return DateTime(timezone=True)
        elif inferred_type == "boolean":
            return Boolean
        elif inferred_type == "categorical":
            return String(255)
        else:
            return Text

    @classmethod
    async def create_dynamic_table(
        cls,
        engine: AsyncEngine,
        table_name: str,
        column_schema: Dict[str, Dict[str, Any]],
    ) -> Table:
        """
        Dynamically create a database table.
        
        Args:
            engine: The SQLAlchemy AsyncEngine.
            table_name: Normalized name of the target table.
            column_schema: Column configuration containing inferred types.
        """
        # Determine the target schema
        target_schema = None if settings.is_sqlite else settings.user_data_schema
        
        metadata = MetaData()
        
        columns = [
            Column("id", Float, primary_key=True, autoincrement=True)  # Add a simple autoincrement ID row
        ]
        
        # Add dynamic columns
        for col_name, col_meta in column_schema.items():
            db_type = cls.get_sqlalchemy_type(col_meta["inferred_type"])
            columns.append(
                Column(
                    col_name,
                    db_type,
                    nullable=col_meta.get("nullable", True),
                )
            )
            
        table = Table(
            table_name,
            metadata,
            *columns,
            schema=target_schema,
        )
        
        try:
            # Create the table in the database
            async with engine.begin() as conn:
                # Ensure the schema exists for PostgreSQL
                if not settings.is_sqlite:
                    from sqlalchemy import text
                    await conn.execute(
                        text(f"CREATE SCHEMA IF NOT EXISTS {settings.user_data_schema}")
                    )
                await conn.run_sync(metadata.create_all)
                
            logger.info("Created dynamic table", table_name=table_name, schema=target_schema)
            return table
            
        except Exception as e:
            logger.exception("Failed to create dynamic table", table_name=table_name)
            raise SQLExecutionException(
                message=f"Failed to create dynamic table: {str(e)}",
                details={"table_name": table_name},
            )

    @classmethod
    async def insert_data(
        cls,
        engine: AsyncEngine,
        table_name: str,
        df: pd.DataFrame,
        column_schema: Dict[str, Dict[str, Any]],
        chunk_size: int = 5000,
    ) -> int:
        """
        Insert DataFrame rows into the dynamic table in chunks.
        
        Returns:
            The total number of rows inserted.
        """
        target_schema = None if settings.is_sqlite else settings.user_data_schema
        
        # Convert datetime columns to pandas datetime objects for correct DB insertion
        df_copy = df.copy()
        for col_name, col_meta in column_schema.items():
            if col_meta["inferred_type"] == "datetime":
                df_copy[col_name] = pd.to_datetime(df_copy[col_name], errors="coerce")
                
        # Re-bind the table definition
        metadata = MetaData()
        columns = [Column("id", Float, primary_key=True, autoincrement=True)]
        for col_name, col_meta in column_schema.items():
            db_type = cls.get_sqlalchemy_type(col_meta["inferred_type"])
            columns.append(Column(col_name, db_type, nullable=col_meta.get("nullable", True)))
            
        table = Table(
            table_name,
            metadata,
            *columns,
            schema=target_schema,
        )
        
        total_rows = len(df_copy)
        inserted_rows = 0
        
        try:
            # Insert chunks using connection.execute()
            async with engine.begin() as conn:
                for start_idx in range(0, total_rows, chunk_size):
                    chunk = df_copy.iloc[start_idx : start_idx + chunk_size]
                    
                    # Convert chunk rows to list of dictionaries.
                    # Handle NaN, NaT by replacing them with None.
                    records = chunk.to_dict(orient="records")
                    cleaned_records = []
                    for record in records:
                        # Clean individual cells
                        cleaned_record = {}
                        for k, v in record.items():
                            if pd.isna(v):
                                cleaned_record[k] = None
                            else:
                                cleaned_record[k] = v
                        cleaned_records.append(cleaned_record)
                        
                    if cleaned_records:
                        await conn.execute(table.insert(), cleaned_records)
                        inserted_rows += len(cleaned_records)
                        
            logger.info("Bulk insertion complete", table_name=table_name, rows=inserted_rows)
            return inserted_rows
            
        except Exception as e:
            logger.exception("Failed bulk insertion into dynamic table", table_name=table_name)
            raise SQLExecutionException(
                message=f"Failed to insert data into dynamic table: {str(e)}",
                details={"table_name": table_name},
            )
            
    @classmethod
    async def drop_dynamic_table(cls, engine: AsyncEngine, table_name: str) -> None:
        """Drop a dynamic table if it exists."""
        target_schema = None if settings.is_sqlite else settings.user_data_schema
        
        metadata = MetaData()
        # Bind minimal table schema just to be able to drop it
        table = Table(
            table_name,
            metadata,
            Column("id", Float, primary_key=True),
            schema=target_schema,
        )
        
        try:
            async with engine.begin() as conn:
                await conn.run_sync(metadata.drop_all)
            logger.info("Dropped dynamic table", table_name=table_name)
        except Exception as e:
            logger.warning("Could not drop dynamic table", table_name=table_name, error=str(e))
