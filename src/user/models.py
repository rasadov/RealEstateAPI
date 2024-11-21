from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CreateTimestampMixin, CustomBase
from src.auth import utils

if TYPE_CHECKING:
    from src.property.models import Property

class User(CreateTimestampMixin):
    """User model."""

    __tablename__ = "UserModel"

    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True)
    bio: Mapped[str] = mapped_column(nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    role: Mapped[str] = mapped_column(nullable=True, default="buyer")
    level: Mapped[int] = mapped_column(nullable=False, default=0)

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
    properties: Mapped[list["Property"]] = relationship("Property", back_populates="owner")

    def __init__(self, user_id: int, serial_number: str) -> None:
        """Initialize agent"""
        self.user_id = user_id
        self.serial_number = serial_number

class Approval(CreateTimestampMixin):
    """Approval model."""

    __tablename__ = "ApprovalModel"

    user_id: Mapped[int] = mapped_column(ForeignKey("UserModel.id"), nullable=False)
    property_id: Mapped[int] = mapped_column(ForeignKey("PropertyModel.id"), nullable=False)

    user: Mapped["User"] = relationship("User")
    property: Mapped["Property"] = relationship("Property")
