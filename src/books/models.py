from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg


class Books(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4()
        )
    )
    title: str
    author: str
    year: int
    description: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))


def __repr__(self):
    return f"<Book {self.title}>"
