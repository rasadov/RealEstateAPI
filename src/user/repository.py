"""Module with user repository"""
from dataclasses import dataclass

from sqlalchemy import select

from src.user.models import User
from src.base.repository import BaseRepository
from src.auth import exceptions

@dataclass
class UserRepository(BaseRepository[User]):
    "User repository"

    async def get_user_by(self, **kwargs) -> User:
        """Get user by any field"""
        result = await self.session.execute(select(User).filter_by(**kwargs))
        return result.scalars().first()

    async def get_or_404(self, user_id: int) -> User:
        """Get user by id or raise 404"""
        result = await self.session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise exceptions.UserNotFound
        return user

    async def get_or_401(self, user_id: int) -> User:
        """Get user by id or raise 401"""
        result = await self.session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise exceptions.Unauthorized
        return user

    async def get_users_page(self, limit: int, offset: int) -> list[User]:
        """Get users page"""
        result = await self.session.execute(select(User).limit(limit).offset(offset))
        return result.scalars().all()

    async def get_users_count(self) -> int:
        """Get users count"""
        result = await self.session.execute(select(User).count())
        return result.scalar()
