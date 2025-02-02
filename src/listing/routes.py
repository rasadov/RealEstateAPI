from fastapi import APIRouter, Depends, UploadFile, File, Query

from src.property.service import PropertyService
from src.property.dependencies import get_property_service
from src.auth.dependencies import get_current_user
from src.auth.schemas import TokenData
from src.listing.schemas import CreateListingSchema
from src.property.service import PropertyService
from src.property.dependencies import get_property_service


router = APIRouter(
    prefix='/api/v1/listing',
    tags=['listing']
)


@router.get("/page")
async def get_listings_page(
    page: int = Query(1),
    elements: int = Query(10),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_listings_page(
        page, elements)

@router.get("/me")
async def get_user_listings(
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_user_listings(user.user_id)

@router.get("/record/{id}")
async def get_listing_by_id(
    id: int,
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_listing_by_id(id)

@router.post("/")
async def create_listing(
    schema: CreateListingSchema = Depends(CreateListingSchema.as_form),
    files: list[UploadFile] = File(...),
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    print("HERE IS THE SCHEMA", schema)
    return await property_service.create_listing(
        schema, files, user.user_id)

@router.post("/image/{listing_id}")
async def add_image_to_listing(
    listing_id: int,
    files: list[UploadFile] = File(...),
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.add_images_to_listing(
        listing_id, files, user.user_id)

@router.put("/{id}")
async def update_listing(
    id: int,
    payload: dict,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.update_listing(
        id, payload, user.user_id)

@router.delete("/record/{id}")
async def delete_listing(
    id: int,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.delete_listing(
        id, user.user_id)

@router.delete("/record/{id}/image/{image_id}")
async def delete_image_from_listing(
    id: int,
    image_id: int,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.delete_image_from_listing(
        id, image_id, user.user_id)
