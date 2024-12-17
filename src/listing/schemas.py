from typing import Optional

from pydantic import BaseModel

from src.base.schemas import as_form


@as_form
class CreateListingSchema(BaseModel):
    name: str
    description: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None

