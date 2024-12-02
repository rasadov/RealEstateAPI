"""Module with property repository"""
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from fastapi import UploadFile

from src.base.repository import BaseRepository
from src.staticfiles.manager import BaseStaticFilesManager
from src.property.models import Property, PropertyImage, PropertyInfo, Location 
from src.user.models import Approval
from src.property import exceptions
from src.property.schemas import CreatePropertySchema
from src.celery.tasks import queue_delete_property

@dataclass
class PropertyRepository(BaseRepository[Property]):
    """Property repository"""

    staticFilesManager: BaseStaticFilesManager

    async def get_map_locations(
            self,
            ) -> Sequence[Location]:
        """Get map locations"""
        result = await self.session.execute(
            select(Location).
            filter(
                and_(
                    Property.is_active == True,
                    Property.is_sold == False,
                    Property.approved == True,
                )
            )
        )
        return result.scalars().all()
    
    async def search_properties(
            self,
            query: str,
            limit: int,
            offset: int,
            ) -> Sequence[Property]:
        """Search properties"""
        result = await self.session.execute(
            select(Property).
            filter(
                and_(
                    Property.is_active == True,
                    Property.is_sold == False,
                    Property.approved == True,
                    Property.name.ilike(f"%{query}%")
                )
            ).order_by(Property.created_at.desc()).
            limit(limit).offset(offset)
        )

    async def get_at_location(
            self,
            latitude: float,
            longitude: float,
            ) -> Sequence[Property]:
        """Returns all properties at a location"""
        result = await self.session.execute(
            select(Property).
            join(Property.location).
            filter(
                and_(
                    Property.is_active == True,
                    Property.is_sold == False,
                    Property.approved == True,
                    Location.latitude == latitude,
                    Location.longitude == longitude,
                )                
            )
        )
        return result.scalars().all()

    async def get_property_by(
            self,
            **kwargs,
            ) -> Property:
        """Get property by any field"""
        result = await self.session.execute(
            select(Property)
            .options(
                joinedload(Property.owner),
                joinedload(Property.location),
                joinedload(Property.images),
                joinedload(Property.info)
            )
            .filter_by(**kwargs))
        return result.scalars().first()

    async def get_approvals_page(
            self,
            limit: int,
            offset: int,
            ) -> Sequence[Approval]:
        """Get approvals page"""
        result = await self.session.execute(
            select(Approval).
            order_by(Approval.created_at.desc()).
            limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_sold_properties_page(
            self,
            limit: int,
            offset: int,
            ) -> Sequence[Property]:
        """Get sold properties page"""
        result = await self.session.execute(
            select(Property).
            filter(Property.is_sold == True).
            order_by(Property.created_at.desc()).
            limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_properties_page(
            self,
            limit: int,
            offset: int,
            ) -> Sequence[Property]:
        """Get properties page"""
        result = await self.session.execute(
            select(Property).
            filter(
                and_(
                    Property.is_active == True,
                    Property.is_sold == False,
                    Property.approved == True,
                    )
                ).order_by(
                    Property.created_at.desc()
                ).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_properties_page_by(
            self,
            limit: int,
            offset: int,
            **kwargs,
            ) -> Sequence[Property]:
        """Get properties page"""
        result = await self.session.execute(
            select(Property).
            options(
            joinedload(Property.owner),
            joinedload(Property.images),
            joinedload(Property.location),
            joinedload(Property.info)
            ).
            filter(**kwargs).
            order_by(Property.created_at.desc()).
            limit(limit).offset(offset)
        )
        return result.scalars().unique().all()

    async def get_properties_page_by_count(
            self,
            **kwargs,
            ) -> int:
        """Get properties page count"""
        result = await self.session.execute(
            select(func.count(Property.id)).
            filter(
                and_(
                Property.is_active == True, 
                Property.is_sold == False,
                Property.approved == True,
                **kwargs
                )
            )
        )
        return result.scalar()

    async def count_images(self, property_id: int) -> int:
        """Count the number of images for a property"""
        result = await self.session.execute(
            select(func.count(PropertyImage.id))
            .filter(PropertyImage.property_id == property_id)
        )
        return result.scalar()

    async def get_or_404(
            self,
            property_id: int,
            ) -> Property:
        """Get property by id or raise 404"""
        result = await self.session.execute(
            select(Property)
            .options(
                joinedload(Property.owner),
                joinedload(Property.location),
                joinedload(Property.images),
                joinedload(Property.info)
            )
            .filter(Property.id == property_id)
        )
        property_obj = result.scalars().first()
        if not property_obj:
            raise exceptions.PropertyNotFound
        return property_obj

    async def get_properties_count(
            self,
            ) -> int:
        """Get properties count"""
        result = await self.session.execute(
            select(func.count(Property.id)))
        return result.scalar()

    async def _get_property_image(
            self,
            image_id: int,
            ) -> PropertyImage:
        """Get property image by id"""
        result = await self.session.execute(
        select(PropertyImage).filter(
            PropertyImage.id == image_id
            )
        )
        image = result.scalars().first()
        if not image:
            raise exceptions.PropertyImageNotFound
        return image

    async def create_property(
            self,
            payload: CreatePropertySchema,
            images: list[UploadFile],
            agent_id: int,
            ) -> Property:
        """Create property"""
        property_obj = Property(
            name=payload.name,
            description=payload.description,
            price=payload.price,
            location=Location(
                latitude=payload.latitude,
                longitude=payload.longitude
                ),
            info=PropertyInfo(
                category=payload.category,
                total_area=payload.total_area,
                living_area=payload.living_area,
                bedrooms=payload.bedrooms,
                living_rooms=payload.living_rooms,
                floor=payload.floor,
                floors=payload.floors,
                district=payload.district,
                address=payload.address
            ),
            owner_id=agent_id)

        self.add(property_obj)
        await self.commit()
        await self.refresh(property_obj)

        for image in images:
            path = await self.staticFilesManager.upload(image)
            property_image = PropertyImage(
                property_id=property_obj.id,
                image_url=path
                )
            self.add(property_image)

        await self.commit()
        return property_obj

    async def add_images_to_property(
            self,
            property_id: int,
            images: list[UploadFile]
            ) -> Property:
        """Add image to property"""
        property_obj = await self.get_or_404(property_id)

        for image in images:
            path = await self.staticFilesManager.upload(image)
            property_image = PropertyImage(
                property_id=property_obj.id,
                image_url=path
                )
            self.add(property_image)
        await self.commit()
        return property_obj

    async def update_property(
            self,
            property_id: int,
            payload: dict,
            ) -> Property:
        """Update property"""
        property_obj = await self.get_or_404(property_id)
        print(payload)
        print(property_obj)
        print(property_obj.info)
        print(property_obj.location)
        print(property_obj.owner)
        print(property_obj.images)
        for key, value in payload.items():
            if type(value) is dict:
                for k, v in value.items():
                    setattr(getattr(property_obj, key), k, v)
            else:
                setattr(property_obj, key, value)
        await self.commit()
        return property_obj

    async def approve_property(
            self,
            property_id: int,
            ) -> Property:
        """Approve property"""
        property_obj = await self.get_or_404(property_id)
        property_obj.approve()
        await self.session.commit()
        return property_obj

    async def delete_image_from_property(
            self,
            image_id: int,
            ) -> None:
        """Delete image from property"""
        image = await self._get_property_image(image_id)
        await self.staticFilesManager.delete(image.image_url)
        self.delete(image_id)
        await self.commit()

    async def delete_property(
            self,
            property_id: int,
            sold: bool,
            ) -> None:
        """Delete property"""
        property = await self.get_or_404(property_id)

        if sold:
            property.is_sold = True
        await self.commit()

        queue_delete_property.delay(property_id)

    async def admin_delete_property(
            self,
            prop: Property,
            ) -> None:
        """Delete property"""
        prop.deactivate()
        await self.commit()
        queue_delete_property.delay(prop.id)
