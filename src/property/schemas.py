from pydantic import BaseModel

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
