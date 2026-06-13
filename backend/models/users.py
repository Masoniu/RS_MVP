from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    google_linked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)