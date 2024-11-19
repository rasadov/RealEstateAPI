"""Module with user repository"""
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import func
from sqlalchemy.future import select

from src.base.repository import BaseRepository
from src.staticfiles.manager import BaseStaticFilesManager
from src.user.models import User
from src.auth import exceptions


@dataclass
class UserRepository(BaseRepository[User]):
    """User repository"""

    staticFilesManager: BaseStaticFilesManager

    async def get_user_by(
            self,
            **kwargs,
            ) -> User:
        """Get user by any field"""
        result = await self.session.execute(
            select(User).filter_by(
                **kwargs
                ))
        return result.scalars().first()

    async def get_or_404(
            self,
            user_id: int,
            ) -> User:
        """Get user by id or raise 404"""
        result = await self.session.execute(
            select(User).filter(
                User.id == user_id
                ))
        user = result.scalars().first()
        if not user:
            raise exceptions.UserNotFound
        return user

    async def get_or_401(
            self,
            user_id: int,
            ) -> User:
        """Get user by id or raise 401"""
        result = await self.session.execute(
            select(User).filter(
                User.id == user_id
                ))
        user = result.scalars().first()
        if not user:
            raise exceptions.Unauthorized
        return user

    async def get_users_page_by(
            self,
            limit: int,
            offset: int,
            **kwargs,
            ) -> Sequence[User]:
        """Get users page"""
        result = await self.session.execute(
            select(User).filter_by(
                **kwargs
                ).
                limit(limit).
                offset(offset)
            )
        return result.scalars().all()

    async def get_users_count(
            self,
            ) -> int:
        """Get users count"""
        result = await self.session.execute(
            select(func.count(User.id))
            )
        return result.scalar()
