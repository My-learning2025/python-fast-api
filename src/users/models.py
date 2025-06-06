import uuid
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime


class Users(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4()
        )
    )
    username: str = Field(max_length=8, unique=True, nullable=False)
    password_hash: str = Field(max_length=8, nullable=False, exclude=True, default="")
    email: str = Field(max_length=40, unique=True, nullable=False)
    isVerified: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))


def __repr__(self):
    return f"<User {self.username}>"
