from sqlalchemy import Column, String, Boolean

from src.base.models import CreateTimestampMixin
from src.auth import utils

class User(CreateTimestampMixin):
    """User model."""

    __tablename__ = "UserModel"

    username = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_superuser = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=False)

    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        return utils.verify_password(password, self.password_hash)

    def change_password(self, new_password: str) -> None:
        """Change user password"""
        self.password_hash = utils.hash_password(new_password)

    def confirm_email(self) -> None:
        """Confirm user email"""
        self.is_confirmed = True

    def __str__(self) -> str:
        return self.email
