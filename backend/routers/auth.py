from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
import models
from fastapi.security import OAuth2PasswordRequestForm
from schemas.users import UserCreate, UserResponse, Token, TokenRefreshRequest
from services.security import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, REFRESH_SECRET_KEY, ALGORITHM
)
from pydantic import BaseModel
from google.auth.transport import requests
from google.oauth2 import id_token
import os

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class GoogleTokenRequest(BaseModel):
    token: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким email вже існує"
        )
    hashed_password = get_password_hash(user.password)

    new_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        name=user.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Невірний email або пароль")
        
    token_data = {
        "sub": str(user.id),
        "name": user.name,
        "email": user.email
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data={"sub": str(user.id)}) 

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_access_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не валідний рефреш токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(body.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    token_data = {
        "sub": str(user.id),
        "name": user.name,
        "email": user.email
    }
    new_access_token = create_access_token(data=token_data)
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/google", response_model=Token)
def google_login(body: GoogleTokenRequest, db: Session = Depends(get_db)):
    """
    Login with Google ID token
    """
    try:
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_CLIENT_ID не налаштований на сервері"
            )
        
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(body.token, requests.Request(), GOOGLE_CLIENT_ID)
        
        # Extract user info from token
        email = idinfo.get('email')
        name = idinfo.get('name', email.split('@')[0])
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email не знайдено в Google токені"
            )
        
        # Find or create user
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            # Create new user without password for Google auth
            user = models.User(
                email=email,
                name=name,
                password_hash=""  # Empty password for Google auth users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Generate tokens
        token_data = {
            "sub": str(user.id),
            "name": user.name,
            "email": user.email
        }
        
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Невірний Google токен: {str(e)}"
        )
    except Exception as e:
        print(f"Google login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка при верифікації Google токена"
        )
