from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# ... -> represents required field
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=72, description="Password of at least 8 characters and max 72 characters")

class UserLogin(BaseModel):
    # username: Optional[str] = Field(None, description="Username (if email is not provided)")
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., description="Plain password")

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None