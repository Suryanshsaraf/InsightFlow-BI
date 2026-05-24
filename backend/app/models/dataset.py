"""
Dataset ORM model.

Represents an uploaded CSV/Excel file and its metadata.
Tracks processing status, column schema, and row counts.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.chart import Chart
    from app.models.dashboard import Dashboard
    from app.models.insight import Insight
    from app.models.query_history import QueryHistory
    from app.models.user import User


class DatasetStatus(str, PyEnum):
    """Processing status lifecycle for a dataset."""

    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Dataset(Base):
    """Uploaded dataset with schema metadata and processing state."""

    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="text/csv", nullable=False)

    # Processing state
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus), default=DatasetStatus.PENDING, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Schema & stats (stored as JSON)
    table_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    column_schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    column_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sample_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )
    statistics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )
    detected_kpis: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
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
    owner: Mapped["User"] = relationship("User", back_populates="datasets")
    dashboards: Mapped[List["Dashboard"]] = relationship(
        "Dashboard", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin"
    )
    charts: Mapped[List["Chart"]] = relationship(
        "Chart", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin"
    )
    query_histories: Mapped[List["QueryHistory"]] = relationship(
        "QueryHistory", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin"
    )
    insights: Mapped[List["Insight"]] = relationship(
        "Insight", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id!r}, name={self.name!r}, status={self.status!r})>"
