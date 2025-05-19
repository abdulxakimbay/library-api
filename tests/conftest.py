# Third party
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

# Local
from src.db import Base, get_session
from src.config import settings
from src.api.main import app
from src.api.auth import create_access_token
from .factories import LibrarianFactory

####################################################################################################
# SETTINGS
####################################################################################################

engine_test = create_async_engine(settings.get_test_db_url, echo=False)
async_session_test = async_sessionmaker(engine_test, expire_on_commit=False)

####################################################################################################
# FIXTURES
####################################################################################################

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def get_test_session():
    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(get_test_session):
    async def override_get_session():
        yield get_test_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        librarian = LibrarianFactory.build()
        get_test_session.add(librarian)
        await get_test_session.commit()
        await get_test_session.refresh(librarian)

        access_token: str = create_access_token(data={"sub": str(librarian.id)})
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        yield client