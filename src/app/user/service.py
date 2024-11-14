from dataclasses import dataclass

from app.base.utils import send_email
from app.auth import exceptions
from app.user.repository import UserRepository
from app.user.models import User
from app.auth import oauth2

@dataclass
class UserService:
    """User service"""

    userRepository: UserRepository

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        user = await self.userRepository.get_user_by(email=email)
        return user

    async def change_password(self, id: int, old_password: str, new_password: str) -> dict:
        """Change user password"""
        user = await self.userRepository.get_or_401(id)
        if not user or not user.verify_password(old_password):
            raise exceptions.InvalidCredentials

        user.change_password(new_password)
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

    async def reset_password(self, token: str, password: str) -> dict:
        """Reset user password"""
        user_id = oauth2.verify_action_token(token,
                                             oauth2.AuthTokenTypes.FORGOT_PASSWORD,
                                             exceptions.CredentialsException)
        if user_id is None:
            raise exceptions.InvalidToken

        user = await self.userRepository.get_or_401(user_id)
        user.change_password(password)
        await self.userRepository.commit()

        return {"message": "Password reset successfully"}

    async def send_confirm_email(self, email: str) -> dict:
        """Send confirm email"""
        user = await self.userRepository.get_user_by(email=email)
        if user is None:
            raise exceptions.UserNotFound

        token = oauth2.create_confirm_email_token(user.id)
        send_email(
            email,
            "Confirm email",
            f"Click on the link to confirm your email: /confirm-email?token={token}" # TO DO: Add frontend URL
        )

        return {"message": "Email sent with email confirmation instructions"}

    async def confirm_email(self, token: str) -> dict:
        """Confirm user email"""
        user_id = oauth2.verify_action_token(token,
                                             oauth2.AuthTokenTypes.CONFIRM_EMAIL,
                                             exceptions.CredentialsException)
        if user_id is None:
            raise exceptions.InvalidToken

        user = await self.userRepository.get_or_401(user_id)
        user.confirm_email()
        await self.userRepository.commit()

        return {"message": "Email confirmed successfully"}
