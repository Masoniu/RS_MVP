"""
File: services/security.py

Security service: password hashing, JWT token generation and validation,
and the FastAPI dependency for retrieving the currently authenticated user.

Environment variables (.env):
    SECRET_KEY               -- secret used to sign access tokens
    REFRESH_SECRET_KEY       -- secret used to sign refresh tokens
    ALGORITHM                -- signing algorithm (default: HS256)
    REFRESH_TOKEN_EXPIRE_DAYS -- lifetime of a refresh token in days (default: 7)
"""

import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from database import get_db
import models

# bcrypt hashing context for passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secrets and token parameters are read from the environment
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "default_refresh_secret")

# Access token lifetime (short-lived — 15 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Refresh token lifetime (long-lived — 7 days by default)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password (str): the password in plain text.

    Returns:
        str: a bcrypt hash suitable for storing in the database.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare a plain-text password against a bcrypt hash.

    Args:
        plain_password (str): the password entered by the user.
        hashed_password (str): the hash stored in the database.

    Returns:
        bool: True if the password matches; False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """
    Create a short-lived JWT access token.

    Clones the data dict, appends an "exp" (expiry) field,
    and signs it with SECRET_KEY.

    Args:
        data (dict): token payload.
                     Required field: "sub" (user_id as a string).
                     Recommended fields: "name", "email", "avatar", "google_linked".

    Returns:
        str: a signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# OAuth2 scheme — FastAPI will look for a Bearer token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI dependency: decodes the Bearer token and returns the current user.

    Used via Depends(get_current_user) in protected route handlers.
    Raises HTTP 401 for any token error or if the user is not found in the DB.

    Args:
        token (str): JWT access token from the Authorization: Bearer <token> header.
        db (Session): database session injected by FastAPI.

    Returns:
        models.User: ORM object of the authenticated user.

    Raises:
        HTTPException(401): if the token is missing, invalid, expired,
                            or the user no longer exists in the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не вдалося перевірити токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived JWT refresh token.
 
    Clones the data dict, appends "exp" and "type": "refresh" fields,
    and signs it with REFRESH_SECRET_KEY to prevent token-type confusion attacks.
 
    Args:
        data (dict): token payload. Required field: "sub" (user_id as a string).
 
    Returns:
        str: a signed JWT refresh string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt