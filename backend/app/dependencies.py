"""
FastAPI dependencies for dependency injection in route parameters.
"""

from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException, PermissionDeniedException
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

# Standard OAuth2 scheme for extracting Bearer tokens from request headers
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,  # We handle error formatting ourselves in dependency
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Validate the Bearer token and retrieve the current authenticated user.
    
    Raises:
        AuthenticationException: If token is invalid, expired, or user not found.
    """
    if not token:
        raise AuthenticationException("Not authenticated. Missing token.")
        
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if not user_id or token_type != "access":
            raise AuthenticationException("Invalid access token structure.")
            
    except JWTError:
        raise AuthenticationException("Could not validate credentials or token expired.")
        
    # Query database to check if user still exists and is active
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise AuthenticationException("Authenticated user not found.")
        
    if not user.is_active:
        raise PermissionDeniedException("Inactive user account.")
        
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Validate that the current user is a superuser."""
    if not current_user.is_superuser:
        raise PermissionDeniedException("Not enough privileges.")
    return current_user
