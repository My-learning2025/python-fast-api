from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from src.util.response import BaseResponse
from .schema import LoginRequest, TokenResponse
from src.config import Config
from .util import AuthUtil


class AuthConfig:
    SECRET_KEY = Config.SECRET_KEY
    SECRET_KEY_EXPIRED = Config.ACCESS_TOKEN_EXPIRE_MINUTES
    ALGORITHM = Config.ALGORITHM
    REFRESH_SECRET = Config.REFRESH_SECRET_KEY
    REFRESH_SECRET_EXPIRED = Config.REFRESH_TOKEN_EXPIRE_DAYS


# Create a singleton instance for dependency injection
authConfig = AuthConfig()
authUtil = AuthUtil()


class AuthService:
    # Mock database - replace with real database in production
    @classmethod
    async def login(
        cls, request: LoginRequest, sessions: AsyncSession
    ) -> TokenResponse:
        user = await authUtil.get_user(request.username, sessions)

        if not user or not authUtil.verify_password(
            request.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authUtil.generate_token(user)
        return TokenResponse(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
        )

    async def refresh_token(
        cls, refresh_token: str, sessions: AsyncSession
    ) -> TokenResponse:

        payload = authUtil.verify_token(refresh_token, is_refresh_token=True)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        if not username or username not in cls._users_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = authUtil.create_access_token(data={"sub": username})
        new_refresh_token = authUtil.create_refresh_token(data={"sub": username})

        data: TokenResponse = TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

        return BaseResponse(
            code=200,
            message="Token refreshed successfully",
            data=data,
        )
