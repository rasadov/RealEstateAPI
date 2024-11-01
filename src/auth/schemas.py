from typing import Optional
from pydantic import BaseModel

class UserRegisterSchema(BaseModel):
    email: str
    password: str

class UserLoginSchema(BaseModel):
    email: str
    password: str

class TokenData(BaseModel):
    user_id: int
    email: Optional[str] = None
    sub: Optional[str] = None