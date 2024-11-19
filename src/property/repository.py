"""Module with property repository"""
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import func
from sqlalchemy.future import select
from fastapi import UploadFile

from src.base.repository import BaseRepository
from src.staticfiles.manager import BaseStaticFilesManager
from src.property.models import Property, PropertyImage, Location
from src.user.models import Approval
from src.property import exceptions
from src.background_tasks.tasks import delete_property_images

@dataclass
class PropertyRepository(BaseRepository[Property]):
    """Property repository"""

    staticFilesManager: BaseStaticFilesManager

    async def get_map_locations(self) -> Sequence[Location]:
        """Get map locations"""
        result = await self.session.execute(
            select(Location).
            filter(Location.is_active == True)
        )
        return result.scalars().all()

    async def get_property_by(self, **kwargs) -> Property:
        """Get property by any field"""
        result = await self.session.execute(select(Property).filter_by(**kwargs))
        return result.scalars().first()

    async def get_approvals_page(self, limit: int, offset: int) -> Sequence[Approval]:
        """Get approvals page"""
        result = await self.session.execute(
            select(Approval).
            order_by(Approval.created_at.desc()).
            limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def get_sold_properties_page(self, limit: int, offset: int) -> Sequence[Property]:
        """Get sold properties page"""
        result = await self.session.execute(
            select(Property).
            filter(Property.is_sold == True).
            order_by(Property.created_at.desc()).
            limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_properties_page(self, limit: int, offset: int) -> Sequence[Property]:
        """Get properties page"""
        result = await self.session.execute(
            select(Property).
            filter(Property.is_active == True and Property.is_sold == False).
            order_by(Property.created_at.desc()).
            limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_properties_page_by(self, limit: int, offset: int, **kwargs) -> Sequence[Property]:
        """Get properties page"""
        result = await self.session.execute(
            select(Property).
            filter_by(**kwargs).
            order_by(Property.created_at.desc()).
            limit(limit).offset(offset)
        )
        return result.scalars().all()
    
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

    async def get_properties_count(self) -> int:
        """Get properties count"""
        result = await self.session.execute(select(func.count(Property.id)))
        return result.scalar()

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
            path = self.staticFilesManager.upload(image)
            property_image = PropertyImage(property_id=property_obj.id, path=path)
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
    
    async def approve_property(self, property_id: int) -> Property:
        """Approve property"""
        property_obj: Property = await self.get_or_404(property_id)
        property_obj.approve()
        await self.session.commit()
        return property_obj

    async def delete_image_from_property(self, image_id: int) -> None:
        """Delete image from property"""
        image: PropertyImage = await self._get_property_image(image_id)
        await self.staticFilesManager.delete(image.path)
        await self.delete(image_id)
        await self.commit()

    async def delete_property(self, property_id: int, sold: bool) -> None:
        """Delete property"""
        property = await self.get_or_404(property_id)

        if sold:
            property.is_sold = True
        await self.commit()

        delete_property_images.delay(property_id)

    async def admin_delete_property(self, property_id: int) -> None:
        """Delete property"""
        await self.get_or_404(property_id)
        await self.delete(property_id)
        await self.commit()
        delete_property_images.delay(property_id)
