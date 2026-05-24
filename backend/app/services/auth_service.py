"""
Authentication service.
"""

from typing import Dict, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException, ValidationException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """Handles authentication and token operations."""
    
    @staticmethod
    async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
        """
        Register a new user in the system.
        
        Raises:
            ValidationException: If email already exists.
        """
        # Check if user already exists
        stmt = select(User).where(User.email == user_in.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValidationException(
                message="A user with this email address already exists.",
                details={"email": user_in.email},
            )
            
        hashed_pwd = hash_password(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_pwd,
            full_name=user_in.full_name,
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
        
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> Tuple[User, Dict[str, str]]:
        """
        Authenticate a user by email and password, and return user + tokens.
        
        Raises:
            AuthenticationException: If credentials are invalid.
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationException("Invalid email or password.")
            
        if not user.is_active:
            raise AuthenticationException("User account is inactive.")
            
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        return user, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
        
    @staticmethod
    async def refresh_tokens(
        db: AsyncSession, refresh_token_str: str
    ) -> Dict[str, str]:
        """
        Generate new access and refresh tokens using a valid refresh token.
        
        Raises:
            AuthenticationException: If refresh token is invalid or expired.
        """
        try:
            payload = decode_token(refresh_token_str)
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "refresh":
                raise AuthenticationException("Invalid refresh token.")
        except Exception:
            raise AuthenticationException("Invalid refresh token or token expired.")
            
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive.")
            
        new_access = create_access_token(user.id)
        new_refresh = create_refresh_token(user.id)
        
        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }
