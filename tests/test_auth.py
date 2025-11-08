import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_endpoint(async_client: AsyncClient):
    response = await async_client.get("/auth/login")

    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "accounts.google.com" in data["authorization_url"]


@pytest.mark.asyncio
async def test_get_current_user_info(async_client: AsyncClient, test_db, mock_auth_user):
    await test_db.authenticated_users.insert_one(mock_auth_user)

    response = await async_client.get(
        f"/auth/me?email={mock_auth_user['email']}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == mock_auth_user["email"]
    assert data["name"] == mock_auth_user["name"]


@pytest.mark.asyncio
async def test_get_nonexistent_user_info(async_client: AsyncClient):
    response = await async_client.get(
        "/auth/me?email=nonexistent@example.com"
    )

    assert response.status_code == 404
