from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import UserCreate, UserUpdate, UserResponse, PaginatedUsers
from app.database import get_database
from app.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedUsers)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    db = get_database()

    skip = (page - 1) * page_size

    total = await db.users.count_documents({})

    cursor = db.users.find({}).skip(skip).limit(page_size).sort("created_at", -1)
    users = await cursor.to_list(length=page_size)

    users_response = []
    for user in users:
        users_response.append(UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            role=user["role"],
            created_at=user["created_at"]
        ))

    total_pages = (total + page_size - 1) // page_size

    return PaginatedUsers(
        users=users_response,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"]
    )


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()

    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user_data = {
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": datetime.utcnow()
    }

    result = await db.users.insert_one(user_data)

    created_user = await db.users.find_one({"_id": result.inserted_id})

    return UserResponse(
        id=str(created_user["_id"]),
        name=created_user["name"],
        email=created_user["email"],
        role=created_user["role"],
        created_at=created_user["created_at"]
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db = get_database()

    existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = {k: v for k, v in user_update.model_dump(exclude_unset=True).items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "email" in update_data:
        email_exists = await db.users.find_one({
            "email": update_data["email"],
            "_id": {"$ne": ObjectId(user_id)}
        })
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already in use by another user")

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})

    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        email=updated_user["email"],
        role=updated_user["role"],
        created_at=updated_user["created_at"]
    )


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db = get_database()

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.delete_one({"_id": ObjectId(user_id)})

    return None
