from typing import Optional

from pydantic import BaseModel

from src.base.schemas import as_form

@as_form
class CreateListingSchema(BaseModel):
    # General
    residentialComplex: Optional[str] = "No title"
    category: Optional[str] = "Apartment"
    description: Optional[str] = "No description"
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    # Info
    buildingArea: Optional[float] = None
    livingArea: Optional[float] = None
    objects: Optional[int] = None
    year: Optional[int] = None
    buildingFloors: Optional[int] = None

    elevator: Optional[bool] = None
    parkingSlot: Optional[bool] = None
    installment: Optional[bool] = None
    swimmingPool: Optional[bool] = None
