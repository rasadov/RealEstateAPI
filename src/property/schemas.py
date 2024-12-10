from pydantic import BaseModel
from typing import Optional

class CreatePropertySchema(BaseModel):
    name: str
    description: str
    price: float
    latitude: float
    longitude: float
    category: str
    total_area: float
    living_area: float
    bedrooms: int
    living_rooms : int
    floor: int
    floors: int
    district: str
    address: str

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

    def get_filters(self) -> dict:
        filters = {}
        if self.min_area:
            filters["min_area"] = (self.min_area, "info.total_area", ">=")
        if self.max_area:
            filters["max_area"] = (self.max_area, "info.total_area", "<=")
        if self.min_price:
            filters["min_price"] = (self.min_price, "price", ">=")
        if self.max_price:
            filters["max_price"] = (self.max_price, "price", "<=")
        if self.rooms:
            filters["rooms"] = (self.rooms, "info.bedrooms", "==")
        if self.category:
            filters["category"] = (self.category, "info.category", "==")
        if self.district:
            filters["district"] = (self.district, "info.district", "==")
        return filters
