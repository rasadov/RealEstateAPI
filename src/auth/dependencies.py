from fastapi import Depends

from src.auth.service import AuthService
from src.user.dependencies import get_user_service


def get_auth_service(
    user_service=Depends(get_user_service),
):
    """Dependency injector for auth service"""
    return AuthService(user_service)
