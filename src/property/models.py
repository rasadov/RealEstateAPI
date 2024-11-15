from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, Float, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreateTimestampMixin, CustomBase
from src.user.models import User

if TYPE_CHECKING:
    from src.user.models import User


class Property(CreateTimestampMixin):
    """Property model."""

    __tablename__ = "PropertyModel"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("UserModel.id"), nullable=False)
    main_image_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyImageModel.id"), nullable=True)

    owner: Mapped["User"] = relationship("User", back_populates="properties")
    main_image: Mapped["PropertyImage"] = relationship("PropertyImage", foreign_keys=[main_image_id])
    images: Mapped[list["PropertyImage"]] = relationship("PropertyImage", back_populates="property")
    likes: Mapped[list["PropertyLike"]] = relationship("PropertyLike", back_populates="property")

    def approve(self):
        self.approved = True

class SoldProperty(CreateTimestampMixin):
    """Sold property model."""

    __tablename__ = "SoldPropertyModel"

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyModel.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)

    property: Mapped["Property"] = relationship("Property")

class PropertyImage(CreateTimestampMixin):
    """Property image model."""

    __tablename__ = "PropertyImageModel"

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyModel.id"), nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)

    property: Mapped["Property"] = mapped_column("Property", back_populates="images")

class PropertyLike(CustomBase):
    """Property like model."""

    __tablename__ = "PropertyLikeModel"

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyModel.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("UserModel.id"), nullable=False)

    property: Mapped["Property"] = relationship("Property", back_populates="likes")
    user: Mapped["User"] = relationship("User")
