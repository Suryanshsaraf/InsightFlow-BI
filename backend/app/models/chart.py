"""
Chart ORM model.

Represents a single chart/visualization with its type, axis configuration,
and optional data filters. Charts belong to a dashboard and a dataset.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.dashboard import Dashboard
    from app.models.dataset import Dataset
    from app.models.user import User


class ChartType(str, PyEnum):
    """Supported chart / visualization types."""

    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    TABLE = "table"
    KPI_CARD = "kpi_card"
    DONUT = "donut"
    TREEMAP = "treemap"
    FUNNEL = "funnel"


class Chart(Base):
    """Individual chart within a dashboard."""

    __tablename__ = "charts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chart_type: Mapped[ChartType] = mapped_column(
        Enum(ChartType), nullable=False
    )

    # Axis / dimension configuration
    x_column: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    y_column: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    group_by_column: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    aggregation: Mapped[Optional[str]] = mapped_column(
        String(50), default="sum", nullable=True
    )

    # Optional SQL query backing this chart
    query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Chart-specific configuration (colors, labels, formatting)
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )

    # Cached result data for fast rendering
    cached_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )

    # Layout position within the dashboard grid
    position_x: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    position_y: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    height: Mapped[int] = mapped_column(Integer, default=4, nullable=False)

    is_auto_generated: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dashboard_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("dashboards.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────
    owner: Mapped["User"] = relationship("User", back_populates="charts")
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="charts")
    dashboard: Mapped[Optional["Dashboard"]] = relationship(
        "Dashboard", back_populates="charts"
    )

    def __repr__(self) -> str:
        return f"<Chart(id={self.id!r}, title={self.title!r}, type={self.chart_type!r})>"
