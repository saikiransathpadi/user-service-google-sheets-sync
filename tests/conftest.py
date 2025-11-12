import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from main import app
from app.config import settings
from app.database import connect_to_mongo


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    test_client = AsyncIOMotorClient(settings.mongodb_uri)
    test_database = test_client.get_default_database()
    await connect_to_mongo()

    yield test_database

    await test_database.users.delete_many({})
    await test_database.authenticated_users.delete_many({})


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_user():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "role": "Admin"
    }


@pytest.fixture
def mock_auth_user():
    return {
        "email": "authenticated@example.com",
        "name": "Authenticated User",
        "profile_pic": "https://example.com/pic.jpg",
        "access_token": "mock_token",
        "refresh_token": "mock_refresh_token"
    }
