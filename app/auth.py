from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from fastapi import HTTPException, Request
from app.config import settings
from app.database import get_database
from datetime import datetime
import json

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/spreadsheets'
]


def create_flow():
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.oauth_redirect_url]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=settings.oauth_redirect_url
    )
    return flow


async def get_user_info(credentials: Credentials):
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    return user_info


async def save_authenticated_user(email: str, name: str, profile_pic: str,
                                   access_token: str, refresh_token: str):
    db = get_database()

    user_data = {
        "email": email,
        "name": name,
        "profile_pic": profile_pic,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    await db.authenticated_users.update_one(
        {"email": email},
        {"$set": user_data},
        upsert=True
    )


async def get_authenticated_user(email: str):
    db = get_database()
    user = await db.authenticated_users.find_one({"email": email})
    return user


async def get_user_credentials(email: str) -> Credentials:
    user = await get_authenticated_user(email)

    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    if not user.get("access_token"):
        raise HTTPException(status_code=401, detail="No access token found")

    credentials = Credentials(
        token=user["access_token"],
        refresh_token=user.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES
    )

    return credentials


async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    email = auth_header.replace("Bearer ", "")

    user = await get_authenticated_user(email)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
