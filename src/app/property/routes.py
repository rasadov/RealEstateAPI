from fastapi import APIRouter, Depends, UploadFile

from app.property.service import PropertyService
from app.property.dependencies import get_property_service
from app.auth.dependencies import get_current_user
from app.auth.schemas import TokenData

router = APIRouter(
    prefix="/api/v1/property",
    tags=["Property"]
)

@router.get("/{id}")
async def get_property_by_id(
    id: int,
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.get_property_by_id(id)

@router.get("/")
async def get_properties_page(
    page: int,
    elements: int,
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.get_properties_page(page, elements)

@router.post("/")

@router.post("/")
async def create_property(
    payload: dict,
    images: list[UploadFile] = None,
    user=Depends(get_current_user),
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.create_property(payload, images, user.user_id)

@router.put("/{id}")
async def update_property(
    id: int,
    payload: dict,
    user=Depends(get_current_user),
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.update_property(id, payload, user.user_id)

@router.post("/{id}/image")
async def add_image_to_property(
    id: int,
    image: UploadFile,
    user=Depends(get_current_user),
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.add_image_to_property(id, image, user.user_id)

@router.delete("/{id}/image/{image_id}")
async def delete_image_from_property(
    id: int,
    image_id: int,
    user=Depends(get_current_user),
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.delete_image_from_property(id, image_id, user.user_id)

@router.delete("/{id}")
async def delete_property(
    id: int,
    user: TokenData = Depends(get_current_user),
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.delete_property(id, user.user_id)

@router.post("/{id}/like")
async def like_property(
    id: int,
    user=Depends(get_current_user),
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.like_property(id, user.user_id)

@router.delete("/{id}/like")
async def unlike_property(
    id: int,
    user=Depends(get_current_user),
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.unlike_property(id, user.user_id)

@router.post("/{id}/approve")
async def approve_property(
    id: int,
    user=Depends(get_current_user),
    propertyService: PropertyService = Depends(get_property_service)
    ):
    return await propertyService.approve_property(id, user.user_id)
