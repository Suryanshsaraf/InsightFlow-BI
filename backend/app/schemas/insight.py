"""
Pydantic v2 schemas for Insight request/response payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.insight import InsightType


class InsightRequest(BaseModel):
    """Request to generate insights for a dataset."""

    dataset_id: str
    focus_columns: Optional[List[str]] = None
    max_insights: int = Field(default=10, ge=1, le=50)


class InsightResponse(BaseModel):
    """Single insight returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    insight_type: InsightType
    confidence: float
    supporting_data: Optional[Dict[str, Any]] = None
    related_columns: Optional[Dict[str, Any]] = None
    suggested_chart_type: Optional[str] = None
    is_auto_generated: bool
    dataset_id: str
    created_at: datetime


class InsightListResponse(BaseModel):
    """Paginated list of insights."""

    items: List[InsightResponse]
    total: int
    page: int
    page_size: int
