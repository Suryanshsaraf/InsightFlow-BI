"""
Insight ORM model.

Stores AI-generated insights and anomalies detected from dataset analysis.
Each insight is tied to a dataset and the user who triggered the analysis.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.user import User


class InsightType(str, PyEnum):
    """Category of AI-generated insight."""

    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    SUMMARY = "summary"
    RECOMMENDATION = "recommendation"
    FORECAST = "forecast"


class Insight(Base):
    """AI-generated insight derived from dataset analysis."""

    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    insight_type: Mapped[InsightType] = mapped_column(
        Enum(InsightType), nullable=False
    )

    # Confidence score (0.0 – 1.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Supporting data/evidence for the insight
    supporting_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )

    # Which columns were analysed
    related_columns: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )

    # Optional suggested chart for this insight
    suggested_chart_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    is_auto_generated: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="insights")
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="insights")

    def __repr__(self) -> str:
        return f"<Insight(id={self.id!r}, type={self.insight_type!r})>"
