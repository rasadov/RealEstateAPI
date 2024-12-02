from dataclasses import dataclass
from typing import Dict, Any, Sequence

from fastapi import UploadFile

from src.property.repository import PropertyRepository
from src.user.repository import UserRepository
from src.auth import exceptions as auth_exceptions
from src.property.models import Property, Location
from src.property.schemas import CreatePropertySchema
from src.auth.schemas import TokenData
from src.property import exceptions

@dataclass
class PropertyService:
    """Property service"""

    propertyRepository: PropertyRepository
    userRepository: UserRepository

    async def get_property_by_id(
            self,
            id: int,
            current_user: TokenData,
            ) -> Property:
        """Get property by id"""
        prop = await self.propertyRepository.get_or_404(id)
        available = False in (prop.is_active, prop.is_sold, prop.approved)
        if not available:
            if current_user:
                user = await self.userRepository.get_or_401(current_user.user_id)
                if (
                    user.level > 0 or
                    (user.agent and user.agent.id == prop.owner_id)
                    ):
                    return prop
            raise auth_exceptions.Unauthorized
        return prop

    async def get_properties_page(
            self,
            page: int,
            elements: int,
            ) -> Dict[str, int | Sequence]:
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

    async def get_properties_by_agent_page(
            self,
            agent_id: int,
            page: int,
            elements: int,
            ) -> Dict[str, int | Sequence]:
        """Get properties by agent page"""
        offset = (page - 1) * elements
        properties = await self.propertyRepository.get_properties_page_by(
            limit=elements, offset=offset, owner_id=agent_id)
        count = await self.propertyRepository.get_properties_page_by_count(
            owner_id=agent_id)
        total_pages = (count - 1) // elements + 1
        return {
            "properties": properties,
            "total_pages": total_pages,
        }
    
    async def search_properties(
            self,
            query: str,
            page: int,
            elements: int,
            ) -> Sequence[Property]:
        """Search properties"""
        offset = (page - 1) * elements
        return await self.propertyRepository.search_properties(
            query, elements, offset)

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
            payload: CreatePropertySchema,
            images: list[UploadFile],
            user_id: int,
            ) -> Property:
        """Create property"""
        agent = await self.userRepository.get_agent_by(
            user_id=user_id
            )

        if agent is None:
            raise auth_exceptions.Unauthorized

        return await self.propertyRepository.create_property(
            payload, images, agent.id)

    async def approve_property(
            self,
            property_id: int,
            user_id: int,
            ) -> Property:
        """Approve property"""
        user = await self.userRepository.get_or_401(user_id)

        if user.level < 1:
            raise auth_exceptions.Unauthorized

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
            raise auth_exceptions.Unauthorized

        return await self.propertyRepository.delete_property(
            property_id, sold)

    async def update_property(
            self,
            property_id: int,
            payload: dict,
            user_id: int,
            ) -> Property:
        """Update property"""
        agent = await self.userRepository.get_agent_by(user_id=user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if agent.user.level < 1 and property.owner_id != agent.id:
            raise auth_exceptions.Unauthorized

        return await self.propertyRepository.update_property(
            property_id, payload)

    async def add_images_to_property(
            self,
            property_id: int,
            images: list[UploadFile],
            user_id: int
            ) -> Property:
        """Add image to property"""
        agent = await self.userRepository.get_agent_by(user_id=user_id)
        property = await self.propertyRepository.get_or_404(property_id)

        if agent.user.level < 1 and property.owner_id != agent.id:
            raise auth_exceptions.Unauthorized

        current_images = await self.propertyRepository.count_images(property_id)
        if current_images + len(images) > 15:
            raise exceptions.PropertyImagesLimitExceeded

        return await self.propertyRepository.add_images_to_property(
            property_id, images)

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
            raise auth_exceptions.Unauthorized

        return await self.propertyRepository.delete_image_from_property(
            property_id, image_id)
