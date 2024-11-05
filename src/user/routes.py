"""User routes module."""
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.schemas import UserRegisterSchema
from src.db import get_db_session
from src.user.service import UserService
from src.user.dependencies import get_user_service

router = APIRouter(
    prefix="/api/v1/user",
    tags=["User"]
)

@router.post('/register')
async def register(user: UserRegisterSchema,
                   userService: UserService = Depends(get_user_service),
                   ):
    return await userService.register(user)

# Reset password and forgot password routes

@router.post("/forgot-password")
async def forgot_password(payload: dict, db: AsyncSession = Depends(get_db_session)):
    # TO DO: Send email with token
    # email = payload.get("email")
    # result = await db.execute(select(models.User).filter(models.User.email == email))
    # user = result.scalars().first()

    # if user is None:
    #     raise HTTPException(status_code=404, detail="User not found")

    # token = oauth2.create_access_token(data={"user_id": user.id, "sub": "forgot_password"})

    pass

# @router.post("/reset-password")
# async def reset_password(payload: dict, token: str = Query(...),
#                          db: AsyncSession = Depends(get_db_session)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid or expired token",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     user_id = oauth2.verify_action_token(token, "forgot_password", credentials_exception)
#     if user_id is None:
#         raise credentials_exception

#     result = await db.execute(select(models.User).filter(models.User.id == user_id))
#     user = result.scalars().first()

#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     user.password_hash = utils.hash_password(payload.get("password"))
#     await db.commit()

#     return {"message": "Password reset successfully"}

# TO DO: Confirm email route
