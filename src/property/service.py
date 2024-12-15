from dataclasses import dataclass
from typing import Sequence

from fastapi import UploadFile

from src.property.repository import PropertyRepository
from src.user.repository import UserRepository
from src.auth import exceptions as auth_exceptions
from src.property.models import Property, Listing, Location
from src.property.schemas import CreatePropertySchema, CreateListingSchema, SearchPropertySchema
from src.auth.schemas import TokenData
from src.property import exceptions

@dataclass
class PropertyService:
    """Property service"""

    property_repository: PropertyRepository
    user_repository: UserRepository

    async def get_property_by_id(
            self,
            id: int,
            current_user: TokenData,
            ) -> Property:
        """Get property by id"""
        prop = await self.property_repository.get_or_404(id)
        available = False in (prop.is_active, prop.is_sold, prop.approved)
        if not available:
            if current_user:
                user = await self.user_repository.get_or_401(current_user.user_id)
                if user.agent and user.agent.id == prop.owner_id:
                    return prop
            raise auth_exceptions.Unauthorized
        return prop

    async def get_properties_page(
            self,
            schema: SearchPropertySchema,
            ) -> dict[str, int | Sequence]:
        """Get properties page"""
        offset = (schema.page - 1) * schema.elements
        filters = schema.get_filters()

        properties = await self.property_repository.get_properties_page(
            schema.elements, offset, filters)
        count = await self.property_repository.get_properties_count()
        total_pages = (count - 1) // schema.elements + 1
        return {
            "properties": properties,
            "total_pages": total_pages,
        }

    async def get_properties_by_agent_page(
            self,
            agent_id: int,
            page: int,
            elements: int,
            ) -> dict[str, int | Sequence]:
        """Get properties by agent page"""
        offset = (page - 1) * elements
        properties = await self.property_repository.get_properties_page_by(
            limit=elements, offset=offset, owner_id=agent_id)
        count = await self.property_repository.get_properties_page_by_count(
            owner_id=agent_id)
        total_pages = (count - 1) // elements + 1
        return {
            "properties": properties,
            "total_pages": total_pages,
        }

    async def get_map_locations(
            self,
            ) -> Sequence[Location]:
        """Get map locations"""
        return await self.property_repository.get_map_locations()
    
    async def get_at_location(
            self,
            latitude: float,
            longitude: float,
            ) -> Sequence[Property]:
        """Returns all properties at a location"""
        return await self.property_repository.get_at_location(
            latitude, longitude)

    async def get_listing_by_id(
            self,
            id: int,
            ) -> Listing:
        """Get listing by id"""
        listing = await self.property_repository.get_listing(id)

        if not listing:
            raise exceptions.ListingNotFound
        return listing

    async def get_listings_page(
            self,
            page: int,
            elements: int,
            ) -> dict[str, int | Sequence]:
        """Get listings page"""
        offset = (page - 1) * elements

        if offset < 0:
            offset = 0

        listings = await self.property_repository.get_listings_page(
            elements, offset)
        count = await self.property_repository.get_listings_count()

        total_pages = (count - 1) // elements + 1

        return {
            "listings": listings,
            "total_pages": total_pages,
        }

    async def create_property(
            self,
            schema: CreatePropertySchema,
            images: list[UploadFile],
            user_id: int,
            ) -> Property:
        """Create property"""
        agent = await self.user_repository.get_agent_by_or_401(user_id=user_id)

        return await self.property_repository.create_property(
            schema, images, agent.id)
    
    async def create_listing(
            self,
            schema: CreateListingSchema,
            images: list[UploadFile],
            user_id: int,
            ) -> Listing:
        """Create listing"""
        agent = await self.user_repository.get_agent_by_or_401(user_id=user_id)

        return await self.property_repository.create_listing(
            schema, images, agent.id)

    async def add_images_to_property(
            self,
            property_id: int,
            images: list[UploadFile],
            user_id: int
            ) -> Property:
        """Add image to property"""
        agent = await self.user_repository.get_agent_by_or_404(user_id=user_id)
        property = await self.property_repository.get_or_404(property_id)

        if property.owner_id != agent.id:
            raise auth_exceptions.Unauthorized

        current_images = await self.property_repository.count_property_images(property_id)
        if current_images + len(images) > 15:
            raise exceptions.PropertyImagesLimitExceeded

        await self.property_repository.add_images_to_property(
            property, images)

        return property

    async def add_images_to_listing(
            self,
            listing_id: int,
            images: list[UploadFile],
            user_id: int
            ) -> Property:
        """Add image to property"""
        agent = await self.user_repository.get_agent_by_or_404(user_id=user_id)
        listing = await self.property_repository.get_listing_or_404(listing_id)

        if listing.agent_id != agent.id:
            raise auth_exceptions.Unauthorized

        current_images = await self.property_repository.count_listing_images(listing.id)
        if current_images + len(images) > 10:
            raise exceptions.ListingImagesLimitExceeded

        return await self.property_repository._add_images_to_listing(
            listing, images)

    async def update_property(
            self,
            property_id: int,
            payload: dict,
            user_id: int,
            ) -> Property:
        """Update property"""
        agent = await self.user_repository.get_agent_by_or_404(user_id=user_id)
        property = await self.property_repository.get_or_404(property_id)

        if property.owner_id != agent.id:
            raise auth_exceptions.Unauthorized

        return await self.property_repository.update_property(
            property_id, payload)
    
    async def update_listing(
            self,
            listing_id: int,
            payload: dict,
            user_id: int,
            ) -> Listing:
        """Update listing"""
        agent = await self.user_repository.get_agent_by_or_404(user_id=user_id)
        listing = await self.property_repository.get_listing_or_404(listing_id)

        if listing.agent_id != agent.id:
            raise auth_exceptions.Unauthorized

        return await self.property_repository.update_listing(
            listing_id, payload)

    async def delete_image_from_property(
            self,
            property_id: int,
            image_id: int,
            user_id: int,
            ) -> Property:
        """Delete property image"""
        agent = await self.user_repository.get_agent_by_or_404(user_id=user_id)
        property = await self.property_repository.get_or_404(property_id)

        if property.owner_id != agent.id:
            raise auth_exceptions.Unauthorized

        return await self.property_repository.delete_image_from_property(image_id)

    async def delete_property(
            self,
            property_id: int,
            user_id: int,
            is_sold: bool,
            ) -> Property:
        """Delete property"""
        agent = await self.user_repository.get_agent_by_or_404(user_id=user_id)
        property = await self.property_repository.get_or_404(property_id)

        if property.owner_id != agent.id:
            raise auth_exceptions.Unauthorized

        return await self.property_repository.delete_property(
            property_id, is_sold)

    async def delete_image_from_listing(
            self,
            listing_id: int,
            image_id: int,
            user_id: int,
            ) -> Listing:
        """Delete listing image"""
        agent = await self.user_repository.get_agent_by_or_404(user_id=user_id)
        listing = await self.property_repository.get_listing_or_404(listing_id)

        if listing.agent_id != agent.id:
            raise auth_exceptions.Unauthorized
        
        return await self.property_repository.delete_image_from_listing(image_id)
    
    async def delete_listing(
            self,
            listing_id: int,
            user_id: int,
            ) -> Listing:
        """Delete listing"""
        agent = await self.user_repository.get_agent_by_or_404(user_id=user_id)
        listing = await self.property_repository.get_listing_or_404(listing_id)

        if listing.agent_id != agent.id:
            raise auth_exceptions.Unauthorized

        return await self.property_repository.delete_listing(listing_id)
