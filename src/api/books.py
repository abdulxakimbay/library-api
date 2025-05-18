# Third party
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

# Local
from ..db import get_session
from ..models import Book
from ..serializers import BookCreate, BookResponse
from .oauth_scheme import verify_token


####################################################################################################
# SETTINGS
####################################################################################################

router = APIRouter(
    prefix="/books",
    tags=["BOOKS"],
    dependencies=[Depends(verify_token)]
)

####################################################################################################
# ENDPOINTS
####################################################################################################

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, session: AsyncSession = Depends(get_session)):
    """Create a new book."""
    new_book = Book(**book.model_dump())
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)
    return new_book


@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    """Retrieve a book by its ID."""
    try:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one()
        return book
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.get("/", response_model=list[BookResponse], status_code=status.HTTP_200_OK)
async def list_books(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    """List all books with pagination."""
    result = await session.execute(select(Book).offset(skip).limit(limit))
    books = result.scalars().all()
    return books


@router.put("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def update_book(book_id: int, updated_book: BookCreate, session: AsyncSession = Depends(get_session)):
    """Update an existing book."""
    try:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one()
        for field, value in updated_book.model_dump().items():
            setattr(book, field, value)
        await session.commit()
        await session.refresh(book)
        return book
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a book by its ID."""
    try:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one()
        await session.delete(book)
        await session.commit()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None