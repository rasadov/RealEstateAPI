"""Base model class and utils."""
from datetime import datetime

from sqlalchemy import func, String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class CustomBase(Base):
    """Base class for models"""

    __abstract__ = True
    __repr_fields__: tuple[str, ...] = ("id",)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        attrs = ", ".join(
            f"{field}: {getattr(self, field)}" for field in self.__repr_fields__
        )
        return f"{self.__class__.__name__}({attrs})"


class CreateTimestampMixin(CustomBase):
    """
    Mixin for adding created at field to the model.

    Must come before the `Base` class in mro().
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ImageMixin(CustomBase):
    """Mixin for adding image to the model"""

    __abstract__ = True

    image_url: Mapped[str] = mapped_column(String, nullable=True)

    def __str__(self):
        return self.image_url

    def __repr__(self):
        return self.image_url

class LocationMixin(CustomBase):
    """Mixin for adding location to the model"""

    __abstract__ = True

    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)

    def __str__(self):
        return f"{self.longitude}, {self.latitude}"

    def __repr__(self):
        return f"{self.longitude}, {self.latitude}"
