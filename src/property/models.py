from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, Float, String, Boolean, DateTime
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
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("UserModel.id"), nullable=False)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    sold_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    main_image_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyImageModel.id"), nullable=True)

    main_image: Mapped["PropertyImage"] = relationship("PropertyImage", foreign_keys=[main_image_id])
    images: Mapped[list["PropertyImage"]] = relationship("PropertyImage", back_populates="property")
    likes: Mapped[list["PropertyLike"]] = relationship("PropertyLike", back_populates="property")


class PropertyImage(CustomBase):
    """Property image model."""

    __tablename__ = "PropertyImageModel"

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyModel.id"), nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)

    property: Mapped["Property"] = mapped_column("Property", back_populates="images")

class PropertyLike(CustomBase):
    """Property like model."""

    __tablename__ = "PropertyLikeModel"

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("PropertyModel.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("UserModel.id"), nullable=False)

    property: Mapped["Property"] = relationship("Property", back_populates="likes")
    user: Mapped["User"] = relationship("User")
