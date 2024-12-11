from typing import Optional

from pydantic import BaseModel

class UserRegisterSchema(BaseModel):
    email: str
    password: str

class UserLoginSchema(BaseModel):
    email: str
    password: str

class EmailSchema(BaseModel):
    email: str

class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str

class ResetPasswordSchema(BaseModel):
    password: str

class UpdateUserSchema(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class UpdateAgentSchema(UpdateUserSchema):
    serial_number: Optional[str] = None
    company: Optional[str] = None
    experience: Optional[float] = None

class ReviewSchema(BaseModel):
    agent_id: int
    rating: int
    comment: Optional[str] = None
