"""
Authentication API router.
"""

import time
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

router = APIRouter()


class LoginPayload(BaseModel):
    email: str
    password: str


class RefreshPayload(BaseModel):
    refreshToken: str


def format_user_response(user: User) -> dict:
    """Format ORM User to match frontend expected structure."""
    return {
        "id": user.id,
        "name": user.full_name,
        "email": user.email,
        "role": "admin" if user.is_superuser else "editor",
        "createdAt": user.created_at.isoformat() if user.created_at else "",
    }


@router.post("/signup")
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and return user info and access/refresh tokens."""
    user = await AuthService.register_user(db, payload)
    
    # Auto authenticate user after signup
    _, tokens = await AuthService.authenticate_user(db, payload.email, payload.password)
    
    return {
        "user": format_user_response(user),
        "tokens": {
            "accessToken": tokens["access_token"],
            "refreshToken": tokens["refresh_token"],
            "expiresAt": int(time.time()) + (30 * 60),  # 30 mins
        },
    }


@router.post("/login")
async def login(payload: LoginPayload, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return user info + access/refresh tokens."""
    user, tokens = await AuthService.authenticate_user(db, payload.email, payload.password)
    
    return {
        "user": format_user_response(user),
        "tokens": {
            "accessToken": tokens["access_token"],
            "refreshToken": tokens["refresh_token"],
            "expiresAt": int(time.time()) + (30 * 60),
        },
    }


@router.post("/refresh")
async def refresh(payload: RefreshPayload, db: AsyncSession = Depends(get_db)):
    """Refresh JWT access token using refresh token."""
    tokens = await AuthService.refresh_tokens(db, payload.refreshToken)
    
    return {
        "accessToken": tokens["access_token"],
        "refreshToken": tokens["refresh_token"],
        "expiresAt": int(time.time()) + (30 * 60),
    }


@router.post("/logout")
async def logout():
    """Sign out endpoint (stateless blacklisting can be added in future)."""
    return {"message": "Successfully logged out"}


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    """Get currently logged-in user profile."""
    return format_user_response(current_user)
