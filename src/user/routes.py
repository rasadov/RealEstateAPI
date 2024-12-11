"""User routes module."""
from fastapi import Depends, APIRouter

from src.user.service import UserService
from src.user.dependencies import get_user_service
from src.user.schemas import (EmailSchema, ChangePasswordSchema,
                              ResetPasswordSchema, UpdateUserSchema,
                              UpdateAgentSchema, ReviewSchema)
from src.auth.dependencies import get_current_user
from src.auth.schemas import TokenData

router = APIRouter(
    prefix="/api/v1/user",
    tags=["User"]
)

@router.get("/me")
async def get_user(
    user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.get_user(
        user.user_id,
        )

@router.get("/agent/{agent_id}")
async def get_agent(
    agent_id: int,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.get_agent(
        agent_id,
        )

@router.post("/forgot-password")
async def forgot_password(
    schema: EmailSchema,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.forgot_password(
        schema.email,
        )

@router.post("/get-confirm-email-token")
async def get_confirm_email_token(
    schema: EmailSchema,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.send_confirm_email(
        schema.email,
        )

@router.post("/review")
async def add_review(
    schema: ReviewSchema,
    user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.add_review(
        user.user_id,
        schema.agent_id,
        schema.rating,
        schema.comment,
        )

@router.patch("/change-password")
async def change_password(
    schema: ChangePasswordSchema,
    user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.change_password(
        user.user_id,
        schema.old_password,
        schema.new_password,
        )

@router.patch("/reset-password")
async def reset_password(
    schema: ResetPasswordSchema,
    token: str,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.reset_password(
        token,
        schema.password,
        )

@router.patch("/confirm-email")
async def confirm_email(
    schema: ResetPasswordSchema,
    token: str,
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.confirm_email(
        token,
        schema.password,
        )

@router.patch("/update/user")
async def update_user(
    schema: UpdateUserSchema,
    user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.update_user(
        user.user_id,
        schema.model_dump(exclude_none=True),
        )

@router.patch("/update/agent")
async def update_agent(
    schema: UpdateAgentSchema,
    user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.update_agent(
        user.user_id,
        schema.model_dump(exclude_none=True),
        )

@router.delete("/delete")
async def delete_user(
    user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
    ):
    return await user_service.delete_user(
        user.user_id,
        )
