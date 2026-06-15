"""
File: schemas/rooms.py

Pydantic schemas for trip room management endpoints.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from schemas.users import UserResponse


class RoomCreate(BaseModel):
    """Input schema for creating a trip room."""

    name: str

class RoomJoin(BaseModel):
    """Input schema for joining a room using an invitation code."""

    invite_code: str

class RoomResponse(BaseModel):
    """Brief summary representation of a room used in collection lists."""

    id: int
    name: str
    invite_code: str
    status: str
    creator_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserShortResponse(BaseModel):
    """Abbreviated public information of a room member."""

    id: int
    name: str
    email: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class RouteData(BaseModel):
    """Embedded active route configuration parameters within room details."""

    locations: list[Any]
    budget: float
    radius_km: float

class RoomDetailResponse(BaseModel):
    """Comprehensive details of a room returned by GET /rooms/{id}."""

    id: int
    name: str
    invite_code: str
    status: str
    creator_id: int
    created_at: datetime
    members: list[UserResponse]
    route: Optional[RouteData] = None

class Config:
    from_attributes = True