"""Module with property repository"""
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from fastapi import UploadFile

from src.base.repository import BaseRepository
from src.staticfiles.manager import BaseStaticFilesManager
from src.property.models import (Property, PropertyImage,
                                 PropertyInfo, PropertyLocation,
                                 PropertyBuilding, PropertyLike)
from src.user.models import Approval, User
from src.property import exceptions
from src.property.schemas import CreatePropertySchema, MapSearchSchema
from src.listing.schemas import CreateListingSchema
from src.listing.models import Listing, ListingImage
from src.celery.tasks import queue_delete_property

@dataclass
class PropertyRepository(BaseRepository[Property]):
    """Property repository"""

    staticFilesManager: BaseStaticFilesManager

    def _get_filter_conditions(
            self,
            filters: list[tuple]
        ) -> list:
        filter_conditions = [
            Property.is_active == True,
            Property.is_sold == False,
            Property.approved == True,
        ]

        operator_mapping = {
            ">=": "__ge__",
            "<=": "__le__",
            "==": "__eq__",
        }

        for value, attr_path, op in filters:
            if "." in attr_path:
                base_attr, related_attr = attr_path.split(".")
                attr = getattr(getattr(Property, base_attr).property.mapper.class_, related_attr)
            else:
                attr = getattr(Property, attr_path)
            filter_conditions.append(getattr(attr, operator_mapping[op])(value))

        return filter_conditions

    async def get_map_locations(
            self,
            filters: list[tuple],
    ) -> Sequence[PropertyLocation]:
        """Get map locations"""
        filter_conditions = self._get_filter_conditions(filters)

        result = await self.session.execute(
            select(Property.id, PropertyLocation.latitude, PropertyLocation.longitude).
            options(
            joinedload(Property.owner),
            joinedload(Property.images),
            joinedload(Property.location),
            joinedload(Property.info)
            ).filter(
                and_(
                    *filter_conditions
                    )
                ).order_by(
                    Property.created_at.desc()
                )
        )
        return result.scalars().unique().all()

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
                    PropertyLocation.latitude == latitude,
                    PropertyLocation.longitude == longitude,
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
    
    async def get_listings_page(
            self,
            limit: int,
            offset: int,
            ) -> Sequence[Listing]:
        """Get listings page"""
        subquery = (
            select(Listing.id)
            .join(Listing.properties)
            .group_by(Listing.id)
            .having(func.count(Property.id) > 0)
            .subquery()
        )

        result = await self.session.execute(
            select(Listing)
            .options(
                joinedload(Listing.agent),
                joinedload(Listing.properties)
                .options(
                    joinedload(Property.location),
                    joinedload(Property.info),
                    joinedload(Property.images)
                ),
                joinedload(Listing.images)
            )
            .filter(Listing.id.in_(subquery))
            .order_by(Listing.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return result.scalars().all()

    async def get_listings_count(
            self,
            ) -> int:
        """Get listings count"""
        subquery = (
            select(Listing.id)
            .join(Listing.properties)
            .group_by(Listing.id)
            .having(func.count(Property.id) > 0)
            .subquery()
        )

        result = await self.session.execute(
            select(func.count(Listing.id))
            .filter(Listing.id.in_(subquery))
        )

        return result.scalar()

    async def get_listing(
            self,
            listing_id: int,
            ) -> Listing:
        """Get listing by id"""
        result = await self.session.execute(
            select(Listing)
            .options(
                joinedload(Listing.agent),
                joinedload(Listing.properties)
                .options(
                    joinedload(Property.location),
                    joinedload(Property.info),
                    joinedload(Property.images)
                ),
                joinedload(Listing.images)
            )
            .filter(Listing.id == listing_id)
        )
        listing = result.scalars().first()
        return listing

    async def get_listing_or_404(
            self,
            listing_id: int,
            ) -> Listing:
        """Get listing by id or raise 404"""
        result = await self.session.execute(
            select(Listing)
            .filter(Listing.id == listing_id)
        )
        listing = result.scalars().first()
        if not listing:
            raise exceptions.ListingNotFound
        return listing
    
    async def get_listing_join_property(
            self,
            **kwargs,
            ) -> Listing:
        """Get listing by any field"""
        result = await self.session.execute(
            select(Listing)
            .options(
                joinedload(Listing.agent),
                joinedload(Listing.properties)
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
            filters: list[tuple],
            ) -> Sequence[Property]:
        """Get properties page"""
        filter_conditions = [
            Property.is_active == True,
            Property.is_sold == False,
            Property.approved == True,
        ]

        operator_mapping = {
            ">=": "__ge__",
            "<=": "__le__",
            "==": "__eq__",
        }

        for value, attr_path, op in filters:
            if "." in attr_path:
                base_attr, related_attr = attr_path.split(".")
                attr = getattr(getattr(Property, base_attr).property.mapper.class_, related_attr)
            else:
                attr = getattr(Property, attr_path)
            filter_conditions.append(getattr(attr, operator_mapping[op])(value))


        result = await self.session.execute(
            select(Property).
            options(
            joinedload(Property.owner),
            joinedload(Property.images),
            joinedload(Property.location),
            joinedload(Property.info)
            ).filter(
                and_(
                    *filter_conditions
                    )
                ).order_by(
                    Property.created_at.desc()
                ).limit(limit).offset(offset)
        )
        return result.scalars().unique().all()

    async def get_my_listings(
            self,
            agent_id: int):
        result = await self.session.execute(
            select(Listing)
            .options(
                joinedload(Listing.agent),
                joinedload(Listing.properties)
                .options(
                    joinedload(Property.location),
                    joinedload(Property.info),
                    joinedload(Property.images)
                ),
                joinedload(Listing.images)
            )
            .filter(Listing.agent_id == agent_id)
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
            )
            .filter_by(**kwargs)
            .order_by(
                Property.created_at.desc()
            )
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().unique().all()

    async def get_properties_page_by_count(
            self,
            **kwargs,
            ) -> int:
        """Get properties page count"""
        result = await self.session.execute(
            select(func.count(Property.id)).
            filter_by(
                is_active = True, 
                is_sold = False,
                approved = True,
                **kwargs
            )
        )
        return result.scalar()

    async def count_property_images(self, property_id: int) -> int:
        """Count the number of images for a property"""
        result = await self.session.execute(
            select(func.count(PropertyImage.id))
            .filter(PropertyImage.property_id == property_id)
        )
        return result.scalar()
    
    async def count_listing_images(self, listing_id: int) -> int:
        """Count the number of images for a listing"""
        result = await self.session.execute(
            select(func.count(ListingImage.id))
            .filter(ListingImage.listing_id == listing_id)
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

    async def _get_listing_image(
            self,
            image_id: int,
            ) -> ListingImage:
        """Get listing image by id"""
        result = await self.session.execute(
        select(ListingImage).filter(
            ListingImage.id == image_id
            )
        )
        image = result.scalars().first()
        if not image:
            raise exceptions.ListingImageNotFound
        return image
    
    async def get_like(
            self, user_id: int, property_id: int
        ) -> bool:
        """Get like"""
        result = await self.session.execute(
            select(PropertyLike).filter_by(
                user_id=user_id,
                property_id=property_id,
                ))
        return bool(result.scalars().first())

    async def get_favorites_page(
            self,
            user_id: int,
            limit: int,
            offset: int,
            ) -> Sequence[Property]:
        """Get favorites page"""
        result = await self.session.execute(
            select(Property)
            .join(Property.likes)
            .filter(
                PropertyLike.user_id == user_id
            )
            .order_by(PropertyLike.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all() 
    
    async def create_listing(
            self,
            schema: CreateListingSchema,
            images: list[UploadFile],
            agent_id: int,
            ) -> Property:
        """Create listing"""
        listing = Listing(
            name=schema.name,
            description=schema.description,
            # district=schema.district,
            # address=schema.address,
            agent_id=agent_id
        )

        self.add(listing)
        await self.commit()
        await self.refresh(listing)
        await self._add_images_to_listing(listing, images)
        await self.commit()
        return listing
    
    async def add_images_to_listing(
            self,
            listing: Listing,
            images: list[UploadFile]
            ) -> Listing:
        """Add images to listing"""
        await self._add_images_to_listing(listing, images)
        await self.commit()
        return listing
    
    async def _add_images_to_listing(
            self,
            listing: Listing,
            images: list[UploadFile]
            ) -> None:
        """Add images to listing"""
        for image in images:
            path = await self.staticFilesManager.upload(image)
            listing_image = ListingImage(
                listing_id=listing.id,
                image_url=path
            )
            self.add(listing_image)

    async def update_listing(
            self,
            listing_id: int,
            payload: dict,
            ) -> Listing:
        """Update listing"""
        listing = await self.get_listing_or_404(listing_id)
        for key, value in payload.items():
            setattr(listing, key, value)
        await self.commit()
        return listing

    async def delete_image_from_listing(
            self,
            image_id: int,
            ) -> None:
        """Delete image from listing"""
        image = await self._get_listing_image(image_id)
        self.staticFilesManager.delete(image.image_url)
        await self.delete(image)
        await self.commit()

    async def delete_listing(
            self,
            listing_id: int,
            ) -> None:
        """Delete listing"""
        listing = await self.get_listing_join_property(listing_id)
        self._deactivate_listing(listing)
        await self.commit()
        queue_delete_property.delay(listing_id)

    async def _deactivate_listing(
            self,
            listing: Listing,
            ) -> None:
        """Deactivate listing"""
        listing.deactivate()
        for property in listing.properties:
            property.deactivate()

    async def create_property(
            self,
            schema: CreatePropertySchema,
            images: list[UploadFile],
            agent_id: int,
            ) -> Property:
        """Create property"""
        property_obj = Property(
            name=schema.name,
            description=schema.description,
            price=schema.price,
            location=PropertyLocation(
                latitude=schema.latitude,
                longitude=schema.longitude
                ),
            info=PropertyInfo(
                category=schema.category,
                total_area=schema.total_area,
                living_area=schema.living_area,
                apartment_area=schema.apartment_area,
                kitchen_area=schema.kitchen_area,
                rooms=schema.rooms,
                bathrooms=schema.bathrooms,
                living_rooms=schema.living_rooms,
                floor=schema.floor,
                floors=schema.floors,
                district=schema.district,
                address=schema.address,
                balcony=schema.balcony,
                view=schema.view
            ),
            building=PropertyBuilding(
                year_built=schema.year_built,
                building_type=schema.building_type,
                elevators=schema.elevators,
                parking=schema.parking,
                flooring_type=schema.flooring_type
            ),
            owner_id=agent_id)

        self.add(property_obj)
        await self.commit()
        await self.refresh(property_obj)
        await self._add_images_to_property(property_obj, images)
        await self.commit()
        return property_obj

    async def add_images_to_property(
            self,
            property: Property,
            images: list[UploadFile]
            ) -> Property:
        """Add image to property"""
        await self._add_images_to_property(property, images)
        await self.commit()
    
    async def _add_images_to_property(
            self,
            property: Property,
            images: list[UploadFile]
            ) -> None:
        """Add image to property"""
        for image in images:
            path = await self.staticFilesManager.upload(image)
            property_image = PropertyImage(
                property_id=property.id,
                image_url=path
                )
            self.add(property_image)

    async def update_property(
            self,
            property_id: int,
            payload: dict,
            ) -> Property:
        """Update property"""
        property_obj = await self.get_or_404(property_id)
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
        self.staticFilesManager.delete(image.image_url)
        await self.delete(image)
        await self.commit()

    async def delete_property(
            self,
            property_id: int,
            is_sold: bool,
            ) -> None:
        """Delete property"""
        property = await self.get_or_404(property_id)

        property.is_sold = is_sold
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

    async def like_property(
        self,
        property_id: int,
        user_id: int,
        ) -> None:
        """Like property"""
        like = PropertyLike(
            property_id=property_id,
            user_id=user_id
        )
        self.add(like)
        await self.commit()

    async def unlike_property(
        self,
        property_id: int,
        user_id: int,
        ) -> None:
        """Unlike property"""
        await self.session.execute(
            select(PropertyLike)
            .filter(
                and_(
                    PropertyLike.property_id == property_id,
                    PropertyLike.user_id == user_id
                )
            )
            .delete()
        )
        await self.commit()
