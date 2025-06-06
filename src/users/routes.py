from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession

from .service import UserService
from .schemas import UserCreate, UserUpdate, UserResponse
from ..db.main import get_session
from ..dependencies import AccessTokenBearer

user_router = APIRouter()
user_service = UserService()
access_token_bearer = AccessTokenBearer()


# Create user
@user_router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await user_service.create_user(user, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Get all users
@user_router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    token: str = Depends(access_token_bearer),
):
    return await user_service.get_users(session, skip, limit)


# Get user by ID
@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# Update user
@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await user_service.update_user(user_id, user_update, session)
    except ValueError as e:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
                if "not found" in str(e)
                else status.HTTP_400_BAD_REQUEST
            ),
            detail=str(e),
        )


# Delete user
@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(access_token_bearer),
):
    try:
        await user_service.delete_user(user_id, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return None
