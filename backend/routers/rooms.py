from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import random
import string

from database import get_db
import models
from services.security import get_current_user
from fastapi import HTTPException
from schemas.rooms import RoomCreate, RoomResponse, RoomJoin, RoomDetailResponse
from schemas.expenses import SettlementResponse
from services.settlements import get_room_balances, calculate_settlements

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


@router.get("/my", response_model=list[RoomResponse])
def get_my_rooms(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    rooms = (
        db.query(models.Room)
        .join(models.RoomMember, models.Room.id == models.RoomMember.room_id)
        .filter(models.RoomMember.user_id == current_user.id)
        .order_by(models.Room.created_at.desc())
        .all()
    )
    return rooms


@router.get("/{room_id}", response_model=RoomDetailResponse)
def get_room_details(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кімнату не знайдено"
        )

    is_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не є учасником цієї кімнати. Доступ заборонено."
        )

    room_members = db.query(models.User).join(
        models.RoomMember, models.User.id == models.RoomMember.user_id
    ).filter(models.RoomMember.room_id == room_id).all()

    route = db.query(models.Route).filter(models.Route.room_id == room_id).first()

    return {
        "id": room.id,
        "name": room.name,
        "invite_code": room.invite_code,
        "status": room.status,
        "creator_id": room.creator_id,
        "created_at": room.created_at,
        "members": room_members,
        "route": {
            "locations": route.locations,
            "budget": route.budget,
            "radius_km": route.radius_km
        } if route else None
    }


@router.get("/{room_id}/balances")
def get_balances(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()
    if not room_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ви не є учасником цієї кімнати")

    balances = get_room_balances(room_id, db)
    return {"room_id": room_id, "balances": balances}


@router.get("/{room_id}/settlements", response_model=list[SettlementResponse])
def get_final_settlements(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()
    if not room_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ви не є учасником цієї кімнати")

    balances = get_room_balances(room_id, db)
    settlements = calculate_settlements(balances)

    return settlements


@router.post("/{room_id}/finish")
def finish_room(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кімнату не знайдено")

    if room.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Тільки творець може завершити поїздку")

    if room.status == "finished":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Кімната вже завершена")

    room.status = "finished"
    db.commit()

    return {"message": "Поїздку завершено, кімнату архівовано"}