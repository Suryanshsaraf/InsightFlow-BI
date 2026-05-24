"""
User ORM model.

Stores authentication credentials and profile data.
Passwords are hashed via passlib before storage.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.chart import Chart
    from app.models.dashboard import Dashboard
    from app.models.dataset import Dataset
    from app.models.insight import Insight
    from app.models.query_history import QueryHistory


class User(Base):
    """Application user with hashed password and profile metadata."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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
    datasets: Mapped[List["Dataset"]] = relationship(
        "Dataset", back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )
    dashboards: Mapped[List["Dashboard"]] = relationship(
        "Dashboard", back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )
    charts: Mapped[List["Chart"]] = relationship(
        "Chart", back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )
    query_histories: Mapped[List["QueryHistory"]] = relationship(
        "QueryHistory", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    insights: Mapped[List["Insight"]] = relationship(
        "Insight", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, email={self.email!r})>"
