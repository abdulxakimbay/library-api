# Python std lib
from datetime import date

# Third party
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Local
from src.models import Book, Reader, BorrowedBook
from .factories import ReaderFactory, BookFactory


####################################################################################################
# TESTS
####################################################################################################


@pytest.mark.asyncio
async def test_create_borrowed_book_failure_out_of_stock(
    async_client: AsyncClient, get_test_session: AsyncSession
):
    book: Book = BookFactory.build(quantity=0)
    get_test_session.add(book)

    reader: Reader = ReaderFactory.build()
    get_test_session.add(reader)

    await get_test_session.commit()
    await get_test_session.refresh(book)
    await get_test_session.refresh(reader)

    borrowed_book_data = {
        "book_id": book.id,
        "reader_id": reader.id,
        "borrowed_date": "2025-05-25",
    }

    response = await async_client.post("/borrowed_books/", json=borrowed_book_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Book is out of stock."


@pytest.mark.asyncio
async def test_create_borrowed_book_failure_borrowed_books_limit(
    async_client: AsyncClient, get_test_session: AsyncSession
):
    book: Book = BookFactory.build(quantity=5)
    get_test_session.add(book)

    reader: Reader = ReaderFactory.build()
    get_test_session.add(reader)

    await get_test_session.commit()
    await get_test_session.refresh(book)
    await get_test_session.refresh(reader)

    for i in range(3):
        borrowed_book = BorrowedBook(
            book_id=book.id,
            reader_id=reader.id,
            borrowed_date=date(2025, 5, 25),
            return_date=None
        )
        get_test_session.add(borrowed_book)

    await get_test_session.commit()

    new_borrowed_book_data = {
        "book_id": book.id,
        "reader_id": reader.id,
        "borrowed_date": "2025-05-25",
    }

    response = await async_client.post("/borrowed_books/", json=new_borrowed_book_data)

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "The reader has already taken the maximum number of books (3) and has not returned them."
    )



