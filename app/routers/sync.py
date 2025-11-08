from fastapi import APIRouter, HTTPException, Depends
from app.models import CreateSheetRequest, CreateSheetResponse
from app.database import get_database
from app.auth import get_current_user
from app.services.sheets_service import GoogleSheetsService
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/sync", tags=["Google Sheets Sync"])


@router.post("/create-sheet", response_model=CreateSheetResponse)
async def create_google_sheet(
    request: CreateSheetRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await GoogleSheetsService.create_sheet(
            user_email=current_user['email'],
            sheet_name=request.sheet_name
        )

        return CreateSheetResponse(
            sheet_id=result['sheet_id'],
            sheet_name=result['sheet_name'],
            sheet_url=result['sheet_url'],
            message="Google Sheet created successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sheet: {str(e)}")


@router.post("/{sheet_id}/to-cloud")
async def sync_to_cloud(
    sheet_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        db = get_database()

        users = await db.users.find({}).to_list(length=None)

        if not users:
            return {
                "message": "No users found to sync",
                "synced_count": 0
            }

        result = await GoogleSheetsService.sync_to_cloud(
            user_email=current_user['email'],
            sheet_id=sheet_id,
            users_data=users
        )

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync to cloud: {str(e)}")


@router.post("/{sheet_id}/from-cloud")
async def sync_from_cloud(
    sheet_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        db = get_database()

        sheet_users = await GoogleSheetsService.sync_from_cloud(
            user_email=current_user['email'],
            sheet_id=sheet_id
        )

        if not sheet_users:
            return {
                "message": "No users found in Google Sheet",
                "inserted": 0,
                "updated": 0
            }

        inserted_count = 0
        updated_count = 0

        for sheet_user in sheet_users:
            if not sheet_user.get('email'):
                continue

            user_id = sheet_user.get('id')
            existing_user = None

            if user_id and ObjectId.is_valid(user_id):
                existing_user = await db.users.find_one({"_id": ObjectId(user_id)})

            if not existing_user:
                existing_user = await db.users.find_one({"email": sheet_user['email']})

            user_data = {
                "name": sheet_user.get('name', ''),
                "email": sheet_user['email'],
                "role": sheet_user.get('role', ''),
            }

            if existing_user:
                await db.users.update_one(
                    {"_id": existing_user["_id"]},
                    {"$set": user_data}
                )
                updated_count += 1
            else:
                user_data['created_at'] = datetime.utcnow()

                await db.users.insert_one(user_data)
                inserted_count += 1

        return {
            "message": f"Successfully synced from Google Sheets",
            "inserted": inserted_count,
            "updated": updated_count,
            "total_processed": len(sheet_users)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync from cloud: {str(e)}")
