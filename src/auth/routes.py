"""
Contains routes for user authentication and authorization.
"""
from fastapi import APIRouter, Depends, Response

from src.auth.service import AuthService
from src.auth.dependencies import get_auth_service
from src.config import Settings

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@router.post("/register")
async def register(
    user: dict,
    auth_service: AuthService = Depends(get_auth_service),
    ):
    return await auth_service.register(user)

@router.post("/login")
async def login(
    user: dict,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    ):
    return await auth_service.login(user, response)

@router.post('/logout')
async def logout(
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    ):
    return await auth_service.logout(response)

@router.get("/login/google")
async def login_google():
    return {
        "url": (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"response_type=code&client_id={Settings.GOOGLE_CLIENT_ID}&"
            f"redirect_uri={Settings.GOOGLE_REDIRECT_URI}&"
            f"scope=openid%20profile%20email&"
            f"access_type=offline"
        )
    }

@router.post('/auth/google')
async def auth_google(
    code: str,
    auth_service: AuthService = Depends(get_auth_service),
    ):
    return await auth_service.auth_google(code)
