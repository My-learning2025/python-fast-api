from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.route import BookCreateModel
from src.books.schema import BookUpdateModel
from .models import Books


class BookService:

    async def getBooks(self, session: AsyncSession, skip: int = 0, limit: int = 100):
        statement = (
            select(Books).offset(skip).limit(limit).order_by(desc(Books.created_at))
        )
        result = await session.exec(statement)
        return result.all()

    async def getBook(self, book_uid: str, session: AsyncSession):
        statement = select(Books).where(Books.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()

        return book if book else None

    async def createBook(self, book_data: BookCreateModel, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        new_book = Books(**book_data_dict)
        session.add(new_book)
        await session.commit()
        return new_book

    async def updateBook(
        self, book_uid: str, book_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.getBook(book_uid, session)
        if book_to_update:
            update_data_dict = book_data.model_dump()

            for key, value in update_data_dict.items():
                setattr(book_to_update, key, value)

            await session.commit()

            return book_to_update
        return "Book not found"

    async def deleteBook(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.getBook(book_uid, session)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return "Book deleted successfully"
        return "Book not found"
