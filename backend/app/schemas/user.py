"""
Pydantic v2 schemas for User request/response payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ── Request schemas ──────────────────────────────────────────────


class UserCreate(BaseModel):
    """Payload for registering a new user."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserUpdate(BaseModel):
    """Payload for updating user profile."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserChangePassword(BaseModel):
    """Payload for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ── Response schemas ─────────────────────────────────────────────


class UserResponse(BaseModel):
    """Public user representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserBrief(BaseModel):
    """Minimal user info for embedding in other responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
