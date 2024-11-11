"""Module with user related dependencies"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import (
    get_db_session,
)
from src.user.repository import UserRepository
from src.user.service import UserService
from src.staticfiles.dependencies import get_static_files_manager

def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
    static_files_manager=Depends(get_static_files_manager),
):
    """Dependency injector for user repository"""
    return UserRepository(session, static_files_manager)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
):
    """Dependency injector for user service"""
    return UserService(user_repository)
