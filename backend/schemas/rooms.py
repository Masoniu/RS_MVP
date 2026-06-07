from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

from schemas.users import UserResponse


class RoomCreate(BaseModel):
    name: str

class RoomJoin(BaseModel):
    invite_code: str

class RoomResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    status: str
    creator_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserShortResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class RouteData(BaseModel):
    locations: list[Any]
    budget: float
    radius_km: float

class RoomDetailResponse(BaseModel):
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