import pytest
from httpx import AsyncClient
from datetime import datetime
from bson import ObjectId


@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient, test_db, mock_auth_user):
    await test_db.authenticated_users.insert_one(mock_auth_user)

    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "role": "Developer"
    }

    response = await async_client.post(
        "/users",
        json=user_data,
        headers={"Authorization": f"Bearer {mock_auth_user['email']}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_users_pagination(async_client: AsyncClient, test_db, mock_auth_user):
    await test_db.authenticated_users.insert_one(mock_auth_user)

    for i in range(15):
        await test_db.users.insert_one({
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "role": "User",
            "created_at": datetime.utcnow()
        })

    response = await async_client.get(
        "/users?page=1&page_size=10",
        headers={"Authorization": f"Bearer {mock_auth_user['email']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["users"]) == 10
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 2


@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient, test_db, mock_auth_user):
    await test_db.authenticated_users.insert_one(mock_auth_user)

    user_doc = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "role": "Manager",
        "created_at": datetime.utcnow()
    }
    result = await test_db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    response = await async_client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_auth_user['email']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == user_doc["name"]
    assert data["email"] == user_doc["email"]


@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient, test_db, mock_auth_user):
    await test_db.authenticated_users.insert_one(mock_auth_user)

    user_doc = {
        "name": "Old Name",
        "email": "old@example.com",
        "role": "User",
        "created_at": datetime.utcnow()
    }
    result = await test_db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    update_data = {
        "name": "New Name",
        "role": "Admin"
    }

    response = await async_client.put(
        f"/users/{user_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {mock_auth_user['email']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["role"] == "Admin"
    assert data["email"] == "old@example.com"


@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient, test_db, mock_auth_user):
    await test_db.authenticated_users.insert_one(mock_auth_user)

    user_doc = {
        "name": "To Delete",
        "email": "delete@example.com",
        "role": "User",
        "created_at": datetime.utcnow()
    }
    result = await test_db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    response = await async_client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_auth_user['email']}"}
    )

    assert response.status_code == 204

    deleted_user = await test_db.users.find_one({"_id": ObjectId(user_id)})
    assert deleted_user is None


@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client: AsyncClient, test_db, mock_auth_user):
    await test_db.authenticated_users.insert_one(mock_auth_user)

    user_doc = {
        "name": "Existing User",
        "email": "existing@example.com",
        "role": "User",
        "created_at": datetime.utcnow()
    }
    await test_db.users.insert_one(user_doc)

    duplicate_user = {
        "name": "Duplicate User",
        "email": "existing@example.com",
        "role": "Admin"
    }

    response = await async_client.post(
        "/users",
        json=duplicate_user,
        headers={"Authorization": f"Bearer {mock_auth_user['email']}"}
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    response = await async_client.get("/users")

    assert response.status_code == 401
