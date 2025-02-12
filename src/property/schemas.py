from typing import Optional

from pydantic import BaseModel

from src.base.schemas import as_form


@as_form
class CreatePropertySchema(BaseModel):
    # General
    title: Optional[str] = "No title"
    category: Optional[str] = "Apartment"
    residentialComplex: Optional[str]
    description: Optional[str] = "No description"
    price: Optional[float] = 1000.0
    currency: Optional[str] = "$"
    # Location
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    # Info
    floor: Optional[int]
    totalArea: Optional[float]
    livingArea: Optional[float]
    rooms: Optional[int]
    livingRoom: Optional[int]
    bedroom: Optional[int]
    bathroom: Optional[int]
    balcony: Optional[int]
    buildingFloors: Optional[int]
    year: Optional[int]
    renovation: Optional[str]
    apartmentStories: Optional[int]
    # Building
    elevator: Optional[bool]
    parkingSlot: Optional[bool]
    installment: Optional[bool]
    swimmingPool: Optional[bool]
    gym: Optional[bool]


class MapSearchSchema(BaseModel):
    areaFrom: Optional[int] = None
    areaTo: Optional[int] = None
    priceRangeMin: Optional[float] = None
    priceRangeMax: Optional[float] = None
    roomNumber: Optional[str] = None  # Comma-separated string
    city: Optional[str] = None
    category: Optional[str] = None

    livingAreaFrom: Optional[float] = None
    livingAreaTo: Optional[float] = None
    minFloor: Optional[int] = None
    maxFloor: Optional[int] = None
    notFirstFloor: Optional[bool] = None
    notLastFloor: Optional[bool] = None
    lastFloor: Optional[bool] = None
    year: Optional[int] = None
    livingRooms: Optional[int] = None
    bathrooms: Optional[int] = None
    balconies: Optional[int] = None
    bedrooms: Optional[int] = None
    installment: Optional[bool] = None
    elevator: Optional[bool] = None
    parkingSlot: Optional[bool] = None
    gym: Optional[bool] = None
    swimmingPool: Optional[bool] = None

    def get_filters(self) -> list[tuple]:
        """
        Returns a list of tuples:
          (value, "dot.notation.path", operator)
        that can be processed by _get_filter_conditions().

        Skips any numeric fields set to 0, and any fields that are None.
        """
        filters = []

        # If min_area is set and not 0
        if self.areaFrom is not None and self.areaFrom > 0:
            filters.append((self.areaFrom, "info.total_area", ">="))

        # If max_area is set and not 0
        if self.areaTo is not None and self.areaTo > 0:
            filters.append((self.areaTo, "info.total_area", "<="))

        # If min_price is set and not 0
        if self.priceRangeMin is not None and self.priceRangeMin > 0:
            filters.append((self.priceRangeMin, "price", ">="))

        # If max_price is set and not 0
        if self.priceRangeMax is not None and self.priceRangeMax > 0:
            filters.append((self.priceRangeMax, "price", "<="))

        # If roomNumber is set and not empty
        if self.roomNumber:
            room_numbers = [int(x) for x in self.roomNumber.split(",")]
            print(room_numbers)
            filters.append((room_numbers, "info.bedrooms", "in"))

        # If category is set (string)
        if self.category:
            filters.append((self.category, "info.category", "=="))

        # If city is set (string)
        if self.city:
            print(self.city)
            filters.append((self.city, "location.address", "ilike"))

        if self.livingAreaFrom is not None and self.livingAreaFrom > 0:
            filters.append((self.livingAreaFrom, "info.living_area", ">="))

        if self.livingAreaTo is not None and self.livingAreaTo > 0:
            filters.append((self.livingAreaTo, "info.living_area", "<="))

        if self.minFloor is not None and self.minFloor > 0:
            print(self.minFloor)
            filters.append((self.minFloor, "info.floor", ">="))

        if self.maxFloor is not None and self.maxFloor > 0:
            print(self.maxFloor)
            filters.append((self.maxFloor, "info.floor", "<="))

        if self.notFirstFloor:
            filters.append(("NotFirstFloor", "info.floor", ">"))

        # If notLastFloor is set
        if self.notLastFloor:
            filters.append(("NotLastFloor", "info.floor", "<"))

        # If lastFloor is set
        if self.lastFloor:
            filters.append(("LastFloor", "info.floor", "=="))

        if self.year is not None and self.year > 0:
            filters.append((self.year, "info.year", "=="))

        if self.livingRooms is not None and self.livingRooms > 0:
            filters.append((self.livingRooms, "info.living_rooms", "=="))

        if self.bathrooms is not None and self.bathrooms > 0:
            filters.append((self.bathrooms, "info.bathrooms", "=="))

        if self.balconies is not None and self.balconies > 0:
            filters.append((self.balconies, "info.balcony", "=="))

        if self.bedrooms is not None and self.bedrooms > 0:
            filters.append((self.bedrooms, "info.bedrooms", "=="))

        if self.installment is not None:
            filters.append((self.installment, "building.installment", "=="))

        if self.elevator is not None:
            filters.append((self.elevator, "building.elevator", "=="))

        if self.parkingSlot is not None:
            filters.append((self.parkingSlot, "building.parking_slot", "=="))

        if self.gym is not None:
            filters.append((self.gym, "building.gym", "=="))

        if self.swimmingPool is not None:
            filters.append((self.swimmingPool, "building.swimming_pool", "=="))

        return filters

class SearchPropertySchema(MapSearchSchema):
    page: int = 1
    elements: int = 50

