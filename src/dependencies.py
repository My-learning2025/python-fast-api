from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth.util import AuthUtil
from .db.main import get_session  # Import your session dependency

auth_util = AuthUtil()


class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
        session=Depends(get_session),  # Add session as a dependency
    ) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        if not self.token_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
            )

        user = await auth_util.verify_token(creds.credentials, session)
        return user


class RefreshTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
        session=Depends(get_session),  # Add session as a dependency
    ) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        if not self.token_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await auth_util.verify_token(creds.credentials, session, True)
        return user
