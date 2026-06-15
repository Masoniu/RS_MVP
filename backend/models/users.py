"""
File: models/users.py

ORM model representing a system user.

The "users" table stores account data, supporting both standard registration
(email + password) and Google OAuth2 authentication.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from database import Base


class User(Base):
    """
    User account data model.

    Attributes:
        id (int): Primary key, auto-incremented.
        email (str): Unique email address used as the login identifier.
        password_hash (str): Bcrypt password hash. Empty for Google accounts.
        name (str): Display name of the user.
        avatar_url (str | None): Profile avatar image URL.
        google_linked (bool): True if the account is linked via Google OAuth2.
        created_at (datetime): Account registration timestamp (UTC).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    google_linked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)