"""Module with property repository"""
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import func, and_, delete, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from fastapi import UploadFile

from src.base.repository import BaseRepository
from src.staticfiles.manager import BaseStaticFilesManager
from src.property.models import (Property, PropertyImage,
                                 PropertyInfo, PropertyLocation,
                                 PropertyBuilding, PropertyLike,
                                 PropertyDocument)
from src.user.models import Approval, User, Agent
from src.property import exceptions
from src.listing import exceptions as listing_exceptions
from src.property.schemas import CreatePropertySchema, MapSearchSchema
from src.listing.schemas import CreateListingSchema
from src.listing.models import Listing, ListingImage
from src.celery.tasks import queue_delete_property

@dataclass
class PropertyRepository(BaseRepository[Property]):
    """Property repository"""

    staticFilesManager: BaseStaticFilesManager

    @staticmethod
    def _get_filter_conditions(filters: list[tuple]) -> list:

        filter_conditions = [
            Property.is_active == True,
            Property.is_sold == False,
            Property.approved == True,
        ]

        operator_mapping = {
            ">=": "__ge__",
            "<=": "__le__",
            "==": "__eq__",
            "in": "in_",
        }

        for value, attr_path, op in filters:
            if attr_path == "room_number":
                or_conditions = []
                for single_bedroom_count in value:
                    # info relationship => .has() on a related column
                    cond = Property.info.has(PropertyInfo.bedrooms == single_bedroom_count)
                    or_conditions.append(cond)

                # Combine them with an OR
                filter_conditions.append(or_(*or_conditions))
            elif attr_path == "info.floor":
                if value == "NotLastFloor":
                    filter_conditions.append(Property.info.has(PropertyInfo.floor < PropertyInfo.floors))
                elif value == "LastFloor":
                    filter_conditions.append(Property.info.has(PropertyInfo.floor == PropertyInfo.floors))
                elif value == "NotFirstFloor":
                    filter_conditions.append(Property.info.has(PropertyInfo.floor != 1))
                else:
                    base_attr, related_attr = attr_path.split(".")
                    print("BASE", base_attr, "RELATED", related_attr)
                    print("BASE", getattr(Property, base_attr))
                    print("RELATED", getattr(Property, base_attr).property.mapper.class_)
                    attr = getattr(
                        getattr(Property, base_attr).property.mapper.class_,
                        related_attr
                    )
                    filter_conditions.append(
                        getattr(attr, operator_mapping[op])(value)
                    )
            else:
                if "." in attr_path:
                    #print("HERE ", getattr(Property, attr_path))
                    base_attr, related_attr = attr_path.split(".")
                    print("BASE", base_attr, "RELATED", related_attr)
                    print("BASE", getattr(Property, base_attr))
                    print("RELATED", getattr(Property, base_attr).property.mapper.class_)
                    attr = getattr(
                        getattr(Property, base_attr).property.mapper.class_,
                        related_attr
                    )
                else:
                    attr = getattr(Property, attr_path)

                if op == "ilike":
                    filter_conditions.append(attr.ilike(f"%{value}%"))
                else:
                    filter_conditions.append(
                        getattr(attr, operator_mapping[op])(value)
                    )

        return filter_conditions

    async def get_map_locations(
            self,
            filters: list[tuple],
    ) -> Sequence[PropertyLocation]:
        """
        Get map locations from PropertyLocation.
        Joins Property to apply filters, but doesn't select everything.
        """
        # Convert your filter list into valid SQLAlchemy conditions
        filter_conditions = PropertyRepository._get_filter_conditions(filters)
        stmt = (
            select(PropertyLocation)
            # If you have a relationship from PropertyLocation to Property
            .join(PropertyLocation.property)
            # then from Property to PropertyInfo, if needed
            .join(Property.info)
            .join(Property.building)
            .where(and_(*filter_conditions))
            .order_by(Property.created_at.desc())
        )

        # Execute the statement
        result = await self.session.execute(stmt)

        # Return unique location objects
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
        # subquery = (
        #     select(Listing.id)
        #     .filter
        # )

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
            .filter_by(
                is_active = True,
            )
            .order_by(Listing.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return result.scalars().unique().all()

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
            raise listing_exceptions.ListingNotFound
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
        filter_conditions = PropertyRepository._get_filter_conditions(filters)
        print(filter_conditions)

        result = await self.session.execute(
            select(Property)
            # Explicitly join or outerjoin the relationships you want to filter on
            .join(Property.info, isouter=True)
            .join(Property.location, isouter=True)
            .join(Property.building, isouter=True)
            # Then use joinedload to eagerly load data in one round trip
            .options(
                joinedload(Property.owner
                           ).joinedload(Agent.user).load_only(
                    User.name, User.id, User.phone, User.email
                ),
                joinedload(Property.listing),
                joinedload(Property.images),
                joinedload(Property.location),
                joinedload(Property.info),
            )
            .filter(
                and_(*filter_conditions)
            )
            .order_by(Property.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().unique().all()

    async def get_properties_page_admin(
            self,
            limit: int,
            offset: int,
            ) -> Sequence[Property]:
        """Get properties page"""
        print("admin")
        result = await self.session.execute(
            select(Property).
            options(
            joinedload(Property.owner)
                .lazyload(Agent.user),
            # joinedload(Property.listing),
            joinedload(Property.images),
            # joinedload(Property.location),
            joinedload(Property.info)
            ).order_by(
                Property.created_at.desc()
            ).limit(limit).offset(offset)
        )
        return result.scalars().unique().all()

    async def get_properties_count_filtered(self, filters: list[tuple]) -> int:
        """Get the number of properties matching the given filters."""
        filter_conditions = self._get_filter_conditions(filters)

        result = await self.session.execute(
            select(func.count(Property.id)).filter(
                and_(*filter_conditions)
            )
        )
        return result.scalar()

    async def get_my_listings(
            self):
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
            ).filter_by(is_active=True)
        )
        return result.scalars().unique().all()

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
                joinedload(Property.owner).
                joinedload(Agent.user).load_only(
                    User.name, User.id, User.phone, User.email
                ).
                joinedload(User.image),
                joinedload(Property.location),
                joinedload(Property.images),
                joinedload(Property.info),
                joinedload(Property.building)
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
            raise listing_exceptions.ListingImageNotFound
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
            .options(
                joinedload(Property.owner),
                joinedload(Property.images),
                joinedload(Property.location),
                joinedload(Property.info)
            )
            .filter(
                PropertyLike.user_id == user_id
            )
            .order_by(PropertyLike.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().unique().all()

    async def get_popular_properties(
            self,
            limit: int,
            offset: int,
            ) -> Sequence[Property]:
        """Get popular properties"""
        result = await self.session.execute(
            select(Property)
            .options(
                joinedload(Property.owner),
                joinedload(Property.images),
                joinedload(Property.location),
                joinedload(Property.info)
            )
            .filter(
                and_(
                    Property.is_active == True,
                    Property.is_sold == False,
                    Property.approved == True,
                )
            )
            .order_by(Property.views.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().unique().all()

    async def get_favorites_ids(
            self,
            user_id: int
    ) -> Sequence[int]:
        """Get favorites ids"""
        result = await self.session.execute(
            select(PropertyLike.property_id)
            .filter(PropertyLike.user_id == user_id)
        )

        return result.scalars().all()

    async def viewed_property(
            self,
            property_id: int,
            ) -> None:
        """Viewed property"""
        property_obj = await self.get_or_404(property_id)
        property_obj.viewed()
        await self.commit()
    
    async def create_listing(
            self,
            schema: CreateListingSchema,
            images: list[UploadFile],
            agent_id: int,
            user_id: int
            ) -> Listing:
        """Create listing"""
        listing = Listing(
            name=schema.residentialComplex,
            category=schema.category,
            description=schema.description,
            longitude=schema.longitude,
            latitude=schema.latitude,
            address=schema.address,
            building_area=schema.buildingArea,
            living_area=schema.livingArea,
            objects=schema.objects,
            year=schema.year,
            building_floors=schema.buildingFloors,
            elevators=schema.elevator,
            parking=schema.parkingSlot,
            installment=schema.installment,
            swimming_pool=schema.swimmingPool,
            agent_id=agent_id
        )

        self.add(listing)
        await self.commit()
        await self.refresh(listing)
        await self._add_images_to_listing(listing, images, user_id)
        await self.commit()
        return listing
    
    async def add_images_to_listing(
            self,
            listing: Listing,
            images: list[UploadFile],
            user_id: int
            ) -> Listing:
        """Add images to listing"""
        await self._add_images_to_listing(listing, images, user_id)
        await self.commit()
        return listing
    
    async def _add_images_to_listing(
            self,
            listing: Listing,
            images: list[UploadFile],
            user_id: int
            ) -> None:
        """Add images to listing"""
        for image in images:
            path = f"listing/{user_id}/{listing.id}/images"
            url = await self.staticFilesManager.upload(image, path)
            listing_image = ListingImage(
                listing_id=listing.id,
                image_url=url
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
        await self.staticFilesManager.delete(image.image_url)
        await self.delete(image)
        await self.commit()

    async def delete_listing(
            self,
            listing_id: int,
            ) -> None:
        """Delete listing"""
        listing = await self.get_listing_join_property(id=listing_id)
        self._deactivate_listing(listing)
        await self.commit()
        queue_delete_property.delay(listing_id)

    def _deactivate_listing(
            self,
            listing: Listing,
            ) -> None:
        """Deactivate listing"""
        listing.deactivate()
        for property in listing.properties:
            property.deactivate()

    async def get_listing_by(
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

    async def create_property(
            self,
            schema: CreatePropertySchema,
            images: list[UploadFile],
            documents: list[UploadFile],
            agent_id: int,
            user_id: int,
            listing_id: int = None,
            ) -> Property:
        """Create property"""
        currencies_to_dollar = {
            "€": 1.03,
            "£": 1.22,
            "$": 1,
            "₺": 0.028,
        }
        property_obj = Property(
            listing_id=listing_id,
            description=schema.description,
            price=schema.price * currencies_to_dollar[schema.currency],
            currency=schema.currency,
            original_price=schema.price,
            location=PropertyLocation(
                latitude=schema.latitude,
                longitude=schema.longitude,
                address=schema.address
                ),
            info=PropertyInfo(
                category=schema.category,

                total_area=schema.totalArea,
                living_area=schema.livingArea,

                rooms=schema.rooms,
                bedrooms=schema.bedroom,
                bathrooms=schema.bathroom,
                living_rooms=schema.livingRoom,

                floor=schema.floor,
                floors=schema.buildingFloors,
                balcony=schema.balcony,
                renovation=schema.renovation,
                apartment_stories=schema.apartmentStories
            ),
            building=PropertyBuilding(
                year_built=schema.year,
                elevators=schema.elevator,
                parking=schema.parkingSlot,
                installment=schema.installment,
                swimming_pool=schema.swimmingPool,
                gym=schema.gym
            ),
            owner_id=agent_id)

        self.add(property_obj)
        await self.commit()
        await self.refresh(property_obj)
        await self._add_images_to_property(property_obj, images, user_id)
        await self._add_documents_to_property(property_obj, documents, user_id)
        await self.commit()
        return property_obj

    async def add_images_to_property(
            self,
            property_obj: Property,
            images: list[UploadFile],
            user_id: int
            ) -> None:
        """Add image to property"""
        await self._add_images_to_property(property_obj, images, user_id)
        await self.commit()

    async def _add_documents_to_property(
            self,
            property_obj: Property,
            documents: list[UploadFile],
            user_id: int
            ) -> None:
        """Add documents to property"""
        for document in documents:
            path = f"property/{user_id}/{property_obj.id}/documents"
            url = await self.staticFilesManager.upload(document, path)
            property_document = PropertyDocument(
                property_id=property_obj.id,
                document_url=url
                )
            self.add(property_document)
    
    async def _add_images_to_property(
            self,
            property_obj: Property,
            images: list[UploadFile],
            user_id: int
            ) -> None:
        """Add image to property"""
        for image in images:
            path = f"property/{user_id}/{property_obj.id}/images"
            url = await self.staticFilesManager.upload(image, path)
            print(f"WE ARE ADDING {url} to {property_obj.id}")
            property_image = PropertyImage(
                property_id=property_obj.id,
                image_url=url
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
        property_obj = await self.get_or_404(property_id)

        property_obj.is_sold = is_sold
        if not is_sold:
            await self.delete(property_obj)
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
        )
        await self.session.execute(
            delete(PropertyLike)
            .where(
                and_(
                    PropertyLike.property_id == property_id,
                    PropertyLike.user_id == user_id
                )
            )
        )
        await self.commit()
