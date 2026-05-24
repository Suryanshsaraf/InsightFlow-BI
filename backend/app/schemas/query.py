"""
Pydantic v2 schemas for NL-to-SQL query request/response payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.query_history import QueryStatus


class QueryRequest(BaseModel):
    """Natural-language query input."""

    question: str = Field(..., min_length=1, max_length=2000)
    dataset_id: str


class QueryResponse(BaseModel):
    """Response containing the generated SQL and its execution results."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    natural_language_query: str
    generated_sql: Optional[str] = None
    status: QueryStatus
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    result_row_count: int
    execution_time_ms: Optional[float] = None
    dataset_id: str
    created_at: datetime


class QueryHistoryItem(BaseModel):
    """Summarised query for history listing."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    natural_language_query: str
    status: QueryStatus
    result_row_count: int
    execution_time_ms: Optional[float] = None
    created_at: datetime


class QueryHistoryListResponse(BaseModel):
    """Paginated list of past queries."""

    items: List[QueryHistoryItem]
    total: int
    page: int
    page_size: int
