from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import random
import string

from database import get_db
import models
from schemas.rooms import RoomCreate, RoomResponse
from services.security import get_current_user

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