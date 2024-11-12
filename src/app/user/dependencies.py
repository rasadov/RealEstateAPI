"""Module with user related dependencies"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import (
    get_db_session,
)
from app.user.repository import UserRepository
from app.user.service import UserService
from app.staticfiles.dependencies import get_static_files_manager

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
