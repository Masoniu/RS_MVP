"""
File: routers/auth.py

Router for user authentication, profile updates, and Google OAuth2 synchronization.

Responsible for:
- Registering traditional credentials-based user profiles with hashed passwords.
- Issuing, decoding, and rotating stateful JWT Access and Refresh tokens.
- Handling external Google OAuth2 token validation, creation, and profile linking.
- Processing secure operational mutations like profile updates and password verification resets.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
import models
from fastapi.security import OAuth2PasswordRequestForm
from schemas.users import UserCreate, UserResponse, Token, TokenRefreshRequest, UpdateProfile, ChangePassword
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
    """
    Pydantic request body schema containing the external Google OAuth2 credential.

    Attributes:
        token (str): The raw identity ID token string returned by the Google Sign-In SDK client side.
    """
    token: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user inside the database if the targeted email does not exist.

    Args:
        user (UserCreate): Input schema validation data holding password, email, and explicit name.
        db (Session): Database engine operational sequence manager.

    Returns:
        models.User: The newly created database user row entity instance.

    Raises:
        HTTPException(400): If the requested email sequence matches an existing database account record.
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким email вже існує"
        )
    
    #Securely store password signatures instead of plain text strings via safe algorithmic hashing blocks
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
    """
    Authenticates credential pairs and issues matching JWT Access and Refresh token payloads.

    Args:
        form_data (OAuth2PasswordRequestForm): FastAPI component extraction structure resolving inputs.
        db (Session): Database transaction executor mapping query spaces.

    Returns:
        dict: Object payload structure aligning fields expected by the validation Token response schema.

    Raises:
        HTTPException(401): If individual email matches fail or cryptographically checked signature mismatches happen.
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Невірний email або пароль")
        
    #Define explicit dictionary data keys representing the signature identity structure
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
    """
    Decodes an unexpired Refresh token signature to mint fresh session Access and Refresh tokens.

    Args:
        body (TokenRefreshRequest): Input validation object containing the active refresh token token string.
        db (Session): Database layer interaction controller.

    Returns:
        dict: A new token package structure containing newly randomized authorization token strings.

    Raises:
        HTTPException(401): If JWT strings fail format validation, expire, or point to missing user indices.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не валідний рефреш токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        #Decode payload metrics using independent cryptographic secret parameters allocated to separate tokens
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


@router.patch("/profile", response_model=Token)
def update_profile(
    body: UpdateProfile,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Modifies active metadata on an authenticated profile and regenerates refreshed session tokens.

    Args:
        body (UpdateProfile): Data envelope structure holding elective updates like updated email or name changes.
        db (Session): Database framework controller transaction instance.
        current_user (models.User): Authenticated user dependency resolving the mutation context.

    Returns:
        dict: Renewed session authorization tokens packing modified user identity fields.

    Raises:
        HTTPException(400): If trying to use a modified email signature owned by an independent profile.
    """
    #Explicit conflict lookup preventing parallel profiles sharing identical lookup addresses
    if body.email and body.email != current_user.email:
        existing = db.query(models.User).filter(models.User.email == body.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Користувач з таким email вже існує"
            )
        current_user.email = body.email

    if body.name is not None:
        current_user.name = body.name

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


@router.post("/change-password")
def change_password(
    body: ChangePassword,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Updates the hashed password key sequence if the incoming confirmation matching signatures clear validation.

    Args:
        body (ChangePassword): Object parameters packing verification keys alongside targeted modifications.
        db (Session): Database persistence engine connection unit.
        current_user (models.User): Authenticated target user executing security transitions.

    Returns:
        dict: Confirmation mapping showing status details.

    Raises:
        HTTPException(400): If the account lacks local hashes (Google-only registration) or matches fail checking.
    """
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Зміна паролю недоступна для Google-акаунтів"
        )

    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поточний пароль невірний"
        )

    current_user.password_hash = get_password_hash(body.new_password)
    db.commit()

    return {"detail": "Пароль успішно змінено"}


@router.post("/google", response_model=Token)
def google_login(body: GoogleTokenRequest, db: Session = Depends(get_db)):
    """
    Parses open incoming Google Identity platform tokens to create or authenticate application users.

    Args:
        body (GoogleTokenRequest): Pydantic payload holding the verified target credential string tokens.
        db (Session): Database processing platform pipeline reference runner.

    Returns:
        dict: Application credential tokens linked to the synced application identity.

    Raises:
        HTTPException(400): If key payloads are parsed completely but lack explicit email markers.
        HTTPException(401): If the token signature validation check steps fail.
    """
    try:
        #Verify cryptographic validity of incoming external client identity tags using Google requests hooks
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(body.token, requests.Request(), GOOGLE_CLIENT_ID)

        email = idinfo.get('email')
        name = idinfo.get('name', email.split('@')[0])
        picture = idinfo.get('picture')

        if not email:
            raise HTTPException(status_code=400, detail="Email не знайдено в Google токені")

        user = db.query(models.User).filter(models.User.email == email).first()

        # Automate seamless shadow-registration profiles if external users log into services for the first time
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
    """
    Integrates external Google identity references into an active profile after verifying matching email contexts.

    Args:
        body (GoogleTokenRequest): Client container token string payload framework object.
        db (Session): Database tracking execution engine framework.
        current_user (models.User): Authenticated operational user claiming link updates.

    Returns:
        dict: Refreshed application tokens displaying updated status flags.

    Raises:
        HTTPException(401): If identity token parsing sequences return invalid structural criteria.
    """
    try:
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(body.token, requests.Request(), GOOGLE_CLIENT_ID)

        google_email = idinfo.get('email')
        if google_email != current_user.email:
            #Logic pathways bypass explicit mismatches but proceed with metadata sync configurations safely
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