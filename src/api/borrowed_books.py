# Python std lib
from datetime import date

# Third party
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

# Local
from ..db import get_session
from ..models import BorrowedBook, Book, Reader
from ..serializers import BorrowedBookCreate, BorrowedBookResponse
from .oauth_scheme import verify_token


####################################################################################################
# SETTINGS
####################################################################################################

router = APIRouter(
    prefix="/borrowed_books",
    tags=["BORROWED BOOKS"],
    dependencies=[Depends(verify_token)]
)

####################################################################################################
# ENDPOINTS
####################################################################################################

@router.post("/", response_model=BorrowedBookResponse, status_code=status.HTTP_201_CREATED)
async def create_borrowed_book(borrowed_book: BorrowedBookCreate, session: AsyncSession = Depends(get_session)):
    """Record a new borrowed book."""
    book_query = await session.execute(select(Book).where(Book.id == borrowed_book.book_id))
    book = book_query.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book is not found.")

    if book.quantity <= 0:
        raise HTTPException(status_code=400, detail="Book is out of stock.")

    reader_query = await session.execute(select(Reader).where(Reader.id == borrowed_book.reader_id))
    reader = reader_query.scalar_one_or_none()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader is not found.")

    borrowed_books_query = await session.execute(
        select(BorrowedBook).where(
            BorrowedBook.reader_id == borrowed_book.reader_id,
            (BorrowedBook.return_date.is_(None) | (BorrowedBook.return_date > func.current_date()))
        )
    )

    borrowed_books_count = len(borrowed_books_query.scalars().all())
    if borrowed_books_count >= 3:
        raise HTTPException(
            status_code=400,
            detail="The reader has already taken the maximum number of books (3) and has not returned them.",
        )

    book.quantity -= 1
    session.add(book)

    new_borrowed_book = BorrowedBook(**borrowed_book.model_dump())
    session.add(new_borrowed_book)
    await session.commit()
    await session.refresh(new_borrowed_book)

    return new_borrowed_book


@router.get("/{borrowed_book_id}", response_model=BorrowedBookResponse, status_code=status.HTTP_200_OK)
async def get_borrowed_book(borrowed_book_id: int, session: AsyncSession = Depends(get_session)):
    """Retrieve a borrowed book by its ID."""
    try:
        result = await session.execute(select(BorrowedBook).where(BorrowedBook.id == borrowed_book_id))
        borrowed_book = result.scalar_one()
        return borrowed_book
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowed book not found")


@router.get("/", response_model=list[BorrowedBookResponse], status_code=status.HTTP_200_OK)
async def list_borrowed_books(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    """List all borrowed books with pagination."""
    result = await session.execute(select(BorrowedBook).offset(skip).limit(limit))
    borrowed_books = result.scalars().all()
    return borrowed_books


@router.put("/{borrowed_book_id}", response_model=BorrowedBookResponse, status_code=status.HTTP_200_OK)
async def update_borrowed_book(
        borrowed_book_id: int, updated_borrowed_book: BorrowedBookCreate, session: AsyncSession = Depends(get_session)
):
    """Update a borrowed book record."""
    try:
        result = await session.execute(select(BorrowedBook).where(BorrowedBook.id == borrowed_book_id))
        borrowed_book = result.scalar_one()

        if updated_borrowed_book.return_date and (
                updated_borrowed_book.return_date <= date.today()
        ):
            book_query = await session.execute(select(Book).where(Book.id == borrowed_book.book_id))
            book = book_query.scalar_one_or_none()
            if book:
                book.quantity += 1
                session.add(book)

        for field, value in updated_borrowed_book.model_dump().items():
            setattr(borrowed_book, field, value)
        await session.commit()
        await session.refresh(borrowed_book)
        return borrowed_book

    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowed book not found")


@router.delete("/{borrowed_book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_borrowed_book(borrowed_book_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a borrowed book record by its ID."""
    try:
        result = await session.execute(select(BorrowedBook).where(BorrowedBook.id == borrowed_book_id))
        borrowed_book = result.scalar_one()
        await session.delete(borrowed_book)
        await session.commit()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowed book not found")
    return None