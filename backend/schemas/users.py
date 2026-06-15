"""
File: schemas/users.py

Pydantic schemas for authentication and user profile endpoints.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """Input schema for new user registration."""
    email: EmailStr
    password: str
    name: str

class UserResponse(BaseModel):
    """API response schema containing public user details (excludes password_hash)."""

    id: int
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    """JWT token pair returned after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str

class TokenRefreshRequest(BaseModel):
    """Request body for POST /auth/refresh."""

    refresh_token: str

class UpdateProfile(BaseModel):
    """Schema for partial profile updates; missing fields remain unchanged."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None

class ChangePassword(BaseModel):
    """Request body for password updates requiring validation."""

    current_password: str
    new_password: str