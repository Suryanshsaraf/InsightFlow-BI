"""
QueryHistory ORM model.

Logs every natural-language query, the generated SQL, execution result,
and performance metrics for auditability and caching.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.user import User


class QueryStatus(str, PyEnum):
    """Execution status of a query."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class QueryHistory(Base):
    """Audit log for NL-to-SQL queries executed by users."""

    __tablename__ = "query_histories"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )

    # Natural-language input from the user
    natural_language_query: Mapped[str] = mapped_column(Text, nullable=False)

    # Generated SQL (may be None if generation failed)
    generated_sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Execution details
    status: Mapped[QueryStatus] = mapped_column(
        Enum(QueryStatus), default=QueryStatus.PENDING, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Result metadata
    result_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        SQLiteJSON, nullable=True
    )
    result_row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

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
    user: Mapped["User"] = relationship("User", back_populates="query_histories")
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="query_histories")

    def __repr__(self) -> str:
        return f"<QueryHistory(id={self.id!r}, status={self.status!r})>"
