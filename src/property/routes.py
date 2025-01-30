from fastapi import APIRouter, Depends, UploadFile, File, Query
from typing import Optional

from src.property.service import PropertyService
from src.property.dependencies import get_property_service
from src.auth.dependencies import get_current_user, get_current_user_optional
from src.auth.schemas import TokenData
from src.property.schemas import CreatePropertySchema, SearchPropertySchema, MapSearchSchema


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

@router.get("/popular")
async def get_popular_properties(
    elements: int = Query(10),
    page: int = Query(1),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_popular_properties(
        limit=elements, offset=(page-1)*elements)

@router.get("/map")
async def get_map_locations(
    schema: MapSearchSchema = Depends(MapSearchSchema),
    property_service: PropertyService = Depends(get_property_service)
    ):
    result = await property_service.get_map_locations(schema)
    print("RESULT ", result)
    return result

@router.get("/fav")
async def get_fav_properties(
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    offset = 0
    limit = 10
    return await property_service.property_repository.get_favorites_page(
        user.user_id, limit, offset)

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

@router.get("/me/liked")
async def get_user_liked_properties(
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.get_favorites_ids(user.user_id)

@router.get("/areas")
async def get_areas():
    return {
        "cities": [
        "Lefkoşa",
        "Girne",
        "Gazimağusa",
        "Güzelyurt",
        "İskele",
        "Lefke",
        "Lapta",
        "Koruçam",
        "Alsancak",
        "Değirmenlik",
        "Esentepe",
        "Dikmen",
        "Mehmetçik",
        "Karpaz",
        "Dipkarpaz",
        "Yeni Erenköy",
        "Geçitkale",
        "Beşparmak"
        ],
        "areas": [
            "Lefkoşa",
            "Girne",
            "Gazimağusa",
            "Güzelyurt",
            "İskele",
            "Lefke"
        ]
    }

@router.post("/create")
async def create_property(
    payload: CreatePropertySchema = Depends(CreatePropertySchema.as_form),
    files: list[UploadFile] = File(...),
    # documents: Optional[list[UploadFile]] = File(...),
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    documents = []
    print("USER DATA ", user)
    return await property_service.create_property(
        payload, files, documents, user.user_id
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

@router.post("/like/{property_id}")
async def like_property(
    property_id: int,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.like_property(
        property_id, user.user_id)

@router.post("/view/{property_id}")
async def view_property(
    property_id: int,
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.viewed_property(
        property_id)

@router.put("update/{id}")
async def update_property(
    id: int,
    payload: dict,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
    return await property_service.update_property(
        id, payload, user.user_id)

@router.delete("/record/{id}/image/{image_id}")
async def delete_image_from_property(
    id: int,
    image_id: int,
    user: TokenData = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
    ):
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
