# Third party
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

# Local
from ..db import get_session
from ..models import Reader
from ..serializers import ReaderCreate, ReaderResponse
from .oauth_scheme import verify_token


####################################################################################################
# SETTINGS
####################################################################################################

router = APIRouter(
    prefix="/readers",
    tags=["READERS"],
    dependencies=[Depends(verify_token)]
)

####################################################################################################
# ENDPOINTS
####################################################################################################

@router.post("/", response_model=ReaderResponse, status_code=status.HTTP_201_CREATED)
async def create_reader(reader: ReaderCreate, session: AsyncSession = Depends(get_session)):
    """Create a new reader."""
    new_reader = Reader(**reader.model_dump())
    session.add(new_reader)
    await session.commit()
    await session.refresh(new_reader)
    return new_reader


@router.get("/{reader_id}", response_model=ReaderResponse, status_code=status.HTTP_200_OK)
async def get_reader(reader_id: int, session: AsyncSession = Depends(get_session)):
    """Retrieve a reader by ID."""
    try:
        result = await session.execute(select(Reader).where(Reader.id == reader_id))
        reader = result.scalar_one()
        return reader
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")


@router.get("/", response_model=list[ReaderResponse], status_code=status.HTTP_200_OK)
async def list_readers(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    """List all readers with pagination."""
    result = await session.execute(select(Reader).offset(skip).limit(limit))
    readers = result.scalars().all()
    return readers


@router.put("/{reader_id}", response_model=ReaderResponse, status_code=status.HTTP_200_OK)
async def update_reader(reader_id: int, updated_reader: ReaderCreate, session: AsyncSession = Depends(get_session)):
    """Update an existing reader."""
    try:
        result = await session.execute(select(Reader).where(Reader.id == reader_id))
        reader = result.scalar_one()
        for field, value in updated_reader.model_dump().items():
            setattr(reader, field, value)
        await session.commit()
        await session.refresh(reader)
        return reader
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")


@router.delete("/{reader_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reader(reader_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a reader by ID."""
    try:
        result = await session.execute(select(Reader).where(Reader.id == reader_id))
        reader = result.scalar_one()
        await session.delete(reader)
        await session.commit()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")
    return None