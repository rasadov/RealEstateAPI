from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CustomBase, ImageMixin

if TYPE_CHECKING:
    from src.user.models import Agent
    from src.property.models import Property


class Listing(CustomBase):
    """Listing model."""

    __tablename__ = "ListingModel"

    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    building_area: Mapped[float] = mapped_column(Float, nullable=True)
    living_area: Mapped[float] = mapped_column(Float, nullable=True)
    objects: Mapped[int] = mapped_column(Integer, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    building_floors: Mapped[int] = mapped_column(Integer, nullable=True)
    elevators: Mapped[bool] = mapped_column(Boolean, nullable=True)
    parking: Mapped[bool] = mapped_column(Boolean, nullable=True)
    installment: Mapped[bool] = mapped_column(Boolean, nullable=True)
    swimming_pool: Mapped[bool] = mapped_column(Boolean, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("AgentModel.id"), nullable=False
    )

    properties: Mapped[list["Property"]] = relationship(
        "Property", cascade="all, delete-orphan"
        )
    agent: Mapped["Agent"] = relationship("Agent")
    images: Mapped[list["ListingImage"]] = relationship(
        "ListingImage", back_populates="listing", cascade="all, delete-orphan"
    )

    @property
    def length(self) -> int:
        return len(self.properties)

    def deactivate(self) -> None:
        self.is_active = False


class ListingImage(ImageMixin):
    """Listing image model."""

    __tablename__ = "ListingImageModel"

    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ListingModel.id"), nullable=False
    )

    listing: Mapped["Listing"] = relationship("Listing", back_populates="images")

