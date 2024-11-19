from typing import Optional

from pydantic import BaseModel

class TokenData(BaseModel):
    user_id: int
    email: Optional[str] = None
    sub: Optional[str] = None
