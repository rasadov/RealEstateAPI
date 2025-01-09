from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Float, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CustomBase, CreateTimestampMixin, ImageMixin, LocationMixin

if TYPE_CHECKING:
    from src.user.models import Agent, User
    from src.listing.models import Listing


class Property(CreateTimestampMixin):
    """Property model."""

    __tablename__ = "PropertyModel"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ListingModel.id"), nullable=True
    )
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("AgentModel.id"), nullable=False
    )

    location: Mapped["PropertyLocation"] = relationship(
        "PropertyLocation", uselist=False, back_populates="property", cascade="all, delete-orphan"
    )
    owner: Mapped["Agent"] = relationship("Agent", back_populates="properties")
    images: Mapped[list["PropertyImage"]] = relationship(
        "PropertyImage", back_populates="property", cascade="all, delete-orphan"
    )
    info: Mapped["PropertyInfo"] = relationship(
        "PropertyInfo", uselist=False, back_populates="property", cascade="all, delete-orphan"
    )
    building: Mapped["PropertyBuilding"] = relationship(
        "PropertyBuilding", uselist=False, back_populates="property", cascade="all, delete-orphan"
    )
    listing: Mapped["Listing"] = relationship("Listing", back_populates="properties")

    def approve(self) -> None:
        self.approved = True
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


class PropertyImage(ImageMixin):
    """Property image model."""

    __tablename__ = "PropertyImageModel"

    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PropertyModel.id"), nullable=False
    )

    property: Mapped["Property"] = relationship("Property", back_populates="images")


class PropertyLocation(LocationMixin):
    """Property location model."""

    __tablename__ = "PropertyLocationModel"

    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PropertyModel.id"), nullable=False
    )

    property: Mapped["Property"] = relationship("Property", back_populates="location")


class PropertyInfo(CustomBase):
    """Property info model."""

    __tablename__ = "PropertyInfoModel"

    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PropertyModel.id"), nullable=False
    )
    category: Mapped[str] = mapped_column(String, nullable=False)
    apartment_area: Mapped[float] = mapped_column(Float, nullable=False)
    total_area: Mapped[float] = mapped_column(Float, nullable=False)
    kitchen_area: Mapped[float] = mapped_column(Float, nullable=False)
    living_area: Mapped[float] = mapped_column(Float, nullable=False)
    bathrooms: Mapped[int] = mapped_column(Integer, nullable=False)
    rooms: Mapped[int] = mapped_column(Integer, nullable=False)
    living_rooms: Mapped[int] = mapped_column(Integer, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    floors: Mapped[int] = mapped_column(Integer, nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    balcony: Mapped[str] = mapped_column(String, nullable=False)
    view: Mapped[str] = mapped_column(String, nullable=False)

    property: Mapped["Property"] = relationship("Property", back_populates="info")


class PropertyBuilding(CustomBase):
    """Information on property building"""

    __tablename__ = "PropertyBuildingModel"

    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PropertyModel.id"), nullable=False
    )

    year_built: Mapped[int] = mapped_column(Integer, nullable=False)
    elevators: Mapped[int] = mapped_column(Integer, nullable=False)
    building_type: Mapped[str] = mapped_column(String, nullable=False)
    flooring_type: Mapped[str] = mapped_column(String, nullable=False)
    parking: Mapped[str] = mapped_column(String, nullable=False)

    property: Mapped["Property"] = relationship("Property", back_populates="building")


class PropertyReport(CreateTimestampMixin):
    """Report model."""

    __tablename__ = "PropertyReportModel"

    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PropertyModel.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UserModel.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    property: Mapped["Property"] = relationship("Property")
    user: Mapped["User"] = relationship("User")
