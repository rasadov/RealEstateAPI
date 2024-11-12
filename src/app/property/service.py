from dataclasses import dataclass
from typing import List, Dict, Any
from fastapi import UploadFile

from app.property.repository import PropertyRepository
from app.user.repository import UserRepository
from app.auth import exceptions
from app.property.models import Property

@dataclass
class PropertyService:
    """Property service"""

    propertyRepository: PropertyRepository
    userRepository: UserRepository

    async def get_property_by_id(self, id: int) -> Property:
        """Get property by id"""
        return await self.propertyRepository.get_or_404(id)

    async def get_properties_page(self, page: int, elements: int) -> Dict[str, Any]:
        """Get properties page"""
        offset = (page - 1) * elements
        properties: List[Property] = await self.propertyRepository.get_properties_page(elements, offset)
        count: int = await self.propertyRepository.get_properties_count()
        total_pages: int = (count - 1) // elements + 1
        return {
            "properties": properties,
            "total_pages": total_pages,
        }
    
    async def create_property(self, payload: dict, images: List[UploadFile], user_id: int) -> Property:
        """Create property"""
        return await self.propertyRepository.create_property(payload, images, user_id)
    
    async def approve_property(self, property_id: int, user_id: int) -> Property:
        """Approve property"""
        user = await self.userRepository.get_or_401(user_id)

        if user.role != "admin":
            raise exceptions.Unauthorized

        return await self.propertyRepository.approve_property(property_id)
    
    async def delete_property(self, property_id: int, user_id: int) -> Property:
        """Delete property"""
        user = await self.userRepository.get_or_401(user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if user.role != "admin" and property.owner_id != user_id:
            raise exceptions.Unauthorized

        return await self.propertyRepository.delete_property(property_id)

    async def update_property(self, property_id: int, payload: dict, user_id: int) -> Property:
        """Update property"""
        user = await self.userRepository.get_or_401(user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if user.role != "admin" and property.owner_id != user_id:
            raise exceptions.Unauthorized

        return await self.propertyRepository.update_property(property_id, payload)

    async def add_image_to_property(self, property_id: int, image: UploadFile, user_id: int) -> Property:
        """Add image to property"""
        user = await self.userRepository.get_or_401(user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if user.role != "admin" and property.owner_id != user_id:
            raise exceptions.Unauthorized

        return await self.propertyRepository.add_image_to_property(property_id, image)
