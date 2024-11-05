from fastapi import Depends, HTTPException, Request, status
import jwt

from src.auth.service import AuthService
from src.auth.exceptions import CredentialsException
from src.user.dependencies import get_user_service
from src.auth.schemas import TokenData
from src.config import ALGORITHM, SECRET_KEY


def get_auth_service(
    user_service=Depends(get_user_service),
) -> AuthService:
    """Dependency injector for auth service"""
    return AuthService(user_service)

def get_current_user(request: Request) -> TokenData:
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise CredentialsException

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise CredentialsException
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError as e:
        raise CredentialsException from e
    return token_data
