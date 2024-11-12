"""User routes module."""
from fastapi import Depends, APIRouter

from app.user.service import UserService
from app.user.dependencies import get_user_service
from app.auth.dependencies import get_current_user
from app.auth.schemas import TokenData

router = APIRouter(
    prefix="/api/v1/user",
    tags=["User"]
)

@router.post("/change-password")
async def change_password(payload: dict, user: TokenData = Depends(get_current_user),
                          userService: UserService = Depends(get_user_service)):
    return await userService.change_password(user.user_id, payload.get("old_password"), payload.get("new_password"))

@router.post("/forgot-password")
async def forgot_password(
    payload: dict,
    userService: UserService = Depends(get_user_service)
    ):
    return await userService.forgot_password(payload.get("email"))

@router.post("/reset-password")
async def reset_password(
    payload: dict,
    token: str,
    userService: UserService = Depends(get_user_service)
    ):
    return await userService.reset_password(token, payload.get("password"))

@router.post("/get-confirm-email-token")
async def get_confirm_email_token(
    payload: dict,
    userService: UserService = Depends(get_user_service)
    ):
    return await userService.send_confirm_email(payload.get("email"))

@router.post("/confirm-email")
async def confirm_email(
    payload: dict,
    token: str,
    userService: UserService = Depends(get_user_service)
    ):
    return await userService.confirm_email(token, payload.get("password"))
