from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class RouteGenerateRequest(BaseModel):
    budget: float
    radius_km: float
    latitude: float
    longitude: float

class RouteResponse(BaseModel):
    id: int
    room_id: int
    budget: float
    radius_km: float
    locations: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True