from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = "password"


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    isVerified: Optional[bool] = None


class UserResponse(UserBase):
    uid: uuid.UUID
    isVerified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
