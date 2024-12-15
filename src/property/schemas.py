from typing import Optional, Type
import inspect

from fastapi import Form
from pydantic import BaseModel, field_validator

def as_form(cls: Type[BaseModel]):
    new_params = []
    for field_name, field in cls.model_fields.items():
        alias = field.alias or field_name  # Fallback to field name if alias is None
        required = field.is_required()
        print(f"Processing field: Name: {field_name}, Alias: {alias}, Required: {required}, Default: {field.default}, Annotation: {field.annotation}")

        param = inspect.Parameter(
            alias,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Form(... if required else None),
            annotation=field.annotation,
        )
        new_params.append(param)

    async def _as_form(**data):
        print("Form data received:", data)
        return cls(**data)

    sig = inspect.signature(_as_form)
    new_sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = new_sig
    setattr(cls, "as_form", _as_form)
    return cls


@as_form
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


@as_form
class CreateListingSchema(BaseModel):
    name: str
    description: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None


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

class PageSchema(BaseModel):
    offset: int = 0
    elements: int = 10
