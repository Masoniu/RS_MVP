from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import random
import string

from database import get_db
import models
from services.security import get_current_user
from fastapi import HTTPException
from schemas.rooms import RoomCreate, RoomResponse, RoomJoin

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)


def generate_invite_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
        room: RoomCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    invite_code = generate_invite_code()
    new_room = models.Room(
        name=room.name,
        creator_id=current_user.id,
        invite_code=invite_code
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    room_member = models.RoomMember(
        room_id=new_room.id,
        user_id=current_user.id
    )
    db.add(room_member)
    db.commit()

    return new_room


@router.post("/join", status_code=status.HTTP_200_OK)
def join_room(
        join_data: RoomJoin,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room = db.query(models.Room).filter(models.Room.invite_code == join_data.invite_code).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кімнату з таким кодом не знайдено"
        )

    existing_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room.id,
        models.RoomMember.user_id == current_user.id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ви вже є учасником цієї кімнати"
        )

    new_member = models.RoomMember(
        room_id=room.id,
        user_id=current_user.id
    )
    db.add(new_member)
    db.commit()

    return {
        "message": "Успішно приєднано до кімнати",
        "room_id": room.id,
        "room_name": room.name
    }