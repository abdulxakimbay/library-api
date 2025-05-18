# Python std lib
from typing import Any, AsyncGenerator

# Third party
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Local
from .config import settings

####################################################################################################
# SETTINGS
####################################################################################################

engine = create_async_engine(settings.get_db_url, echo=False)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

####################################################################################################
# FUNCTIONS
####################################################################################################

async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with SessionFactory() as session:
        yield session
