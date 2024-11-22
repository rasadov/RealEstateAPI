from dataclasses import dataclass

from fastapi.responses import JSONResponse, Response
from fastapi import Request
from httpx import AsyncClient

from src.auth.utils import hash_password
from src.auth import exceptions
from src.auth import oauth2
from src.user.models import User, Agent
from src.user.service import UserService
from src.config import Settings

@dataclass
class AuthService:
    """Auth service"""

    user_service: UserService

    @staticmethod
    def _parse_token(
            request: Request,
            tokenType: str,
            ) -> int:
        """Parse token from request"""
        token = request.cookies.get(tokenType)
        if not token:
            raise exceptions.TokenNotFound
        return oauth2.verify_action_token(
            token,
            tokenType,
            exceptions.CredentialsException,
            )

    async def authenticate(
            self,
            email: str,
            ) -> JSONResponse:
        """Authenticate user"""

        user = await self.user_service.get_user_by_email(email)
        tokens = oauth2.generate_auth_tokens(user.id)

        response = JSONResponse(content={
            "detail": "Login successful",
            "email": user.email,
            "user_id": user.id,
            "level": user.level,
        })
        response.set_cookie(
            "access_token",
            tokens["access_token"]
            )
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"]
            )

        return response

    async def login(
            self,
            email: str,
            password: str,
            ) -> JSONResponse:
        """Login user"""
        user = await self.user_service.get_user_by_email(email)

        if user is None or not user.verify_password(password):
            raise exceptions.InvalidCredentials

        return await self.authenticate(user.email)

    async def register(
            self,
            payload : dict,
            ) -> JSONResponse:
        """Register user"""
        user_exists = await self.user_service.userRepository.get_user_by(
            email=payload.get("email"))
        if user_exists:
            raise exceptions.EmailAlreadyTaken

        new_user = User(
            name=payload.get("name"),
            email=payload.get("email"),
            password_hash=hash_password(payload.get("password"))
        )
        self.user_service.userRepository.add(new_user)
        await self.user_service.userRepository.commit()
        await self.user_service.userRepository.refresh(new_user)
        if payload.get("role") == "agent":
            await self._register_agent(
                new_user,
                payload.get("serial_number")
                )

        return await self.authenticate(new_user.email)

    async def _register_agent(
            self,
            user: User,
            serial_number: str,
            ) -> None:
        """Register agent"""
        if not serial_number:
            raise exceptions.InvalidSerialNumber
        agent = Agent(user.id, serial_number)
        self.user_service.userRepository.add(agent)
        await self.user_service.userRepository.commit()

    async def refresh_tokens(
            self,
            request: Request,
            ) -> JSONResponse:
        """Refresh token"""
        user_id = self._parse_token(request, oauth2.AuthTokenTypes.REFRESH)
        user = await self.user_service.userRepository.get_or_401(user_id)
        tokens = oauth2.generate_auth_tokens(user.id)

        response = JSONResponse(content={
            "detail": "Token refreshed",
            })
        response.set_cookie(
            "access_token",
            tokens["access_token"]
            )
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"]
            )

        return response

    @staticmethod
    async def logout(response: Response) -> dict:
        """Logout user"""
        response.delete_cookie("access_token")
        return {"detail": "Logged out successfully"}

    async def auth_google(self, code: str) -> JSONResponse:
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
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"})

        if user_info_response.status_code != 200:
            raise exceptions.FailedToGetUserInfo

        user_info = user_info_response.json()
        user = await self.user_service.get_user_by_email(
            user_info.get("email"))

        if user:
            return await self.authenticate(user.email)

        regitration_data = {
            "email": user_info.get("email"),
            "password": "",
        }

        return await self.register(regitration_data)
