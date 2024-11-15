"""Module with property repository"""
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from fastapi import UploadFile

from src.base.repository import BaseRepository
from src.staticfiles.manager import BaseStaticFilesManager
from src.property.models import Property, PropertyLike, PropertyImage, SoldProperty
from src.property import exceptions
from src.background_tasks.tasks import delete_property

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
        result = await self.session.execute(
            select(Property).filter(
                Property.id == property_id,
                Property.is_active == True
                )
            )
        property_obj = result.scalars().first()
        if not property_obj:
            raise exceptions.PropertyNotFound
        return property_obj

    async def get_properties_page(self, limit: int, offset: int) -> list[Property]:
        """Get properties page"""
        result = await self.session.execute(
            select(Property).
            filter(Property.is_active == True).
            order_by(Property.created_at.desc()).
            limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_properties_count(self) -> int:
        """Get properties count"""
        result = await self.session.execute(select(Property).count())
        return result.scalar()

    async def get_property_likes(self, property_id: int) -> list[PropertyLike]:
        """Get property likes"""
        result = await self.session.execute(
            select(PropertyLike).filter(PropertyLike.property_id == property_id)
            )
        return result.scalars().all()

    async def _get_property_image(self, image_id: int) -> PropertyImage:
        """Get property image by id"""
        result = await self.session.execute(
            select(PropertyImage).filter(PropertyImage.id == image_id)
            )
        image = result.scalars().first()
        if not image:
            raise exceptions.PropertyImageNotFound
        return image

    async def create_property(self, payload: dict, images: list[UploadFile], user_id: int) -> Property:
        """Create property"""
        property_obj = Property(**payload, owner_id=user_id)
        self.add(property_obj)
        await self.commit()
        for image in images:
            self.staticFilesManager.upload(image)
            property_image = PropertyImage(property_id=property_obj.id, **image)
            self.add(property_image)
        await self.commit()
        return property_obj

    async def add_image_to_property(self, property_id: int, image: UploadFile) -> Property:
        """Add image to property"""
        property_obj = await self.get_or_404(property_id)
        path = self.staticFilesManager.upload(image)
        property_image = PropertyImage(property_id=property_id, path=path)
        self.add(property_image)
        await self.commit()
        return property_obj

    async def update_property(self, property_id: int, payload: dict) -> Property:
        """Update property"""
        property_obj = await self.get_or_404(property_id)
        for key, value in payload.items():
            setattr(property_obj, key, value)
        await self.commit()
        return property_obj

    async def like_property(self, property_id: int, user_id: int) -> Property:
        """Like property"""
        like = PropertyLike(property_id=property_id, user_id=user_id)
        self.add(like)
        await self.commit()
        return await self.get_or_404(property_id)

    async def delete_image_from_property(self, image_id: int) -> Property:
        """Delete image from property"""
        image: PropertyImage = await self._get_property_image(image_id)
        await self.staticFilesManager.delete(image.path)
        await self.delete(image_id)
        await self.commit()

    async def delete_property(self, property_id: int, sold: bool) -> None:
        """Delete property"""
        property = await self.get_or_404(property_id)

        if sold:
            sold_property = SoldProperty(
                property_id=property.id,
                price=property.price,
                district=property.district,
                longitude=property.longitude,
                latitude=property.latitude,
            )
            self.add(sold_property)        
        property.deactivate()
        await self.commit()

        delete_property.delay(property_id)

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
