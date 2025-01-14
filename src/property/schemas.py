from typing import Optional

from pydantic import BaseModel

from src.base.schemas import as_form



@as_form
class CreatePropertySchema(BaseModel):
    description: str
    price: float
    latitude: float
    longitude: float
    category: str
    total_area: float
    living_area: float
    rooms: int
    bathrooms: int
    living_rooms: int
    floor: int
    floors: int
    district: Optional[str]
    address: Optional[str]
    balcony: Optional[str]
    view: Optional[str]
    year_built: Optional[int]
    building_type: Optional[str]
    elevators: Optional[int]
    parking: Optional[str]
    flooring_type: Optional[str]
    # owner_id: int

class MapSearchSchema(BaseModel):
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    rooms: Optional[int] = None
    category: Optional[str] = None
    district: Optional[str] = None

class SearchPropertySchema(BaseModel):
    page: int = 1
    elements: int = 10
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    rooms: Optional[int] = None
    category: Optional[str] = None
    district: Optional[str] = None

    def get_filters(self) -> list[tuple]:
        filters = []
        if self.min_area:
            filters.append((self.min_area, "info.total_area", ">="))
        if self.max_area:
            filters.append((self.max_area, "info.total_area", "<="))
        if self.min_price:
            filters.append((self.min_price, "price", ">="))
        if self.max_price:
            filters.append((self.max_price, "price", "<="))
        if self.rooms:
            filters.append((self.rooms, "info.bedrooms", "=="))
        if self.category:
            filters.append((self.category, "info.category", "=="))
        if self.district:
            filters.append((self.district, "info.district", "=="))
        return filters
