from dataclasses import dataclass
from typing import Sequence

from fastapi import UploadFile

from src.base.utils import send_email
from src.auth import exceptions
from src.user.repository import UserRepository
from src.user.models import User, Agent, UserProfileImage
from src.auth import oauth2

@dataclass
class UserService:
    """User service"""

    user_repository: UserRepository

    async def get_user_by_email(
            self,
            email: str,
            ) -> User:
        """Get user by email"""
        user = await self.user_repository.get_user_by(email=email)
        return user
    
    async def get_user(
            self,
            id: int,
            ) -> dict:
        """Get user"""
        user = await self.user_repository.get_or_401(id)
        return user.dict()

    async def get_agents_page(
            self,
            page: int,
            elements: int,
            ) -> Sequence[Agent]:
        """Get agents page"""
        return await self.user_repository.get_users_page_by()

    async def upload_image(
            self,
            user_id: int,
            image: UploadFile,
            ) -> dict:
        """Upload user image"""
        user = await self.user_repository.get_or_401(user_id)

        existing_images = await self.user_repository.get_user_profile_images(user.id)

        # Delete each existing image both from storage and the database
        for old_image in existing_images:
            try:
                # Delete the image file from storage
                await self.user_repository.staticFilesManager.delete(old_image.image_url)
            except Exception as e:
                # Optionally log the error or handle failure to delete from storage
                print(f"Error deleting file {old_image.image_url}: {e}")
            # Remove the image record from the database
            await self.user_repository.delete(old_image)

        # Commit deletions (you might want to commit after each delete if necessary)
        await self.user_repository.commit()

        url = await self.user_repository.staticFilesManager.upload(
            image,
            f"users/{user.id}/{image.filename}"
            )
        new_profile_image = UserProfileImage(
            user_id=user.id,
            image_url=url,
        )
        self.user_repository.add(new_profile_image)
        await self.user_repository.commit()
        return {"image_url": url}

    async def add_review(
            self,
            current_user_id: int,
            agent_id: int,
            rating: int,
            comment: str,
            ) -> dict:
        """Post comment"""
        user = await self.user_repository.get_or_401(current_user_id)
        agent = await self.user_repository.get_agent_by_or_404(id=agent_id)
        if user.id == agent.user_id:
            raise exceptions.InvalidReview
        
        await self.user_repository.add_review(user.id, agent.id, rating, comment)
        
        return {"detail": "Comment added successfully"}

    async def change_password(
            self,
            id: int,
            old_password: str,
            new_password: str,
            ) -> dict:
        """Change user password"""
        user = await self.user_repository.get_or_401(id)
        if not user.verify_password(old_password):
            raise exceptions.InvalidCredentials

        user.change_password(new_password)
        await self.user_repository.commit()

        return {"detail": "Password changed successfully"}

    async def forgot_password(
            self,
            email: str,
            ) -> dict:
        """Forgot password"""
        user = await self.user_repository.get_user_by(email=email)
        print(user)
        if user is None:
            raise exceptions.UserNotFound

        token = oauth2.create_forgot_password_token(user.id)
        send_email(
            email,
            "Forgot password",
            f"Click on the link to reset your password: /reset-password?token={token}",
        )
        return {"detail": "Email sent with password reset instructions"}

    async def reset_password(
            self,
            token: str,
            password: str,
            ) -> dict:
        """Reset user password"""
        user_id = oauth2.verify_action_token(
            token,
            oauth2.AuthTokenTypes.FORGOT_PASSWORD,
            exceptions.CredentialsException,
            )
        if user_id is None:
            raise exceptions.InvalidToken

        user = await self.user_repository.get_or_401(user_id)
        user.change_password(password)
        await self.user_repository.commit()

        return {"detail": "Password reset successfully"}

    async def send_confirm_email(
            self,
            email: str,
            ) -> dict:
        """Send confirm email"""
        user = await self.user_repository.get_user_by(email=email)
        if user is None:
            raise exceptions.UserNotFound

        token = oauth2.create_confirm_email_token(user.id)
        send_email(
            email,
            "Confirm email",
            f"Click on the link to confirm your email: /confirm-email?token={token}" # TO DO: Add frontend URL
        )

        return {"detail": "Email sent with email confirmation instructions"}

    async def confirm_email(
            self,
            token: str,
            ) -> dict:
        """Confirm user email"""
        user_id = oauth2.verify_action_token(
            token,
            oauth2.AuthTokenTypes.CONFIRM_EMAIL,
            exceptions.CredentialsException,
            )
        if user_id is None:
            raise exceptions.InvalidToken

        user = await self.user_repository.get_or_401(user_id)
        user.confirm_email()
        await self.user_repository.commit()

        return {"detail": "Email confirmed successfully"}
    
    async def update_user(
            self,
            id: int,
            payload: dict,
            ) -> dict:
        """Update user"""
        user = await self.user_repository.get_or_401(id)
        user.update_user(payload)
        await self.user_repository.commit()

        return {"detail": "User updated successfully"}

    async def update_agent(
            self,
            id: int,
            payload: dict,
            ) -> dict:
        """Update agent"""
        user = await self.user_repository.get_agent_by_or_404(user_id=id)
        user.update_agent(payload)
        await self.user_repository.commit()
        
        return {"detail": "Agent updated successfully"}

    async def delete_user(
            self,
            current_user_id: int,
            ) -> dict:
        """Delete user"""
        current_user = await self.user_repository.get_or_401(current_user_id)

        await self.user_repository.delete(current_user)
        await self.user_repository.commit()
        return {
            "detail": "User deleted successfully"
            }
