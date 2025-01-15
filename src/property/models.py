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

    description: Mapped[str] = mapped_column(String, nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="$")
    original_price: Mapped[float] = mapped_column(Float, nullable=True)
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
    likes: Mapped[list["PropertyLike"]] = relationship("PropertyLike", back_populates="property")

    def approve(self) -> None:
        self.approved = True
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def viewed(self) -> None:
        self.views += 1


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

    address: Mapped[str] = mapped_column(String, nullable=True)
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
    category: Mapped[str] = mapped_column(String, nullable=True)
    total_area: Mapped[float] = mapped_column(Float, nullable=True)
    living_area: Mapped[float] = mapped_column(Float, nullable=True)
    bathrooms: Mapped[int] = mapped_column(Integer, nullable=True)
    bedrooms: Mapped[int] = mapped_column(Integer, nullable=True)
    living_rooms: Mapped[int] = mapped_column(Integer, nullable=True)
    floor: Mapped[int] = mapped_column(Integer, nullable=True)
    floors: Mapped[int] = mapped_column(Integer, nullable=True)
    balcony: Mapped[int] = mapped_column(Integer, nullable=True)
    condition: Mapped[str] = mapped_column(String, nullable=True)
    apartment_stories: Mapped[int] = mapped_column(Integer, nullable=True)

    property: Mapped["Property"] = relationship("Property", back_populates="info")


class PropertyBuilding(CustomBase):
    """Information on property building"""

    __tablename__ = "PropertyBuildingModel"

    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PropertyModel.id"), nullable=False
    )

    year_built: Mapped[int] = mapped_column(Integer, nullable=True)
    elevators: Mapped[bool] = mapped_column(Boolean, nullable=True)
    parking: Mapped[bool] = mapped_column(Boolean, nullable=True)
    installment: Mapped[bool] = mapped_column(Boolean, nullable=True)
    swimming_pool: Mapped[bool] = mapped_column(Boolean, nullable=True)

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


class PropertyLike(CreateTimestampMixin):
    """Property like model."""

    __tablename__ = "PropertyLikeModel"

    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PropertyModel.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UserModel.id"), nullable=False
    )

    property: Mapped["Property"] = relationship("Property")
    user: Mapped["User"] = relationship("User")
