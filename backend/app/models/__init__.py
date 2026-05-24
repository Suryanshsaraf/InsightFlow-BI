"""
Models package — re-exports all ORM models for convenient import.

Usage::

    from app.models import User, Dataset, Dashboard, Chart, QueryHistory, Insight
"""

from app.models.chart import Chart, ChartType
from app.models.dashboard import Dashboard
from app.models.dataset import Dataset, DatasetStatus
from app.models.insight import Insight, InsightType
from app.models.query_history import QueryHistory, QueryStatus
from app.models.user import User

__all__ = [
    "User",
    "Dataset",
    "DatasetStatus",
    "Dashboard",
    "Chart",
    "ChartType",
    "QueryHistory",
    "QueryStatus",
    "Insight",
    "InsightType",
]
