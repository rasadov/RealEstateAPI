from dataclasses import dataclass

from src.base.utils import send_email
from src.auth import exceptions
from src.user.repository import UserRepository
from src.user.schemas import UserRegisterSchema
from src.user.models import User
from src.auth.utils import hash_password
from src.auth import oauth2

@dataclass
class UserService:
    """User service"""

    userRepository: UserRepository

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
            password_hash=hash_password(user.password),
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

    async def change_password(self, id: int, old_password: str, new_password: str) -> dict:
        """Change user password"""
        user = await self.userRepository.get_or_401(id)
        if not user or not user.verify_password(old_password):
            raise exceptions.InvalidCredentials

        user.password_hash = hash_password(new_password)
        await self.userRepository.commit()

        return {"message": "Password changed successfully"}

    async def forgot_password(self, email: str) -> dict:
        """Forgot password"""
        user = await self.userRepository.get_user_by(email=email)
        if user is None:
            raise exceptions.UserNotFound

        token = oauth2.create_forgot_password_token(user.id)
        send_email(
            email,
            "Forgot password",
            f"Click on the link to reset your password: /reset-password?token={token}"
        )

        return {"message": "Email sent with password reset instructions"}
