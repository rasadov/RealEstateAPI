from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CustomBase, ImageMixin

if TYPE_CHECKING:
    from src.user.models import Agent
    from src.property.models import Property


class Listing(CustomBase):
    """Listing model."""

    __tablename__ = "ListingModel"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("AgentModel.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

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

