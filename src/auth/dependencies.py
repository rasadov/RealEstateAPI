from fastapi import Depends, Request
import jwt

from src.auth.service import AuthService
from src.auth.exceptions import CredentialsException
from src.user.dependencies import get_user_service
from src.auth.schemas import TokenData
from src.config import Settings


def get_auth_service(
    user_service=Depends(get_user_service),
) -> AuthService:
    """Dependency injector for auth service"""
    return AuthService(user_service)

def _get_payload_from_token(
        access_token: str,
        SECRET_KEY: str,
        ALGORITHMS: list[str]
) -> dict:
    payload = jwt.decode(
        access_token,
        SECRET_KEY,
        algorithms=ALGORITHMS
    )
    return payload

def get_current_user(
        request: Request
) -> TokenData:
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise CredentialsException

    try:
        user_id = _get_payload_from_token(
            access_token,
            Settings.SECRET_KEY,
            [Settings.ALGORITHM]
        ).get("user_id")
        if user_id is None:
            raise CredentialsException
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError as e:
        raise CredentialsException from e
    return token_data

def get_current_user_optional(
        request: Request
) -> TokenData | None:
    access_token = request.cookies.get("access_token")

    if not access_token:
        return None

    try:
        user_id = _get_payload_from_token(
            access_token,
            Settings.SECRET_KEY,
            [Settings.ALGORITHM]
        ).get("user_id")
        if user_id is None:
            return None
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError:
        return None
    return token_data
