from dataclasses import dataclass
from typing import Dict, Sequence

from src.user.repository import UserRepository
from src.user.models import User, Approval
from src.auth import exceptions
from src.auth.schemas import TokenData 
from src.property.repository import PropertyRepository
from src.property.models import Property


@dataclass
class AdminService:
    """Admin service."""
    user_repository: UserRepository
    property_repository: PropertyRepository


    async def get_users_page(
            self,
            token: TokenData,
            page: int,
            elements: int,
            role: str = None,
            lvl: int = None,
            ) -> Sequence[User]:
        """Get users."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if  level < 1:
            raise exceptions.Unauthorized

        filters = {}
        # if lvl is not None:
        #     if lvl > level or (lvl == level and level != 4):
        #         raise exceptions.Unauthorized
        #     filters["level"] = lvl
        # else:
        #     if level == 4:
        #         filters["level"] = 4
        #     else:
        #         filters["level"] = level - 1

        if role is not None:
            filters["role"] = role

        return await self.user_repository.get_users_page_by()

    async def get_agent_page(
            self,
            token: TokenData,
            page: int,
            elements: int,
            ) -> Sequence[User]:
        """Get users."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if  level < 1:
            raise exceptions.Unauthorized

        return await self.user_repository.get_agents_page(
            page, elements)

    async def delete_property(
            self,
            token: TokenData,
            property_id: int,
            ) -> Dict[str, str]:
        """Delete property."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 1:
            raise exceptions.Unauthorized

        prop = await self.property_repository.get_or_404(property_id)
        await self.property_repository.admin_delete_property(prop)
        return {
            "detail": "Property deleted",
        }

    async def get_admin_properties_page(
            self,
            token: TokenData,
            page: int,
            elements: int,
            ) -> Sequence[Property]:
        """Get properties."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 1:
            raise exceptions.Unauthorized

        return {
            "properties": await self.property_repository.get_properties_page_admin(
                elements, (page - 1) * elements),
            "total": await self.property_repository.get_properties_count()
        }

    async def get_unapproved_properties_page(
            self,
            token: TokenData,
            page: int,
            elements: int,
            ) -> Sequence[Property]:
        """Get unapproved properties."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 1:
            raise exceptions.Unauthorized

        return await self.property_repository.get_properties_page_by(
            elements, (page - 1) * elements, approved=False)

    async def get_approvals(
            self,
            token: TokenData,
            page: int,
            elements: int,
            ) -> Sequence[Approval]:
        """Get approvals."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 2:
            raise exceptions.Unauthorized

        return await self.property_repository.get_approvals_page(
            elements, (page - 1) * elements)

    async def delete_user(
            self,
            token: TokenData,
            user_id: int,
            ) -> Dict[str, str]:
        """Delete user."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 1:
            raise exceptions.Unauthorized

        user = await self.user_repository.get_or_404(user_id)
        await self.user_repository.delete_user(user.id)
        return {
            "detail": "User deleted",
        }

    async def get_sold_properties(
            self,
            token: TokenData,
            page: int,
            elements: int,
            ) -> Sequence[Property]:
        """Get sold properties."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 2:
            raise exceptions.Unauthorized

        return await self.property_repository.get_sold_properties_page(
            elements, (page - 1) * elements)

    async def approve_property(
            self,
            token: TokenData,
            property_id: int,
            ) -> dict[str, str]:
        """Approve property."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 2:
            raise exceptions.Unauthorized

        property_obj = await self.property_repository.get_or_404(property_id)
        property_obj.approve()
        await self.property_repository.commit()
        return {
            "detail": "Property approved",
        }

    async def disapprove_property(
            self,
            token: TokenData,
            property_id: int,
            ) -> dict[str, str]:
        """Disapprove property."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 2:
            raise exceptions.Unauthorized

        property_obj = await self.property_repository.get_or_404(property_id)
        property_obj.disapprove()
        await self.property_repository.commit()
        return {
            "detail": "Property disapproved",
        }

    async def deactivate_property(
            self,
            token: TokenData,
            property_id: int,
            ) -> dict[str, str]:
        """Deactivate property."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 2:
            raise exceptions.Unauthorized

        property_obj = await self.property_repository.get_or_404(property_id)
        property_obj.deactivate()
        await self.property_repository.commit()
        return {
            "detail": "Property deactivated",
        }

    async def get_properties(
            self,
            token: TokenData,
            page: int,
            elements: int,
            ) -> Sequence[Property]:
        """Get properties."""
        user_obj = await self.user_repository.get_or_401(token.user_id)
        level = user_obj.level

        if level < 1:
            raise exceptions.Unauthorized

        return await self.property_repository.get_properties_page(
            elements, (page - 1) * elements, [])
