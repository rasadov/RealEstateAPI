from sqlalchemy import Column, String, Boolean

from src.base.models import CreateTimestampMixin

class User(CreateTimestampMixin):
    """User model."""

    __tablename__ = "UserModel"

    name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_superuser = Column(Boolean, default=False)
