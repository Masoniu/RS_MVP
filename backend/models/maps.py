"""
File: models/maps.py

ORM models related to mapping and routes.

LocationPrice — Custom admission prices for specific OSM objects.
OSMCache — Overpass API response cache (24-hour expiration).
Route — Saved walking route configuration for a specific room.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from datetime import datetime, timedelta
from database import Base


class LocationPrice(Base):
    """
    Custom entrance fee configuration for a specific OSM object.

    If a record exists, it overrides category default prices in the routing service.

    Attributes:
        osm_id (str): Unique OSM object identifier formatted as "type/id" 
                      (e.g., "node/123456789"). Primary key.
        name (str): Name of the object (for administrative reference).
        category (str): Object category — "park", "museum", or "cafe".
        entry_price (float): Entry fee in UAH (0.0 = free).
        notes (str | None): Optional administrator remarks.
        updated_at (datetime): Timestamp of the last record update.
    """

    __tablename__ = "location_prices"

    osm_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False, default=0.0)
    notes = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OSMCache(Base):
    """
    Cached response payload from the Overpass API.

    The cache key is formatted as "osm_{lat}_{lon}_{radius_km}".
    The entry is considered valid as long as expires_at > utcnow().

    Attributes:
        id (int): Primary key.
        cache_key (str): Unique string identifier for the query.
        response (dict): Full JSON response dictionary from Overpass ("elements" node).
        lat (float): Latitude coordinate of the query center.
        lng (float): Longitude coordinate of the query center.
        radius_km (float): Search radius limit in kilometers.
        expires_at (datetime): Cache expiration timestamp (UTC).
    """

    __tablename__ = "osm_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, index=True, nullable=False)
    response = Column(JSON, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=24))


class Route(Base):
    """
    Saved walking route configuration associated with a specific room.

    Enforces a strict 1:1 ratio per room; saving a new route deletes the old one.
    Locations are stored as a JSON array to maintain a flat database structure for the MVP.

    Attributes:
        id (int): Primary key.
        room_id (int): FK → rooms.id; the room this route belongs to.
        locations (list[dict]): List of route items matching the LocationItem structure
                                (osm_id, name, lat, lon, price, category).
        budget (float): Total walking budget constraint in UAH.
        radius_km (float): Search radius scale used during generation.
        created_at (datetime): Timestamp when the route was saved (UTC).
    """

    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    locations = Column(JSON, nullable=False)
    budget = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)