from datetime import datetime, timedelta
import logging
from typing import Optional
from fastapi import HTTPException, status
import jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

from ..users.models import Users
from src.config import Config
from .schema import TokenResponse


class AuthConfig:
    """Centralized authentication configuration"""

    SECRET_KEY = Config.SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
    ALGORITHM = Config.ALGORITHM
    REFRESH_SECRET = Config.REFRESH_SECRET_KEY
    REFRESH_TOKEN_EXPIRE_DAYS = Config.REFRESH_TOKEN_EXPIRE_DAYS


class AuthUtil:
    """Authentication utility class with optimized methods"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)

    def generate_token(self, user: Users) -> TokenResponse:
        """Generate access and refresh tokens for a user"""
        now = datetime.utcnow()  # Use UTC for consistency

        # Base payload
        base_payload = {
            "uid": str(user.uid),
            "username": user.username,
            "email": user.email,
        }

        # Access token payload
        access_payload = {
            **base_payload,
            "exp": now + timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }

        # Refresh token payload
        refresh_payload = {
            **base_payload,
            "exp": now + timedelta(days=AuthConfig.REFRESH_TOKEN_EXPIRE_DAYS),
            "type": "refresh",
        }

        access_token = self._create_token(access_payload, AuthConfig.SECRET_KEY)
        refresh_token = self._create_token(refresh_payload, AuthConfig.REFRESH_SECRET)

        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    def _create_token(self, payload: dict, secret_key: str) -> str:
        """Internal method to create JWT tokens"""
        return jwt.encode(payload, secret_key, algorithm=AuthConfig.ALGORITHM)

    async def verify_token(
        self, token: str, session: AsyncSession, is_refresh_token: bool = False
    ) -> Users:
        secret_key = (
            AuthConfig.REFRESH_SECRET if is_refresh_token else AuthConfig.SECRET_KEY
        )
        expected_type = "refresh" if is_refresh_token else "access"

        try:
            payload = jwt.decode(token, secret_key, algorithms=[AuthConfig.ALGORITHM])

            # Validate token type
            if payload.get("type") != expected_type:
                raise self.credentials_exception

            username = payload.get("username")
            if not username:
                raise self.credentials_exception

        except jwt.ExpiredSignatureError:
            logging.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            logging.warning(f"Invalid token: {e}")
            raise self.credentials_exception
        except Exception as e:
            logging.error(f"Unexpected error during token verification: {e}")
            raise self.credentials_exception

        # Get user from database
        user = await self.get_user(username, session)
        if not user:
            logging.warning(f"User not found: {username}")
            raise self.credentials_exception

        return user

    async def get_user(self, username: str, session: AsyncSession) -> Optional[Users]:
        """Retrieve user by username from database"""
        try:
            result = await session.exec(select(Users).where(Users.username == username))
            return result.first()
        except Exception as e:
            logging.error(f"Database error while fetching user {username}: {e}")
            return None

    async def refresh_access_token(
        self, refresh_token: str, session: AsyncSession
    ) -> TokenResponse:
        """Generate new access token using refresh token"""
        user = await self.verify_token(refresh_token, session, is_refresh_token=True)

        # Generate new access token (keep existing refresh token)
        now = datetime.utcnow()
        access_payload = {
            "uid": str(user.uid),
            "username": user.username,
            "email": user.email,
            "exp": now + timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }

        new_access_token = self._create_token(access_payload, AuthConfig.SECRET_KEY)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,  # Return the same refresh token
            token_type="bearer",
        )


# Create a singleton instance for dependency injection
auth_util = AuthUtil()
