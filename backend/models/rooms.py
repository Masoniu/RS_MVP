"""
File: models/rooms.py

ORM models for trip rooms and their participants.

Room       — "shared trip" entity; has a status (active / finished)
             and a unique 6-character invitation code.
RoomMember — Many-to-Many junction table linking Room and User.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Room(Base):
    """
    Trip room entity.

    Attributes:
        id (int): Primary key.
        name (str): Name of the room specified at creation.
        creator_id (int): FK → users.id; user who created the room.
        invite_code (str): Unique 6-character code used to join.
        status (str): Current room state — "active" or "finished".
        created_at (datetime): Creation timestamp (UTC).
        creator (User): ORM relationship with the User model.
    """

    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invite_code = Column(String(6), unique=True, index=True, nullable=False)
    status = Column(String, default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    creator = relationship("User")


class RoomMember(Base):
    """
    Room participant junction model (Room ↔ User).

    Uses a composite primary key (room_id + user_id) to prevent 
    duplicate records for the same user in a single room.

    Attributes:
        room_id (int): FK → rooms.id.
        user_id (int): FK → users.id.
        joined_at (datetime): Join timestamp (UTC).
    """

    __tablename__ = "room_members"

    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)