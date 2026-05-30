from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LocationItem(BaseModel):
    osm_id: str
    name: str
    lat: float
    lon: float
    price: float
    category: str

class RouteCandidatesResponse(BaseModel):
    parks: List[LocationItem]
    museums: List[LocationItem]
    cafes: List[LocationItem]

class SaveRouteRequest(BaseModel):
    budget: float
    radius_km: float
    locations: List[LocationItem]

class RouteResponse(BaseModel):
    id: int
    room_id: int
    budget: float
    radius_km: float
    locations: List[LocationItem]
    created_at: datetime

    class Config:
        from_attributes = True