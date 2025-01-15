from typing import Optional

from pydantic import BaseModel

from src.base.schemas import as_form


@as_form
class CreatePropertySchema(BaseModel):
    # General
    category: str
    residentialComplex: Optional[str]
    description: str
    price: float
    currency: str
    # Location
    latitude: float
    longitude: float
    address: str
    # Info
    floor: int
    totalArea: float
    livingArea: float
    livingRoom: int
    bedroom: int
    balcony: int
    bathroom: int
    buildingFloors: int
    year: Optional[int]
    condition: Optional[str]
    apartmentStories: Optional[int]

    elevator: Optional[bool]
    parkingSlot: Optional[bool]
    installment: Optional[bool]
    swimmingPool: Optional[bool]


class MapSearchSchema(BaseModel):
    areafrom: Optional[float] = None
    areato: Optional[float] = None
    priceRangemin: Optional[float] = None
    priceRangemax: Optional[float] = None
    roomNumber: Optional[int] = None
    location: Optional[str] = None
    category: Optional[str] = None
    # renovation: Optional[str] = None


    def get_filters(self) -> list[tuple]:
        """
        Returns a list of tuples:
          (value, "dot.notation.path", operator)
        that can be processed by _get_filter_conditions().

        Skips any numeric fields set to 0, and any fields that are None.
        """
        filters = []

        # If min_area is set and not 0
        if self.areafrom is not None and self.areafrom > 0:
            filters.append((self.areafrom, "info.total_area", ">="))

        # If max_area is set and not 0
        if self.areato is not None and self.areato > 0:
            filters.append((self.areato, "info.total_area", "<="))

        # If min_price is set and not 0
        if self.priceRangemin is not None and self.priceRangemin > 0:
            filters.append((self.priceRangemin, "price", ">="))

        # If max_price is set and not 0
        if self.priceRangemax is not None and self.priceRangemax > 0:
            filters.append((self.priceRangemax, "price", "<="))

        # If rooms is set and not 0
        if self.roomNumber is not None and self.roomNumber > 0:
            filters.append((self.roomNumber, "info.bedrooms", "=="))

        # If category is set (string)
        if self.category:
            filters.append((self.category, "info.category", "=="))

        return filters


class SearchPropertySchema(MapSearchSchema):
    page: int = 1
    elements: int = 10

