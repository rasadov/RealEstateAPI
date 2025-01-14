from typing import Optional

from pydantic import BaseModel

from src.base.schemas import as_form


@as_form
class CreateListingSchema(BaseModel):
    cater
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None

