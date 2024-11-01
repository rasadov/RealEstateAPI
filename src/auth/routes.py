"""
Contains routes for user authentication and authorization.
"""
from fastapi import Depends, APIRouter, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from db.base import get_db
from schemas import UserRegisterSchema, UserLoginSchema
from auth import (utils, exceptions, oauth2, models,
                  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI)


router = APIRouter(
    tags=["Authentication"]
)

@router.post('/register')
async def register(user: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
    user_exists = await db.execute(select(models.User).filter(models.User.email == user.email))
    if user_exists.scalars().first():
        raise exceptions.UserAlreadyExists

    new_user = models.User(
        email=user.email,
        password_hash=utils.hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = oauth2.create_access_token(data={"user_id": new_user.id})
    response = JSONResponse(content={"message": "User created successfully",
                                "email": new_user.email,
                                "user_id": new_user.id,
                                "role": new_user.role})

    response.set_cookie("access_token", access_token)
    return response

@router.post("/login")
async def login(cred: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.email == cred.email))
    user = result.scalars().first()

    if user is None or not utils.verify_password(cred.password, user.password_hash):
        raise exceptions.InvalidCredentials

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    response = JSONResponse(content={
        "message": "Login successful",
        "email": user.email,
        "user_id": user.id,
        "role": user.role,
    })

    response.set_cookie("access_token", access_token)

    return response

@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

# Authentication with Google

@router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }

@router.post("/auth/google")
async def auth_google(code: str, db: AsyncSession = Depends(get_db)):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with AsyncClient() as client:
        response = await client.post(token_url, data=data)
        access_token = response.json().get("access_token")
        user_info_response = await client.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                              headers={"Authorization": f"Bearer {access_token}"})

    if user_info_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    user_info = user_info_response.json()
    result = await db.execute(select(models.User).filter(models.User.email == user_info.get("email")))
    user = result.scalars().first()
    
    if user:
        access_token = oauth2.create_access_token(data={"user_id": user.id})
        response = JSONResponse(content={
            "message": "Login successful",
            "email": user.email,
            "user_id": user.id,
            "role": user.role,
        })

        response.set_cookie("access_token", access_token)
        return response

    new_user = models.User(
        email=user_info.get("email"),
        password_hash="",
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = oauth2.create_access_token(data={"user_id": new_user.id})
    response = JSONResponse(content={
        "message": "Login successful",
        "email": new_user.email,
        "user_id": new_user.id,
        "role": new_user.role,
    })

    response.set_cookie("access_token", access_token)
    return response

# Reset password and forgot password routes

@router.post("/forgot-password")
async def forgot_password(payload: dict, db: AsyncSession = Depends(get_db)):
    # TO DO: Send email with token
    email = payload.get("email")
    result = await db.execute(select(models.User).filter(models.User.email == email))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    token = oauth2.create_access_token(data={"user_id": user.id, "sub": "forgot_password"})

    pass

@router.post("/reset-password")
async def reset_password(payload: dict, token: str = Query(...),
                         db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = oauth2.verify_action_token(token, "forgot_password", credentials_exception)
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = utils.hash_password(payload.get("password"))
    await db.commit()

    return {"message": "Password reset successfully"}

# TO DO: Confirm email route