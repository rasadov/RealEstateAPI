from dataclasses import dataclass
from fastapi.responses import JSONResponse, Response
from fastapi import Request
from httpx import AsyncClient

from src.auth.utils import hash_password
from src.auth import exceptions
from src.auth import oauth2
from src.user.models import User
from src.user.service import UserService
from src.config import Settings

@dataclass
class AuthService:
    """Auth service"""

    userService: UserService

    @staticmethod
    async def _parse_token(request: Request, tokenType: str) -> dict:
        """Parse token from request"""
        token = request.cookies.get("access_token")
        if not token:
            raise exceptions.TokenNotFound
        return oauth2.verify_action_token(token, tokenType, exceptions.CredentialsException)

    async def authenticate(self, email: str) -> dict:
        """Authenticate user"""

        user = await self.userService.get_user_by_email(email)
        tokens = oauth2.generate_auth_tokens(user.id)

        response = JSONResponse(content={
            "message": "Login successful",
            "email": user.email,
            "user_id": user.id,
            "role": user.role,
        })
        response.set_cookie("access_token", tokens["access_token"])
        response.set_cookie("refresh_token", tokens["refresh_token"])

        return response

    async def login(self, email: str, password: str) -> dict:
        """Login user"""
        user = await self.userService.get_user_by_email(email)

        if user is None or not user.verify_password(password):
            raise exceptions.InvalidCredentials

        return await self.authenticate(user.email)

    async def register(self, payload : dict) -> dict:
        """Register user"""
        user_exists = await self.userService.userRepository.get_user_by(email=payload.get("email"))
        if user_exists:
            raise exceptions.EmailAlreadyTaken

        new_user = User(
            email=payload.get("email"),
            password_hash=hash_password(payload.get("password")),
        )
        await self.userService.userRepository.add(new_user)
        await self.userService.userRepository.commit()
        await self.userService.userRepository.refresh(new_user)

        return await self.authenticate(new_user.email)

    async def refresh_tokens(self, request: Request) -> dict:
        """Refresh token"""
        user_id = await self._parse_token(request, "refresh_token")
        user = self.userService.userRepository.get_or_401(user_id)
        tokens = oauth2.generate_auth_tokens(user.id)

        response = JSONResponse(content={"message": "Token refreshed"})
        response.set_cookie("access_token", tokens["access_token"])
        response.set_cookie("refresh_token", tokens["refresh_token"])

        return response

    @staticmethod
    async def logout(response: Response) -> dict:
        """Logout user"""
        response.delete_cookie("access_token")
        return {"message": "Logged out successfully"}

    async def auth_google(self, code: str) -> dict:
        """Authenticate user with Google"""
        token_url = "https://accounts.google.com/o/oauth2/token"
        data = {
            "code": code,
            "client_id": Settings.GOOGLE_CLIENT_ID,
            "client_secret": Settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": Settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        async with AsyncClient() as client:
            response = await client.post(token_url, data=data)
            access_token = response.json().get("access_token")
            user_info_response = await client.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                                headers={"Authorization": f"Bearer {access_token}"})

        if user_info_response.status_code != 200:
            raise exceptions.FailedToGetUserInfo

        user_info = user_info_response.json()
        user = await self.userService.get_user_by_email(user_info.get("email"))

        if user:
            return await self.authenticate(user.email)
        
        regitration_data = {
            "email": user_info.get("email"),
            "password": "",
        }

        return await self.register(regitration_data)
