"""User routes module."""
from fastapi import Depends, APIRouter

from src.user.service import UserService
from src.user.dependencies import get_user_service
from src.auth.dependencies import get_current_user
from src.auth.schemas import TokenData

router = APIRouter(
    prefix="/api/v1/user",
    tags=["User"]
)

@router.patch("/change-password")
async def change_password(payload: dict, user: TokenData = Depends(get_current_user),
                          user_service: UserService = Depends(get_user_service)):
    return await user_service.change_password(
        user.user_id,
        payload.get("old_password"),
        payload.get("new_password"),
        )

@router.post("/forgot-password")
async def forgot_password(
    payload: dict,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.forgot_password(
        payload.get("email"),
        )

@router.patch("/reset-password")
async def reset_password(
    payload: dict,
    token: str,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.reset_password(
        token,
        payload.get("password"),
        )

@router.post("/get-confirm-email-token")
async def get_confirm_email_token(
    payload: dict,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.send_confirm_email(
        payload.get("email"),
        )

@router.patch("/confirm-email")
async def confirm_email(
    payload: dict,
    token: str,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.confirm_email(
        token,
        payload.get("password"),
        )
