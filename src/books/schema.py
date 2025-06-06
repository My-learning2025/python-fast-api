import uuid
from pydantic import BaseModel
from datetime import datetime


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    year: int
    description: str
    created_at: datetime
    updated_at: datetime


class BookCreateModel(BaseModel):
    title: str = "Python"
    author: str = "John Doe"
    year: int = 2023
    description: str = "A book about Python"


class BookResponse(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    year: int
    description: str
    created_at: datetime
    updated_at: datetime


class BookUpdateModel(BaseModel):
    title: str
    author: str
    year: int
    description: str
