"""Module with property repository"""
from dataclasses import dataclass

from sqlalchemy import select

from app.base.repository import BaseRepository
from app.staticfiles.manager import BaseStaticFilesManager
from app.property.models import Property, PropertyLike, PropertyImage
from app.property import exceptions
from app.auth import exceptions as auth_exceptions

@dataclass
class PropertyRepository(BaseRepository[Property]):
    """Property repository"""

    staticFilesManager: BaseStaticFilesManager

    async def get_property_by(self, **kwargs) -> Property:
        """Get property by any field"""
        result = await self.session.execute(select(Property).filter_by(**kwargs))
        return result.scalars().first()
    
    async def get_like_by(self, **kwargs) -> PropertyLike:
        """Get like by any field"""
        result = await self.session.execute(select(PropertyLike).filter_by(**kwargs))
        return result.scalars().first()

    async def get_or_404(self, property_id: int) -> Property:
        """Get property by id or raise 404"""
        result = await self.session.execute(select(Property).filter(Property.id == property_id))
        property_obj = result.scalars().first()
        if not property_obj:
            raise exceptions.PropertyNotFound
        return property_obj

    async def get_properties_page(self, limit: int, offset: int) -> list[Property]:
        """Get properties page"""
        result = await self.session.execute(select(Property).limit(limit).offset(offset))
        return result.scalars().all()

    async def get_properties_count(self) -> int:
        """Get properties count"""
        result = await self.session.execute(select(Property).count())
        return result.scalar()
    
    async def get_property_likes(self, property_id: int) -> list[dict]:
        """Get property likes"""
        result = await self.session.execute(select(PropertyLike).filter(PropertyLike.property_id == property_id))
        return result.scalars().all()

    async def get_property_images(self, property_id: int) -> list[PropertyImage]:
        """Get property images"""
        pass

    async def get_property_image(self, image_id: int) -> dict:
        """Get property image"""
        pass
    
    async def create_property(self, payload: dict, images: list[dict], user_id: int) -> Property:
        """Create property"""
        pass

    async def add_image_to_property(self, property_id: int, image: dict, user_id: int) -> Property:
        """Add image to property"""
        pass

    async def update_property(self, property_id: int, payload: dict, user_id: int) -> Property:
        """Update property"""
        pass

    async def like_property(self, property_id: int, user_id: int) -> Property:
        """Like property"""
        like = PropertyLike(property_id=property_id, user_id=user_id)
        self.add(like)
        await self.commit()
        return await self.get_or_404(property_id)

    async def delete_image_from_property(self, property_id: int, image_id: int, user_id: int) -> Property:
        """Delete image from property"""
        image: PropertyImage = await self.get_property_image(image_id)
        if image["property_id"] != property_id:
            raise exceptions.PropertyNotFound
        if image["user_id"] != user_id:
            raise auth_exceptions.Unauthorized
        await self.staticFilesManager.delete(image.path)
        await self.delete(image_id)
        await self.commit()

    async def delete_property(self, property_id: int) -> None:
        """Delete property
        
        TO DO: can be optimized by sending to celery task
        """
        property = await self.get_or_404(property_id)
        images = await self.get_property_images(property_id)
        for image in images:
            await self.staticFilesManager.delete(image.path)
            await self.delete(image)
        await self.delete(property)
        await self.commit()

    async def unlike_property(self, property_id: int, user_id: int) -> None:
        """Unlike property"""
        like = self.get_like_by(property_id=property_id, user_id=user_id)
        self.delete(like)
        await self.commit()

    async def approve_property(self, property_id: int) -> Property:
        """Approve property"""
        property_obj: Property = await self.get_or_404(property_id)
        property_obj.approve()
        await self.session.commit()
        return property_obj
