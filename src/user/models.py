from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreateTimestampMixin, CustomBase
from src.auth import utils

if TYPE_CHECKING:
    from src.property.models import Property, PropertyLike

class User(CreateTimestampMixin):
    """User model."""

    __tablename__ = "UserModel"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    bio: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("RoleModel.id"), nullable=True)

    role: Mapped["Roles"] = relationship("Roles")
    properties: Mapped[list["Property"]] = relationship("Property", back_populates="owner")
    likes: Mapped[list["PropertyLike"]] = relationship("PropertyLike", back_populates="user")


    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        return utils.verify_password(password, self.password_hash)

    def change_password(self, new_password: str) -> None:
        """Change user password"""
        self.password_hash = utils.hash_password(new_password)

    def confirm_email(self) -> None:
        """Confirm user email"""
        self.is_confirmed = True

class Roles(CustomBase):
    """Role model."""

    __tablename__ = "RoleModel"

    name: Mapped[str] = mapped_column(nullable=False)
