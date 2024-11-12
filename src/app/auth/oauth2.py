"""
Functions for handling OAuth2 token creation and verification.
"""
from datetime import datetime, timedelta, timezone
from enum import Enum

import jwt

from app.auth.schemas import TokenData
from app.config import (SECRET_KEY, ALGORITHM,
                        ACCESS_TOKEN_EXPIRE_MINUTES,
                        REFRESH_TOKEN_EXPIRE_MINUTES)

class AuthTokenTypes(str, Enum):
    """Enum class with authentication token types"""

    ACCESS = "auth-access"
    REFRESH = "auth-refresh"
    FORGOT_PASSWORD = "forgot-password"
    CONFIRM_EMAIL = "confirm-email"


def _create_auth_token(data: dict, expire_minutes: int) -> str:
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_token(user_id: int, token_type: AuthTokenTypes, expire_minutes: int) -> str:
    """Create a token with the specified type and expiration"""
    data = {"sub": token_type, "user_id": user_id}
    return _create_auth_token(data, expire_minutes)

def create_access_token(user_id: int) -> str:
    """Create access token"""
    return create_token(user_id, AuthTokenTypes.ACCESS, ACCESS_TOKEN_EXPIRE_MINUTES)

def create_refresh_token(user_id: int) -> str:
    """Create refresh token"""
    return create_token(user_id, AuthTokenTypes.REFRESH, REFRESH_TOKEN_EXPIRE_MINUTES)

def create_forgot_password_token(user_id: int) -> str:
    """Create forgot password token"""
    return create_token(user_id, AuthTokenTypes.FORGOT_PASSWORD, ACCESS_TOKEN_EXPIRE_MINUTES)

def create_confirm_email_token(user_id: int) -> str:
    """Create confirm email token"""
    return create_token(user_id, AuthTokenTypes.CONFIRM_EMAIL, ACCESS_TOKEN_EXPIRE_MINUTES)

def generate_auth_tokens(user_id: int) -> dict:
    """Generate access and refresh tokens"""
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

def decode_token(token: str, credentials_exception) -> TokenData:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        token_data = TokenData(user_id=user_id)
        return token_data
    except jwt.PyJWTError:
        raise credentials_exception

def verify_action_token(token: str, action: str, credentials_exception) -> int | None:
    token_data = decode_token(token, credentials_exception)
    if token_data and token_data.user_id and token_data.sub == action:
        return token_data.user_id
    return None