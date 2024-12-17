from typing import Type
import inspect

from fastapi import Form
from pydantic import BaseModel


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
