from dataclasses import dataclass
from typing import Dict, Any, Sequence

from fastapi import UploadFile

from src.property.repository import PropertyRepository
from src.user.repository import UserRepository
from src.auth import exceptions
from src.property.models import Property, Location

@dataclass
class PropertyService:
    """Property service"""

    propertyRepository: PropertyRepository
    userRepository: UserRepository

    async def get_property_by_id(
            self,
            id: int,
            ) -> Property:
        """Get property by id"""
        return await self.propertyRepository.get_or_404(id)

    async def get_properties_page(
            self,
            page: int,
            elements: int,
            ) -> Dict[str, Any]:
        """Get properties page"""
        offset = (page - 1) * elements
        properties = await self.propertyRepository.get_properties_page(
            elements, offset)
        count = await self.propertyRepository.get_properties_count()
        total_pages = (count - 1) // elements + 1
        return {
            "properties": properties,
            "total_pages": total_pages,
        }
    
    async def get_map_locations(
            self,
            ) -> Sequence[Location]:
        """Get map locations"""
        return await self.propertyRepository.get_map_locations()
    
    async def get_at_location(
            self,
            latitude: float,
            longitude: float,
            ) -> Sequence[Property]:
        """Returns all properties at a location"""
        return await self.propertyRepository.get_at_location(
            latitude, longitude)

    async def create_property(
            self,
            payload: dict,
            images: list[UploadFile],
            user_id: int,
            ) -> Property:
        """Create property"""
        return await self.propertyRepository.create_property(
            payload, images, user_id)

    async def approve_property(
            self,
            property_id: int,
            user_id: int,
            ) -> Property:
        """Approve property"""
        user = await self.userRepository.get_or_401(user_id)

        if user.level < 1:
            raise exceptions.Unauthorized

        return await self.propertyRepository.approve_property(property_id)

    async def delete_property(
            self,
            property_id: int,
            user_id: int,
            sold: bool,
            ) -> Property:
        """Delete property"""
        await self.userRepository.get_or_401(user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if property.owner_id != user_id:
            raise exceptions.Unauthorized

        return await self.propertyRepository.delete_property(
            property_id, sold)

    async def update_property(
            self,
            property_id: int,
            payload: dict,
            user_id: int,
            ) -> Property:
        """Update property"""
        user = await self.userRepository.get_or_401(user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if user.level < 1 and property.owner_id != user_id:
            raise exceptions.Unauthorized

        return await self.propertyRepository.update_property(
            property_id, payload)

    async def add_image_to_property(
            self,
            property_id: int,
            image: UploadFile,
            user_id: int
            ) -> Property:
        """Add image to property"""
        user = await self.userRepository.get_or_401(user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if user.level < 1 and property.owner_id != user_id:
            raise exceptions.Unauthorized

        return await self.propertyRepository.add_image_to_property(
            property_id, image)

    async def delete_image_from_property(
            self,
            property_id: int,
            image_id: int,
            user_id: int,
            ) -> Property:
        """Delete property image"""
        user = await self.userRepository.get_or_401(user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if user.level < 1 and property.owner_id != user_id:
            raise exceptions.Unauthorized

        return await self.propertyRepository.delete_image_from_property(
            property_id, image_id)
