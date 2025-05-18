# Python std lib
from datetime import date

# Third party
from pydantic import BaseModel, EmailStr, Field, ConfigDict

####################################################################################################
# TOKEN-SCHEMAS
####################################################################################################

class RefreshToken(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str


class Tokens(BaseModel):
    refresh_token: str
    access_token: str


class TokenData(BaseModel):
    sub: str


####################################################################################################
# LIBRARIAN SCHEMAS
####################################################################################################

class LibrarianBase(BaseModel):
    email: EmailStr


class LibrarianCreate(LibrarianBase):
    password: str = Field(..., min_length=6, max_length=255)


class LibrarianResponse(LibrarianBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LibrarianLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=255)

####################################################################################################
# READER SCHEMAS
####################################################################################################

class ReaderBase(BaseModel):
    full_name: str = Field(..., max_length=255)
    email: EmailStr


class ReaderCreate(ReaderBase):
    pass


class ReaderResponse(ReaderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

####################################################################################################
# BOOK SCHEMAS
####################################################################################################

class BookBase(BaseModel):
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    published_year: int | None = None
    isbn: str | None = Field(None, max_length=255)
    quantity: int = Field(..., ge=0)


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

####################################################################################################
# BORROWED BOOK SCHEMAS
####################################################################################################

class BorrowedBookBase(BaseModel):
    reader_id: int
    book_id: int
    borrowed_date: date
    return_date: date | None = None


class BorrowedBookCreate(BorrowedBookBase):
    pass


class BorrowedBookResponse(BorrowedBookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)