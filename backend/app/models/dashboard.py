"""
Dashboard ORM model.

A dashboard groups multiple charts together and is tied to a dataset.
Stores layout configuration as a JSON blob for flexible front-end rendering.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.chart import Chart
    from app.models.dataset import Dataset
    from app.models.user import User


class Dashboard(Base):
    """User-created dashboard that aggregates charts over a dataset."""

    __tablename__ = "dashboards"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    layout_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )
    is_auto_generated: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
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
    owner: Mapped["User"] = relationship("User", back_populates="dashboards")
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="dashboards")
    charts: Mapped[List["Chart"]] = relationship(
        "Chart", back_populates="dashboard", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Dashboard(id={self.id!r}, title={self.title!r})>"
