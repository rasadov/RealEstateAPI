"""Module with user repository"""
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

from src.base.repository import BaseRepository
from src.listing.models import Listing
from src.property.models import Property
from src.staticfiles.manager import BaseStaticFilesManager
from src.user.models import User, Agent, Review, UserProfileImage
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
            select(User)
            .options(
                joinedload(User.agent)
                .joinedload(Agent.reviews),
                joinedload(User.image),
            )
            .filter_by(
                **kwargs
                ))
        return result.scalars().first()

    async def get_or_404(
            self,
            user_id: int,
            ) -> User:
        """Get user by id or raise 404"""
        result = await self.session.execute(
            select(User)
            .options(
                joinedload(User.agent)
                .joinedload(Agent.reviews),
                joinedload(User.image),
            )
            .filter(
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
            select(User).options(
                joinedload(User.agent)
                .joinedload(Agent.reviews),
                joinedload(User.image),
            ).filter(
                User.id == user_id
                ))
        user = result.scalars().first()
        if not user:
            raise exceptions.Unauthorized
        return user

    async def get_agent_by(
            self,
            exception: Exception = None,
            **kwargs,
            ) -> Agent:
        """Get agent by any field"""
        result = await self.session.execute(
            select(Agent).options(
                joinedload(Agent.user)
                .load_only(User.id, User.name, User.email, User.phone, User.bio, User.created_at)
                .joinedload(User.image),
                joinedload(Agent.reviews),
                joinedload(Agent.properties).options(
                    joinedload(Property.location),
                    joinedload(Property.info),
                    joinedload(Property.images),
                ),
                joinedload(Agent.listings)
                .joinedload(Listing.images),
                ).filter_by(
                **kwargs
                ))
        agent = result.scalars().first()
        if not agent:
            raise exception
        return agent

    async def get_agent_by_or_404(
            self,
            **kwargs,
            ) -> Agent:
        """Get agent by any field"""
        return await self.get_agent_by(
            exceptions.AgentNotFound,
            **kwargs
            )
    
    async def get_agent_by_or_401(
            self,
            **kwargs,
            ) -> Agent:
        """Get agent by any field"""
        return await self.get_agent_by(
            exceptions.Unauthorized,
            **kwargs
            )

    async def get_user_profile_images(
            self,
            user_id: int
    ) -> Sequence[UserProfileImage]:
        """Get user profile images"""
        result = await self.session.execute(
            select(UserProfileImage)
            .filter(UserProfileImage.user_id == user_id)
        )
        return result.scalars().all()

    async def get_users_page_by(
            self
            ) -> Sequence[Agent]:
        """Get users page"""
        result = await self.session.execute(
            select(
                Agent
            )
            .join(User)
            .options(
                joinedload(Agent.user).
                load_only(
                    User.id,
                    User.name,
                    User.email,
                    User.phone,
                    User.bio,
                    User.created_at,
                )
                .joinedload(User.image),
            )
            .filter(User.id.in_([18, 34, 35, 37, 38, 39]))
            )
        return result.scalars().unique().all()

    async def get_agents_page(
            self,
            page: int,
            elements: int,
            ) -> Sequence[User]:
        """Get agents page"""
        result = await self.session.execute(
            select(User).options(
                joinedload(User.agent)
                .options(
                    joinedload(Agent.reviews),
                    joinedload(Agent.properties),
                ),
                joinedload(User.image),
                ).filter(
                User.role == "agent"
                )
            .limit(elements)
            .offset((page-1)*elements)
            )

        return result.scalars().unique().all()

    async def get_users_count(
            self,
            ) -> int:
        """Get users count"""
        result = await self.session.execute(
            select(func.count(User.id))
            )
        return result.scalar()

    async def add_review(
            self,
            user_id: int,
            agent_id: int,
            rating: int,
            comment: str,
            ) -> None:
        """Post comment"""
        print(user_id, agent_id, rating, comment)
        print(type(user_id), type(agent_id), type(rating), type(comment))
        self.session.add(
            Review(
                user_id=user_id,
                agent_id=agent_id,
                rating=rating,
                comment=comment,
                ))
        await self.session.commit()

    async def delete_user(
            self,
            user_id: int,
            ) -> None:
        """Delete user"""
        user = await self.get_or_404(user_id)
        await self.session.delete(user)
        await self.session.commit()
