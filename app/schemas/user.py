from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    is_writer: bool = False

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_writer: bool
    created_at: datetime

    class Config:
        from_attributes = True

# NEW: Profile Update Schema
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None

# NEW: Public Profile Schema
class UserProfilePublic(BaseModel):
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    is_writer: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None