"""
Schemas package — re-exports all Pydantic models.
"""

from app.schemas.chart import (
    ChartCreate,
    ChartListResponse,
    ChartRecommendation,
    ChartResponse,
    ChartUpdate,
)
from app.schemas.dashboard import (
    DashboardBrief,
    DashboardCreate,
    DashboardListResponse,
    DashboardResponse,
    DashboardUpdate,
)
from app.schemas.dataset import (
    ColumnInfo,
    DatasetBrief,
    DatasetCreate,
    DatasetListResponse,
    DatasetResponse,
    DatasetUpdate,
)
from app.schemas.insight import InsightListResponse, InsightRequest, InsightResponse
from app.schemas.query import (
    QueryHistoryItem,
    QueryHistoryListResponse,
    QueryRequest,
    QueryResponse,
)
from app.schemas.user import (
    UserBrief,
    UserChangePassword,
    UserCreate,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserChangePassword",
    "UserResponse",
    "UserBrief",
    # Dataset
    "DatasetCreate",
    "DatasetUpdate",
    "DatasetResponse",
    "DatasetBrief",
    "DatasetListResponse",
    "ColumnInfo",
    # Dashboard
    "DashboardCreate",
    "DashboardUpdate",
    "DashboardResponse",
    "DashboardBrief",
    "DashboardListResponse",
    # Chart
    "ChartCreate",
    "ChartUpdate",
    "ChartResponse",
    "ChartRecommendation",
    "ChartListResponse",
    # Query
    "QueryRequest",
    "QueryResponse",
    "QueryHistoryItem",
    "QueryHistoryListResponse",
    # Insight
    "InsightRequest",
    "InsightResponse",
    "InsightListResponse",
]
