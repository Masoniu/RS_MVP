from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

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

class RoomDetailResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    status: str
    creator_id: int
    created_at: datetime
    members: List[UserShortResponse]
    route: Optional[dict] = None

    class Config:
        from_attributes = True