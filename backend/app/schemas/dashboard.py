"""
Pydantic v2 schemas for Dashboard request/response payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DashboardCreate(BaseModel):
    """Payload for creating a new dashboard."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    dataset_id: str
    layout_config: Optional[Dict[str, Any]] = None


class DashboardUpdate(BaseModel):
    """Fields that can be updated on an existing dashboard."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None


class DashboardResponse(BaseModel):
    """Full dashboard representation with nested chart summaries."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    is_auto_generated: bool
    owner_id: str
    dataset_id: str
    created_at: datetime
    updated_at: datetime
    charts: List[ChartBriefInDashboard] = Field(default_factory=list)


class ChartBriefInDashboard(BaseModel):
    """Minimal chart info embedded inside a dashboard response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    chart_type: str
    position_x: int
    position_y: int
    width: int
    height: int


# Resolve forward reference
DashboardResponse.model_rebuild()


class DashboardBrief(BaseModel):
    """Minimal dashboard info for listing endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    is_auto_generated: bool
    dataset_id: str
    created_at: datetime


class DashboardListResponse(BaseModel):
    """Paginated list of dashboards."""

    items: List[DashboardBrief]
    total: int
    page: int
    page_size: int
