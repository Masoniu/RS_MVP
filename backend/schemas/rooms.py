from pydantic import BaseModel
from datetime import datetime

class RoomCreate(BaseModel):
    name: str

class RoomResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    status: str
    creator_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class RoomJoin(BaseModel):
    invite_code: str