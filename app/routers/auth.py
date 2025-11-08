from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.auth import create_flow, get_user_info, save_authenticated_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/login")
async def login():
    try:
        flow = create_flow()

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        return JSONResponse({
            "authorization_url": authorization_url,
            "message": "Please visit the authorization URL to complete login"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth flow: {str(e)}")


@router.get("/callback")
async def callback(code: str):
    try:
        flow = create_flow()

        flow.fetch_token(code=code)

        credentials = flow.credentials

        user_info = await get_user_info(credentials)

        await save_authenticated_user(
            email=user_info.get("email"),
            name=user_info.get("name"),
            profile_pic=user_info.get("picture"),
            access_token=credentials.token,
            refresh_token=credentials.refresh_token
        )

        return JSONResponse({
            "message": "Authentication successful",
            "user": {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "profile_pic": user_info.get("picture")
            },
            "access_token": user_info.get("email")
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to authenticate: {str(e)}")


@router.get("/me")
async def get_current_user_info(email: str):
    from app.auth import get_authenticated_user

    user = await get_authenticated_user(email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "email": user["email"],
        "name": user["name"],
        "profile_pic": user.get("profile_pic"),
        "created_at": user["created_at"]
    }
