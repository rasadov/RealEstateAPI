from dataclasses import dataclass
from fastapi.responses import JSONResponse, Response
from httpx import AsyncClient

from src.auth import exceptions
from src.auth import utils
from src.auth import oauth2
from src.user.service import UserService
from src.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

@dataclass
class AuthService:
    """Auth service"""

    userService: UserService


    async def login(self, username: str, password: str) -> dict:
        """Login user"""
        user = await self.userService.get_user_by_email(username)

        if user is None or not utils.verify_password(password, user.password_hash):
            raise exceptions.InvalidCredentials

        return await self.authenticate(user.email)

    async def authenticate(self, username: str) -> dict:
        """Authenticate user"""

        user = await self.userService.get_user_by_email(username)
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

    @staticmethod
    async def refresh_token(response: Response, user_id: int) -> dict:
        """Refresh token"""
        access_token = oauth2.create_access_token(data={"user_id": user_id})
        response.set_cookie("access_token", access_token)
        return {"message": "Token refreshed"}

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
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
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

        new_user = await self.userService.register(user_info.get("email"), "")
        return await self.authenticate(new_user.email)
