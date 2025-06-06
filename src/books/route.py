from http.client import HTTPException
from fastapi import APIRouter, Depends, status
from src.books.schema import BookCreateModel, BookResponse, BookUpdateModel
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session


book_router = APIRouter()
book_service = BookService()


@book_router.post("", status_code=status.HTTP_201_CREATED, response_model=BookResponse)
async def createBook(
    bookCreateModel: BookCreateModel, session: AsyncSession = Depends(get_session)
):
    bookCreateData = await book_service.createBook(
        bookCreateModel,
        session,
    )
    if bookCreateData:
        return bookCreateData
    else:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create book",
        )


@book_router.patch("/{book_id}", response_model=BookResponse)
async def updateBook(
    book_id: str,
    book_update: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
):
    bookUpdateData = await book_service.updateBook(book_id, book_update, session)
    if bookUpdateData:
        return bookUpdateData
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found",
    )


@book_router.get("", response_model=List[BookResponse])
async def get_books(
    session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100
):
    return await book_service.getBooks(session, skip, limit)


@book_router.get("/{book_uid}", response_model=BookResponse)
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    bookData = await book_service.getBook(book_uid, session)
    if bookData:
        return bookData
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found",
    )


@book_router.delete("/{book_uid}")
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    deleteResult = await book_service.deleteBook(book_uid, session)
    if deleteResult:
        return {"message": deleteResult}
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found",
    )
