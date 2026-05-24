"""
Pydantic v2 schemas for Dataset request/response payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.dataset import DatasetStatus


class DatasetCreate(BaseModel):
    """Metadata supplied when uploading a new dataset (file sent as form data)."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class DatasetUpdate(BaseModel):
    """Fields that can be updated on an existing dataset."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ColumnInfo(BaseModel):
    """Schema for a single column's metadata."""

    name: str
    dtype: str
    nullable: bool = True
    unique_count: int = 0
    sample_values: List[Any] = Field(default_factory=list)


class DatasetResponse(BaseModel):
    """Full dataset representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    file_name: str
    file_size_bytes: int
    mime_type: str
    status: DatasetStatus
    error_message: Optional[str] = None
    table_name: Optional[str] = None
    column_schema: Optional[Dict[str, Any]] = None
    row_count: int
    column_count: int
    sample_data: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    detected_kpis: Optional[Dict[str, Any]] = None
    owner_id: str
    created_at: datetime
    updated_at: datetime


class DatasetBrief(BaseModel):
    """Minimal dataset info for listing endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: DatasetStatus
    row_count: int
    column_count: int
    created_at: datetime


class DatasetListResponse(BaseModel):
    """Paginated list of datasets."""

    items: List[DatasetBrief]
    total: int
    page: int
    page_size: int
