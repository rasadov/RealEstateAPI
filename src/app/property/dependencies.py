"""Module with user related dependencies"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import (
    get_db_session,
)
from app.property.repository import PropertyRepository
from app.property.service import PropertyService
from app.staticfiles.dependencies import get_static_files_manager

def get_property_repository(
    session: AsyncSession = Depends(get_db_session),
    static_files_manager=Depends(get_static_files_manager),
):
    """Dependency injector for user repository"""
    return PropertyRepository(session, static_files_manager)

def get_property_service(
    property_repository: PropertyRepository = Depends(get_property_repository),
):
    """Dependency injector for user service"""
    return PropertyService(property_repository)