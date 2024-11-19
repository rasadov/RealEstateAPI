from fastapi import APIRouter, Depends

from src.admin.service import AdminService
from src.admin.dependencies import get_admin_service
from src.auth.dependencies import get_current_user
from src.auth.schemas import TokenData

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"]
)

@router.get("/users/all")
async def get_users(
    page: int,
    elements: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.get_users_page(current_user, page, elements)

@router.get("/users/agent")
async def get_agents(
    page: int,
    elements: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.get_users_page(current_user, page, elements, role="agent")

@router.get("/users/agent")
async def get_agents(
    page: int,
    elements: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.get_users_page(current_user, page, elements, role="buyer")

@router.get("/properties/unapproved")
async def get_unapproved_properties(
    page: int,
    elements: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.get_unapproved_properties_page(current_user, page, elements)

@router.get("/approvals")
async def get_approvals(
    page : int,
    elements: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.get_approvals(current_user, page, elements)

@router.get("/sold-properties")
async def get_sold_properties(
    page: int,
    elements: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.get_sold_properties(current_user, page, elements)

@router.patch("/approve-property")
async def approve_property(
    property_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.approve_property(current_user, property_id)

@router.patch("/deactivate-property")
async def deactivate_property(
    property_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.deactivate_property(current_user, property_id)

@router.delete("/delete-property")
async def delete_property(
    property_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: TokenData = Depends(get_current_user)
    ):
    return await admin_service.delete_property(current_user, property_id)
