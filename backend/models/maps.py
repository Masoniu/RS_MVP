from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, default="Новий маршрут")
    created_at = Column(DateTime, default=datetime.utcnow)
    locations = relationship("Location", cascade="all, delete-orphan")

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    order_index = Column(Integer, nullable=False, default=0)

class OSMCache(Base):
    __tablename__ = "osm_cache"

    id = Column(Integer, primary_key=True, index=True)
    query_key = Column(String, unique=True, index=True, nullable=False)
    response_data = Column(JSON, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow)