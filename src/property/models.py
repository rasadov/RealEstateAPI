from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Float, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreateTimestampMixin, CustomBase

if TYPE_CHECKING:
    from src.user.models import Agent

class Listing(CustomBase):
    """Listing model."""

    __tablename__ = "ListingModel"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey("AgentModel.id"), nullable=False)

    properties: Mapped[list["Property"]] = relationship("Property")
    agent: Mapped["Agent"] = relationship("Agent")

class Property(CreateTimestampMixin):
    """Property model."""

    __tablename__ = "PropertyModel"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    listing_id: Mapped[int] = mapped_column(Integer, ForeignKey("ListingModel.id"), nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("AgentModel.id"), nullable=False)

    location: Mapped["Location"] = relationship("Location", uselist=False, backref="property")
    owner: Mapped["Agent"] = relationship("Agent", back_populates="properties")
    images: Mapped[list["PropertyImage"]] = relationship("PropertyImage", back_populates="property")
    info: Mapped["PropertyInfo"] = relationship("PropertyInfo", uselist=False, backref="property")

    def approve(self) -> None:
        self.approved = True
        self.is_active = True
        self.location.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
        self.location.is_active = False

class PropertyImage(CustomBase):
    """Property image model."""

    __tablename__ = "PropertyImageModel"

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyModel.id"), nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)

    property: Mapped["Property"] = mapped_column("Property", back_populates="images")

class Location(CustomBase):
    """Location model."""

    __tablename__ = "LocationModel"

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyModel.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)

class PropertyInfo(CustomBase):
    """Property info model."""

    __tablename__ = "PropertyInfoModel"

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyModel.id"), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    total_area: Mapped[float] = mapped_column(Float, nullable=False)
    living_area: Mapped[float] = mapped_column(Float, nullable=False)
    bedrooms: Mapped[int] = mapped_column(Integer, nullable=False)
    living_rooms: Mapped[int] = mapped_column(Integer, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    floors: Mapped[int] = mapped_column(Integer, nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
