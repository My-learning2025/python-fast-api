from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from .schema import LoginRequest, TokenResponse, UserProfile
from .service import AuthService
from sqlmodel.ext.asyncio.session import AsyncSession
from ..db.main import get_session
from ..dependencies import AccessTokenBearer


auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
access_token_bearer = AccessTokenBearer()


@auth_router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    return await AuthService.login(request, session)


@auth_router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    return await AuthService.refresh_token(refresh_token)


@auth_router.get(
    "/profile", response_model=UserProfile, dependencies=[Depends(access_token_bearer)]
)
async def get_profile_from_header(
    user_details: UserProfile = Depends(access_token_bearer),
):
    return user_details
