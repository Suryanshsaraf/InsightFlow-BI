"""
Insights API router.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.dashboard import Dashboard
from app.models.dataset import Dataset
from app.models.insight import Insight, InsightType
from app.models.user import User
from app.services.ai_insights import AIInsightService
from app.core.exceptions import NotFoundException

router = APIRouter()


class GenerateInsightsPayload(BaseModel):
    dashboardId: str


def format_insight_response(insight: Insight, dashboard_id: str) -> dict:
    """Format ORM Insight to match frontend expected structure."""
    # Map type
    in_type = insight.insight_type.value
    if in_type not in ["anomaly", "trend", "correlation", "forecast", "recommendation", "summary"]:
        in_type = "summary"
        
    # Map severity based on type and confidence
    severity = "info"
    if in_type == "anomaly":
        severity = "critical" if insight.confidence > 0.8 else "warning"
    elif in_type == "trend" and insight.confidence > 0.85:
        severity = "positive"
    elif in_type == "recommendation":
        severity = "info"
        
    return {
        "id": insight.id,
        "dashboardId": dashboard_id,
        "type": in_type,
        "title": insight.title,
        "description": insight.description,
        "severity": severity,
        "confidence": insight.confidence,
        "createdAt": insight.created_at.isoformat() if insight.created_at else "",
    }


@router.post("/generate")
async def generate_dashboard_insights(
    payload: GenerateInsightsPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-driven insights for a dashboard's dataset.
    Deletes old insights and stores newly generated ones.
    """
    # 1. Fetch Dashboard
    stmt = select(Dashboard).where(Dashboard.id == payload.dashboardId, Dashboard.owner_id == current_user.id)
    res = await db.execute(stmt)
    dashboard = res.scalar_one_or_none()
    
    if not dashboard:
        raise NotFoundException("Dashboard not found")
        
    # 2. Fetch associated Dataset
    dataset_stmt = select(Dataset).where(Dataset.id == dashboard.dataset_id)
    dataset_res = await db.execute(dataset_stmt)
    dataset = dataset_res.scalar_one_or_none()
    
    if not dataset:
        raise NotFoundException("Dataset not found")
        
    # 3. Call AIInsightService to generate insights
    ai_data = await AIInsightService.generate_insights(dataset)
    
    # 4. Clean up any existing auto-generated insights for this dataset
    cleanup_stmt = select(Insight).where(Insight.dataset_id == dataset.id, Insight.is_auto_generated == True)
    cleanup_res = await db.execute(cleanup_stmt)
    for existing in cleanup_res.scalars().all():
        await db.delete(existing)
    await db.commit()
    
    # 5. Insert new insights
    parsed_insights = ai_data.get("insights", [])
    inserted_insights = []
    
    for in_data in parsed_insights:
        # Resolve insight type safely
        raw_type = in_data.get("type", "summary").lower()
        try:
            insight_type = InsightType(raw_type)
        except ValueError:
            # Map type variants to standard types
            if raw_type == "recommendation":
                insight_type = InsightType.RECOMMENDATION
            elif raw_type == "anomaly":
                insight_type = InsightType.ANOMALY
            elif raw_type == "correlation":
                insight_type = InsightType.CORRELATION
            elif raw_type == "trend":
                insight_type = InsightType.TREND
            else:
                insight_type = InsightType.SUMMARY
                
        insight = Insight(
            title=in_data.get("title", "Insight"),
            description=in_data.get("description", ""),
            insight_type=insight_type,
            confidence=float(in_data.get("confidence", in_data.get("confidence_score", 0.8))),
            related_columns=in_data.get("related_columns", []),
            is_auto_generated=True,
            user_id=current_user.id,
            dataset_id=dataset.id,
        )
        
        db.add(insight)
        inserted_insights.append(insight)
        
    await db.commit()
    
    # Format and return responses
    return [format_insight_response(ins, dashboard.id) for ins in inserted_insights]


@router.get("/dashboard/{dashboard_id}")
async def get_dashboard_insights(
    dashboard_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve existing insights associated with a dashboard's dataset."""
    # 1. Fetch Dashboard to get dataset_id
    stmt = select(Dashboard).where(Dashboard.id == dashboard_id, Dashboard.owner_id == current_user.id)
    res = await db.execute(stmt)
    dashboard = res.scalar_one_or_none()
    
    if not dashboard:
        raise NotFoundException("Dashboard not found")
        
    # 2. Fetch insights matching dataset_id
    insight_stmt = select(Insight).where(Insight.dataset_id == dashboard.dataset_id).order_by(Insight.created_at.desc())
    insight_res = await db.execute(insight_stmt)
    insights = insight_res.scalars().all()
    
    # If no insights generated yet, generate them dynamically in the background or return mock ones
    if not insights:
        # Fallback to auto-generation
        payload = GenerateInsightsPayload(dashboardId=dashboard_id)
        return await generate_dashboard_insights(payload, current_user, db)
        
    return [format_insight_response(ins, dashboard_id) for ins in insights]
