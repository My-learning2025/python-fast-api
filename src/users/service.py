from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone, timedelta
import uuid
from .models import Users
from .schemas import UserCreate, UserUpdate
from .security import get_password_hash


class UserService:
    async def get_users(self, session: AsyncSession, skip: int = 0, limit: int = 100):
        statement = (
            select(Users).offset(skip).limit(limit).order_by(desc(Users.created_at))
        )

        result = await session.exec(statement)
        return result.all()

    async def get_user(self, user_id: uuid.UUID, session: AsyncSession):
        statement = select(Users).where(Users.uid == user_id)
        result = await session.exec(statement)
        user = result.first()
        return user if user else None

    async def create_user(self, user_data: UserCreate, session: AsyncSession):
        # Check if username or email already exists
        existing_user = await session.exec(
            select(Users).where(
                (Users.username == user_data.username)
                | (Users.email == user_data.email)
            )
        )

        user = existing_user.first()

        if user:
            raise ValueError("Username or email already registered")

        # Create new user
        user_data_dict = user_data.model_dump()
        # Define UTC+7 timezone
        utc_plus_7 = timezone(timedelta(hours=7))
        user_data_dict["created_at"] = datetime.now(utc_plus_7)
        user_data_dict["updated_at"] = datetime.now(utc_plus_7)
        user_data_dict["password_hash"] = get_password_hash(user_data.password)
        new_user = Users(**user_data_dict)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def update_user(
        self, user_id: uuid.UUID, user_data: UserUpdate, session: AsyncSession
    ):
        user_to_update = await self.get_user(user_id, session)
        if not user_to_update:
            raise ValueError("User not found")

        # Check if new username or email conflicts with existing users
        if (
            user_data.username != user_to_update.username
            or user_data.email != user_to_update.email
        ):
            existing_user = await session.exec(
                select(Users).where(
                    (Users.username == user_data.username)
                    | (Users.email == user_data.email)
                )
            ).first()

            if existing_user and existing_user.uid != user_id:
                raise ValueError("Username or email already taken")

        # Update user fields
        update_data_dict = user_data.model_dump(exclude_unset=True)
        for key, value in update_data_dict.items():
            setattr(user_to_update, key, value)

        user_to_update.updated_at = datetime.now()
        session.add(user_to_update)
        await session.commit()
        await session.refresh(user_to_update)
        return user_to_update

    async def delete_user(self, user_id: uuid.UUID, session: AsyncSession):
        user_to_delete = await self.get_user(user_id, session)
        if not user_to_delete:
            raise ValueError("User not found")

        await session.delete(user_to_delete)
        await session.commit()
        return True
