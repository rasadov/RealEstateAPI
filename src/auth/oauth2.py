"""
Functions for handling OAuth2 token creation and verification.
"""
from datetime import datetime, timedelta, timezone
from enum import Enum

from fastapi import HTTPException, Request, status
import jwt

from src.auth.schemas import TokenData
from src.config import (SECRET_KEY, ALGORITHM,
                        ACCESS_TOKEN_EXPIRE_MINUTES,
                        REFRESH_TOKEN_EXPIRE_MINUTES)

class AuthTokenTypes(str, Enum):
    """Enum class with authentication token types"""

    ACCESS = "auth-access"
    REFRESH = "auth-refresh"

def _create_auth_token(data: dict, expire_minutes: int):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(user_id: int):
    """Create access token"""
    data = {"sub": AuthTokenTypes.ACCESS, "user_id": user_id}
    return _create_auth_token(data, ACCESS_TOKEN_EXPIRE_MINUTES)

def create_refresh_token(user_id: int):
    """Create refresh token"""
    data = {"sub": AuthTokenTypes.REFRESH, "user_id": user_id}
    return _create_auth_token(data, REFRESH_TOKEN_EXPIRE_MINUTES)

def generate_auth_tokens(user_id: int):
    """Generate access and refresh tokens"""
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def _verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        token_data = TokenData(user_id=user_id)
        return token_data
    except jwt.PyJWTError:
        raise credentials_exception

async def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise credentials_exception

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError as e:
        raise credentials_exception
    return token_data

def verify_action_token(token: str, action: str, credentials_exception):
    token_data = _verify_token(token, credentials_exception)
    if token_data and token_data.id and token_data.sub == action:
        return token_data.id
    return None
