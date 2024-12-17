from fastapi import APIRouter, Depends, UploadFile, File, Query
from typing import Optional

from src.property.service import PropertyService
from src.property.dependencies import get_property_service
from src.auth.dependencies import get_current_user, get_current_user_optional
from src.auth.schemas import TokenData
from src.property.schemas import CreatePropertySchema, SearchPropertySchema


router = APIRouter(
    prefix="/api/v1/property",
    tags=["Property"]
)

@router.get("/")
async def get_properties_page(
    schema: SearchPropertySchema = Depends(SearchPropertySchema),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_properties_page(
        schema)

@router.get("/map")
async def get_map_locations(
    property_service: PropertyService = Depends(get_property_service)
    ):
    print("HERE IS THE MAP LOCATIONS")
    return await property_service.get_map_locations()

@router.get("/record/{id}")
async def get_property_by_id(
    id: int,
    property_service: PropertyService = Depends(get_property_service),
    current_user: Optional[TokenData] = Depends(get_current_user_optional),
    ):
    return await property_service.get_property_by_id(id, current_user)

@router.get("/agent/{agent_id}/page")
async def get_properties_by_agent_page(
    agent_id: int,
    page: int = Query(1),
    elements: int = Query(10),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_properties_by_agent_page(
        agent_id, page, elements)

@router.post("/create")
async def create_property(
    payload: CreatePropertySchema = Depends(CreatePropertySchema.as_form),
    files: list[UploadFile] = File(...),
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.create_property(
        payload, files, user.user_id
    )

@router.post("/image/{property_id}")
async def add_image_to_property(
    property_id: int,
    files: list[UploadFile] = File(...),
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.add_images_to_property(
        property_id, files, user.user_id)

@router.put("update/{id}")
async def update_property(
    id: int,
    payload: dict,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    print("HERE IS THE PAYLOAD", payload)
    return await property_service.update_property(
        id, payload, user.user_id)

@router.delete("/record/{id}/image/{image_id}")
async def delete_image_from_property(
    id: int,
    image_id: int,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    print("HERE IS THE IMAGE ID", image_id)
    return await property_service.delete_image_from_property(
        id, image_id, user.user_id)

@router.delete("/record/{id}")
async def delete_property(
    id: int,
    is_sold: bool = Query(False),
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.delete_property(
        id, user.user_id, is_sold=is_sold)
