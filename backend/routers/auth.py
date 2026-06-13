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
from services.security import get_current_user

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
    try:
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(body.token, requests.Request(), GOOGLE_CLIENT_ID)

        email = idinfo.get('email')
        name = idinfo.get('name', email.split('@')[0])
        picture = idinfo.get('picture')

        if not email:
            raise HTTPException(status_code=400, detail="Email не знайдено в Google токені")

        user = db.query(models.User).filter(models.User.email == email).first()

        if not user:
            user = models.User(
                email=email,
                name=name,
                password_hash="",
                avatar_url=picture,
                google_linked=True
            )
            db.add(user)
        else:
            user.google_linked = True
            if picture and not user.avatar_url:
                user.avatar_url = picture

        db.commit()
        db.refresh(user)

        token_data = {
            "sub": str(user.id),
            "name": user.name,
            "email": user.email,
            "avatar": user.avatar_url,
            "google_linked": user.google_linked
        }

        return {
            "access_token": create_access_token(data=token_data),
            "refresh_token": create_refresh_token(data={"sub": str(user.id)}),
            "token_type": "bearer"
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Невірний Google токен: {str(e)}")

@router.post("/link-google", response_model=Token)
def link_google(
        body: GoogleTokenRequest,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    try:
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(body.token, requests.Request(), GOOGLE_CLIENT_ID)

        google_email = idinfo.get('email')
        if google_email != current_user.email:
            pass

        picture = idinfo.get('picture')
        current_user.google_linked = True
        if picture:
            current_user.avatar_url = picture

        db.commit()
        db.refresh(current_user)

        token_data = {
            "sub": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email,
            "avatar": current_user.avatar_url,
            "google_linked": current_user.google_linked
        }

        return {
            "access_token": create_access_token(data=token_data),
            "refresh_token": create_refresh_token(data={"sub": str(current_user.id)}),
            "token_type": "bearer"
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Помилка верифікації Google")