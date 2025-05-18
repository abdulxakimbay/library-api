# Python std lib
import datetime
from typing import Annotated

# Third party
from sqlalchemy import String, CheckConstraint, Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Local
from .db import Base

####################################################################################################
# SETTINGS
####################################################################################################

intpk = Annotated[int, mapped_column(primary_key=True)]

####################################################################################################
# MODELS
####################################################################################################

class Librarian(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)


class Reader(Base):
    __tablename__ = "readers"

    id: Mapped[intpk]
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    borrowed_books: Mapped[list["BorrowedBook"]] = relationship(back_populates="reader")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[intpk]
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    published_year: Mapped[int] = mapped_column(nullable=True)
    isbn: Mapped[str] = mapped_column(String(255), unique=True, nullable=True, index=True)
    quantity: Mapped[int] = mapped_column(CheckConstraint("quantity >= 0"), nullable=False, default=1)

    borrowed_books: Mapped[list["BorrowedBook"]] = relationship(back_populates="book")


class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id: Mapped[intpk]
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=False, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False, index=True)
    borrowed_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    return_date: Mapped[datetime.date] = mapped_column(Date, nullable=True, server_default=None)

    reader: Mapped["Reader"] = relationship("Reader", back_populates="borrowed_books")
    book: Mapped["Book"] = relationship("Book", back_populates="borrowed_books")
