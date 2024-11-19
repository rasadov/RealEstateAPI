from fastapi import Depends

from src.admin.service import AdminService
from src.user.dependencies import get_user_repository
from src.user.repository import UserRepository
from src.property.dependencies import get_property_repository
from src.property.repository import PropertyRepository

def get_admin_service(
        user_repository: UserRepository = Depends(get_user_repository),
        property_repository: PropertyRepository = Depends(get_property_repository),
) -> AdminService:
    """Get admin service."""
    return AdminService(user_repository, property_repository)
