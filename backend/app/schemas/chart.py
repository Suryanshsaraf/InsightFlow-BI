"""
Pydantic v2 schemas for Chart request/response payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.chart import ChartType


class ChartCreate(BaseModel):
    """Payload for creating a new chart."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    chart_type: ChartType
    dataset_id: str
    dashboard_id: Optional[str] = None
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    group_by_column: Optional[str] = None
    aggregation: Optional[str] = "sum"
    query: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    position_x: int = 0
    position_y: int = 0
    width: int = 6
    height: int = 4


class ChartUpdate(BaseModel):
    """Fields that can be updated on an existing chart."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    chart_type: Optional[ChartType] = None
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    group_by_column: Optional[str] = None
    aggregation: Optional[str] = None
    query: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    dashboard_id: Optional[str] = None


class ChartResponse(BaseModel):
    """Full chart representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    chart_type: ChartType
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    group_by_column: Optional[str] = None
    aggregation: Optional[str] = None
    query: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    cached_data: Optional[Dict[str, Any]] = None
    position_x: int
    position_y: int
    width: int
    height: int
    is_auto_generated: bool
    owner_id: str
    dataset_id: str
    dashboard_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ChartRecommendation(BaseModel):
    """A recommended chart configuration from the AI recommendation engine."""

    chart_type: ChartType
    title: str
    description: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    group_by_column: Optional[str] = None
    aggregation: Optional[str] = None
    reasoning: str


class ChartListResponse(BaseModel):
    """Paginated list of charts."""

    items: List[ChartResponse]
    total: int
    page: int
    page_size: int
