from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas.users import UserCreate, UserResponse
from services.security import get_password_hash

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

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

    # Зберігаємо в базу даних
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user