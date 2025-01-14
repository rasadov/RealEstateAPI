from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CustomBase, CreateTimestampMixin, ImageMixin
from src.auth import utils

if TYPE_CHECKING:
    from src.property.models import Property, Listing


class User(CreateTimestampMixin):
    """User model."""

    __tablename__ = "UserModel"

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    bio: Mapped[str] = mapped_column(String, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String, nullable=True, default="buyer")
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    agent: Mapped["Agent"] = relationship("Agent", uselist=False, back_populates="user")
    image: Mapped["UserProfileImage"] = relationship(
        "UserProfileImage", uselist=False, back_populates="user",
    )
    approvals: Mapped[list["Approval"]] = relationship(
        "Approval", back_populates="user"
    )

    @property
    def image_url(self) -> str:
        """Get user image url"""
        return self.image.image_url if self.image else "https://flattybucket.s3.us-east-1.amazonaws.com/uploads/user.jpg"

    def update_user(self, payload: dict) -> None:
        """Update user"""
        for key, value in payload.items():
            if key in ("name", "phone", "bio"):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid key: {key}")

    def dict(self) -> dict:
        """Get user dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "bio": self.bio,
            "role": self.role,
            "level": self.level,
            "created_at": self.created_at.isoformat(),
            "image_url": self.image_url,
        }

    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        return utils.verify_password(password, self.password_hash)

    def change_password(self, new_password: str) -> None:
        """Change user password"""
        self.password_hash = utils.hash_password(new_password)

    def confirm_email(self) -> None:
        """Confirm user email"""
        self.is_confirmed = True


class UserProfileImage(ImageMixin):
    """User image model."""

    __tablename__ = "UserImageModel"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UserModel.id"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="image")


class Agent(CustomBase):
    """Agent model."""

    __tablename__ = "AgentModel"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UserModel.id"), nullable=False
    )
    serial_number: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=True)
    experience: Mapped[float] = mapped_column(Float, nullable=True)
    sales: Mapped[int] = mapped_column(Integer, nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="agent")
    properties: Mapped[list["Property"]] = relationship(
        "Property", back_populates="owner"
    )
    listings: Mapped[list["Listing"]] = relationship("Listing", back_populates="agent")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="agent")

    def __init__(self, user_id: int, serial_number: str) -> None:
        """Initialize agent"""
        self.user_id = user_id
        self.serial_number = serial_number

    def dict(self) -> dict:
        """Get agent dictionary"""
        return {
            "id": self.id,
            "name": self.user.name,
            "email": self.user.email,
            "created_at": self.user.created_at,
            "phone": self.user.phone,
            "bio": self.user.bio,
            "serial_number": self.serial_number,
            "company": self.company,
            "experience": self.experience,
        }
    
    def update_agent(self, payload: dict) -> None:
        """Update agent"""
        for key, value in payload.items():
            print("KEY", key)
            print("VALUE", value)
            if key in ("serial_number", "company", "experience", "sales"):
                setattr(self, key, value)
            elif key in ("name", "phone", "bio"):
                setattr(self.user, key, value)
            else:
                raise ValueError(f"Invalid key: {key}")


class Approval(CreateTimestampMixin):
    """Approval model."""

    __tablename__ = "ApprovalModel"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UserModel.id"), nullable=False
    )
    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PropertyModel.id"), nullable=False
    )

    user: Mapped["User"] = relationship("User")
    property: Mapped["Property"] = relationship("Property")


class Review(CreateTimestampMixin):
    """Review of Agent model."""

    __tablename__ = "ReviewModel"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UserModel.id"), nullable=False
    )
    agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("AgentModel.id"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User")
    agent: Mapped["Agent"] = relationship("Agent")


class AgentReport(CreateTimestampMixin):
    """Report model."""

    __tablename__ = "AgentReportModel"

    agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("AgentModel.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UserModel.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    agent: Mapped["Agent"] = relationship("Agent")
    user: Mapped["User"] = relationship("User")
