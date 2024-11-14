from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import CreateTimestampMixin, CustomBase
from app.auth import utils

if TYPE_CHECKING:
    from app.property.models import Property, PropertyLike

class User(CreateTimestampMixin):
    """User model."""

    __tablename__ = "UserModel"

    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True)
    bio: Mapped[str] = mapped_column(nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("RoleModel.id"), nullable=True)

    role: Mapped["Roles"] = relationship("Roles")
    properties: Mapped[list["Property"]] = relationship("Property", back_populates="owner")
    likes: Mapped[list["PropertyLike"]] = relationship("PropertyLike", back_populates="user")
    approvals: Mapped[list["Approval"]] = relationship("Approval", back_populates="user")


    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        return utils.verify_password(password, self.password_hash)

    def change_password(self, new_password: str) -> None:
        """Change user password"""
        self.password_hash = utils.hash_password(new_password)

    def confirm_email(self) -> None:
        """Confirm user email"""
        self.is_confirmed = True

class Agent(CustomBase):
    """Agent model."""

    __tablename__ = "AgentModel"

    user_id: Mapped[int] = mapped_column(ForeignKey("UserModel.id"), nullable=False)
    serial_number: Mapped[str] = mapped_column(nullable=False)
    company: Mapped[str] = mapped_column()

    user: Mapped["User"] = relationship("User")

class Approval(CustomBase):
    """Approval model."""

    __tablename__ = "ApprovalModel"

    user_id: Mapped[int] = mapped_column(ForeignKey("UserModel.id"), nullable=False)
    property_id: Mapped[int] = mapped_column(ForeignKey("PropertyModel.id"), nullable=False)

    user: Mapped["User"] = relationship("User")
    property: Mapped["Property"] = relationship("Property")

class Roles(CustomBase):
    """Role model."""

    __tablename__ = "RoleModel"

    name: Mapped[str] = mapped_column(nullable=False)
