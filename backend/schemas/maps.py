"""
File: schemas/maps.py

Pydantic schemas for map lookups and route configurations.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LocationItem(BaseModel):
    """Standardized representation of a single map location point."""

    osm_id: str
    name: str
    lat: float
    lon: float
    price: float
    category: str

class RouteCandidatesResponse(BaseModel):
    """Response payload enclosing grouped swipe-card data arrays."""

    parks: List[LocationItem]
    museums: List[LocationItem]
    cafes: List[LocationItem]

class SaveRouteRequest(BaseModel):
    """Request payload enclosing chosen location cards to save as a route."""

    budget: float
    radius_km: float
    locations: List[LocationItem]

class RouteResponse(BaseModel):
    """Response tracking a successfully synchronized room route record."""

    id: int
    room_id: int
    budget: float
    radius_km: float
    locations: List[LocationItem]
    created_at: datetime

    class Config:
        from_attributes = True