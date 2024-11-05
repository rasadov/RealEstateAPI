from dataclasses import dataclass

from src.auth import exceptions
from src.user.repository import UserRepository
from src.user.schemas import UserRegisterSchema
from src.user.models import User

@dataclass
class UserService:
    """User service"""

    userRepository: UserRepository

    async def get_or_404(self, user_id: int) -> User:
        """Get user by id"""
        user = await self.userRepository.get_or_404(user_id)
        return user
    
    async def get_or_401(self, user_id: int) -> User:
        """Get user by id or raise 401"""
        user = await self.userRepository.get_or_401(user_id)
        return user

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        user = await self.userRepository.get_user_by(email=email)
        return user

    async def register(self, user: UserRegisterSchema) -> dict:
        """Register user"""
        user_exists = await self.userRepository.get_user_by(email=user.email)
        if user_exists:
            raise exceptions.EmailAlreadyTaken

        new_user = User(
            email=user.email,
            password_hash=user.password,
        )
        await self.userRepository.add(new_user)
        await self.userRepository.commit()
        await self.userRepository.refresh(new_user)

        return {
            "message": "User created successfully",
            "email": new_user.email,
            "user_id": new_user.id,
            "role": new_user.role
        }
