"""
Dashboards API router.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.chart import Chart
from app.models.dashboard import Dashboard
from app.models.user import User
from app.core.exceptions import DashboardNotFoundException

router = APIRouter()


class DashboardUpdatePayload(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    layoutConfig: Optional[Dict[str, Any]] = None


def format_chart_response(chart: Chart) -> dict:
    """Format ORM Chart to match frontend expected structure."""
    chart_type_val = chart.chart_type.value
    # Map backend types to frontend supported ChartType enum
    # 'line' | 'bar' | 'pie' | 'area' | 'table'
    if chart_type_val == "donut":
        chart_type_val = "pie"
    elif chart_type_val not in ["line", "bar", "pie", "area", "table"]:
        chart_type_val = "table"
        
    x_label = chart.x_column.replace("_", " ").title() if chart.x_column else ""
    y_label = chart.y_column.replace("_", " ").title() if chart.y_column else ""
    
    colors = chart.config.get("colors", ["#4361EE"]) if chart.config else ["#4361EE"]
    
    chart_config = {
        "id": chart.id,
        "type": chart_type_val,
        "title": chart.title,
        "description": chart.description or "",
        "datasetId": chart.dataset_id,
        "xAxis": {
            "field": chart.x_column or "",
            "label": x_label,
        } if chart.x_column else None,
        "yAxis": {
            "field": chart.y_column or "",
            "label": y_label,
        } if chart.y_column else None,
        "series": [
            {
                "field": chart.y_column or "",
                "label": y_label,
                "color": colors[0] if colors else "#4361EE",
            }
        ] if chart.y_column else [],
        "colorScheme": colors,
        "showLegend": chart.config.get("show_legend", True) if chart.config else True,
        "showGrid": chart.config.get("show_grid", True) if chart.config else True,
    }
    
    # Get rows from cached_data
    rows = []
    if chart.cached_data and "rows" in chart.cached_data:
        rows = chart.cached_data["rows"]
        
    return {
        "id": chart.id,
        "chartConfig": chart_config,
        "data": rows,
    }


def format_dashboard_response(dashboard: Dashboard) -> dict:
    """Format ORM Dashboard to match frontend expected structure."""
    # Fetch KPIs from dataset
    kpis = []
    if dashboard.dataset and dashboard.dataset.detected_kpis:
        kpis_data = dashboard.dataset.detected_kpis.get("kpis", [])
        # Add a unique ID to each KPI for the frontend key rendering
        for i, kpi in enumerate(kpis_data):
            kpi_id = f"kpi_{dashboard.id}_{i}"
            kpis.append({
                "id": kpi_id,
                "title": kpi.get("label", "Metric"),
                "value": kpi.get("value", 0),
                "format": kpi.get("format", "number"),
                "trend": kpi.get("change_direction", "neutral"),
                "trendValue": kpi.get("change_percent"),
                "datasetId": dashboard.dataset_id,
            })
            
    # Format charts
    charts = [format_chart_response(c) for c in dashboard.charts]
    
    # Layout Config
    layout_items = []
    if dashboard.layout_config and "items" in dashboard.layout_config:
        for item in dashboard.layout_config["items"]:
            layout_items.append({
                "i": item.get("i"),
                "x": item.get("x", 0),
                "y": item.get("y", 0),
                "w": item.get("w", 6),
                "h": item.get("h", 4),
            })
            
    return {
        "id": dashboard.id,
        "name": dashboard.title,
        "description": dashboard.description or "",
        "createdAt": dashboard.created_at.isoformat() if dashboard.created_at else "",
        "updatedAt": dashboard.updated_at.isoformat() if dashboard.updated_at else "",
        "createdBy": dashboard.owner_id,
        "datasetId": dashboard.dataset_id,
        "isPublic": False,
        "tags": [],
        "kpis": kpis,
        "charts": charts,
        "filters": [],  # Optional interactive filters
        "layout": layout_items,
    }


@router.get("/")
async def list_dashboards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all dashboards owned by the current user."""
    stmt = select(Dashboard).where(Dashboard.owner_id == current_user.id).order_by(Dashboard.created_at.desc())
    res = await db.execute(stmt)
    dashboards = res.scalars().all()
    
    return [format_dashboard_response(d) for d in dashboards]


@router.get("/{id}")
async def get_dashboard(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed charts, layout, and KPIs for a specific dashboard."""
    stmt = select(Dashboard).where(Dashboard.id == id, Dashboard.owner_id == current_user.id)
    res = await db.execute(stmt)
    dashboard = res.scalar_one_or_none()
    
    if not dashboard:
        raise DashboardNotFoundException()
        
    return format_dashboard_response(dashboard)


@router.put("/{id}")
async def update_dashboard(
    id: str,
    payload: DashboardUpdatePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update dashboard title, description, or custom chart layout grids."""
    stmt = select(Dashboard).where(Dashboard.id == id, Dashboard.owner_id == current_user.id)
    res = await db.execute(stmt)
    dashboard = res.scalar_one_or_none()
    
    if not dashboard:
        raise DashboardNotFoundException()
        
    if payload.title is not None:
        dashboard.title = payload.title
    if payload.description is not None:
        dashboard.description = payload.description
    if payload.layoutConfig is not None:
        # Convert frontend layout to backend layout config schema
        dashboard.layout_config = payload.layoutConfig
        
    db.add(dashboard)
    await db.commit()
    await db.refresh(dashboard)
    
    return format_dashboard_response(dashboard)


@router.delete("/{id}")
async def delete_dashboard(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a dashboard."""
    stmt = select(Dashboard).where(Dashboard.id == id, Dashboard.owner_id == current_user.id)
    res = await db.execute(stmt)
    dashboard = res.scalar_one_or_none()
    
    if not dashboard:
        raise DashboardNotFoundException()
        
    await db.delete(dashboard)
    await db.commit()
    
    return {"success": True, "message": "Dashboard deleted successfully"}
