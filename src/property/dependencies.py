"""Module with user related dependencies"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import (
    get_db_session,
)
from src.property.repository import PropertyRepository
from src.property.service import PropertyService
from src.staticfiles.dependencies import get_static_files_manager
from src.user.dependencies import get_user_repository


def get_property_repository(
    session: AsyncSession = Depends(get_db_session),
    static_files_manager=Depends(get_static_files_manager),
) -> PropertyRepository:
    """Dependency injector for user repository"""
    return PropertyRepository(session, static_files_manager)

def get_property_service(
    property_repository: PropertyRepository = Depends(get_property_repository),
    user_repository=Depends(get_user_repository),
) -> PropertyService:
    """Dependency injector for user service"""
    return PropertyService(property_repository, user_repository)
