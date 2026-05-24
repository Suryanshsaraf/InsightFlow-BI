"""
API version 1 root router.

Aggregates and prefixes child routers.
"""

from fastapi import APIRouter

from app.api.v1 import auth, charts, dashboards, datasets, insights, queries

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
router.include_router(dashboards.router, prefix="/dashboards", tags=["Dashboards"])
router.include_router(charts.router, prefix="/charts", tags=["Charts"])
router.include_router(queries.router, prefix="/queries", tags=["SQL Queries"])
router.include_router(insights.router, prefix="/insights", tags=["AI Insights"])
