"""Module with user related dependencies"""
from fastapi import Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import (
    get_db_session,
)
from src.property.repository import PropertyRepository
from src.property.service import PropertyService
from src.property.schemas import CreatePropertySchema
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

def create_property_form(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    category: str = Form(...),
    total_area: float = Form(...),
    living_area: float = Form(...),
    bedrooms: int = Form(...),
    living_rooms: int = Form(...),
    floor: int = Form(...),
    floors: int = Form(...),
    district: str = Form(...),
    address: str = Form(...)
) -> CreatePropertySchema:
    return CreatePropertySchema(
        name=name,
        description=description,
        price=price,
        latitude=latitude,
        longitude=longitude,
        category=category,
        total_area=total_area,
        living_area=living_area,
        bedrooms=bedrooms,
        living_rooms=living_rooms,
        floor=floor,
        floors=floors,
        district=district,
        address=address
    )
