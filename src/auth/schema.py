import uuid
from pydantic import BaseModel, EmailStr
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserProfile(BaseModel):
    uid: uuid.UUID
    username: str
    email: EmailStr
    isVerified: bool = False
    created_at: datetime
    updated_at: datetime
    # is_active: bool = True

    class Config:
        from_attributes = True


class Payload(BaseModel):
    uid: str
    username: str
    email: str
    exp: datetime
