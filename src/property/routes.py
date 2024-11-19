from fastapi import APIRouter, Depends, UploadFile

from src.property.service import PropertyService
from src.property.dependencies import get_property_service
from src.auth.dependencies import get_current_user
from src.auth.schemas import TokenData

router = APIRouter(
    prefix="/api/v1/property",
    tags=["Property"]
)

@router.get("/{id}")
async def get_property_by_id(
    id: int,
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_property_by_id(id)

@router.get("/map")
async def get_map_locations(
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_map_locations()

@router.get("/page")
async def get_properties_page(
    page: int,
    elements: int,
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_properties_page(
        page, elements)

@router.post("/create")
async def create_property(
    payload: dict,
    images: list[UploadFile] = None,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.create_property(
        payload, images, user.user_id)

@router.put("/{id}")
async def update_property(
    id: int,
    payload: dict,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.update_property(
        id, payload, user.user_id)

@router.post("/{id}/image")
async def add_image_to_property(
    id: int,
    image: UploadFile,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.add_image_to_property(
        id, image, user.user_id)

@router.delete("/{id}/image/{image_id}")
async def delete_image_from_property(
    id: int,
    image_id: int,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.delete_image_from_property(
        id, image_id, user.user_id)

@router.delete("/{id}")
async def delete_property(
    id: int,
    user: TokenData   = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.delete_property(
        id, user.user_id)

@router.post("/{id}/approve")
async def approve_property(
    id: int,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.approve_property(
        id, user.user_id)