"""
File: routers/rooms.py

Router for room management, memberships, and debt settlements.

Responsible for:
- generating distinct alphanumeric invite codes for shared tracking instances
- creating trip rooms and automatically attaching the resource creator to membership lists
- verifying invite tokens and preventing duplicate member entries inside specific pools
- fetching detailed room data scopes, including aggregated balance records and debt solutions
- protecting operational status updates by enforcing administrative creator permissions
"""

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
    """
    Generates a random uppercase alphanumeric string for room invites.

    Args:
        length (int): The desired character length of the generated code. Defaults to 6.

    Returns:
        str: A randomized alphanumeric string.
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
        room: RoomCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Creates a new trip room and automatically adds the creator as its first member.

    Args:
        room (RoomCreate): Schema containing initialization data like the room name.
        db (Session): Database session instance for persistence.
        current_user (models.User): Authenticated user entity initiating the creation.

    Returns:
        models.Room: The newly created database room record object.
    """
    invite_code = generate_invite_code()
    new_room = models.Room(
        name=room.name,
        creator_id=current_user.id,
        invite_code=invite_code
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    #The creator must be tracked inside room_members to access shared statistics
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
    """
    Adds an authenticated user to an existing room using a valid invite code string.

    Args:
        join_data (RoomJoin): Schema holding the unique alphanumeric invite token.
        db (Session): Database session instance for query and mutation executions.
        current_user (models.User): Authenticated user entity attempting to join.

    Returns:
        dict: A confirmation payload containing a descriptive message, room identity, and room name.

    Raises:
        HTTPException(404): If no active room matches the provided invite token.
        HTTPException(400): If the target user profile is already mapped as a participant or if the room is finished.
    """
    room = db.query(models.Room).filter(models.Room.invite_code == join_data.invite_code).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кімнату з таким кодом не знайдено"
        )

    if room.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ця прогулянка вже завершена. До неї неможливо приєднатися."
        )

    #Database lookup checks existing table references to block duplicate memberships
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
    """
    Fetches all distinct room structures the authenticated caller is linked to as a participant.

    Args:
        db (Session): Database session query operator instance.
        current_user (models.User): Authenticated user model holding identity limits.

    Returns:
        list[models.Room]: A list of aggregated room entities sorted descending by creation timestamps.
    """
    #Inner join bridges relational associations between User entities and Group data sets
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
    """
    Returns absolute room configuration specs, active route maps, and detailed participant list arrays.

    Args:
        room_id (int): Primary structural tracking key of the target room row.
        db (Session): Database session transaction instance.
        current_user (models.User): Authenticated user profile asserting read permissions.

    Returns:
        dict: A fully mapped layout matching the fields required by RoomDetailResponse schema.

    Raises:
        HTTPException(404): If no target room entity matches the provided integer primary key.
        HTTPException(403): If the authenticated user is not authenticated as a valid group participant.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кімнату не знайдено"
        )

    #Strict relationship guard matches metadata records to ensure safe data isolation
    is_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не є учасником цієї кімнати. Доступ заборонено."
        )

    #Database selection extracting all individual profiles linked to this shared space
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
    """
    Retrieves the current asymmetric debt/credit ledger state indices for all distinct room members.

    Args:
        room_id (int): Unique primary identification integer of the target room.
        db (Session): Database operation layer pipeline runner.
        current_user (models.User): Authenticated participant querying for financial records.

    Returns:
        dict: A collection tracking room identification alongside nested structural member balance maps.

    Raises:
        HTTPException(403): If the authenticated profile is not registered as an active room participant.
    """
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
    """
    Calculates an optimized transaction checklist to completely resolve current group debts.

    Args:
        room_id (int): Database key indicator reference to extract ledger balances from.
        db (Session): Database transaction engine instance executor.
        current_user (models.User): Authenticated user session requesting calculations.

    Returns:
        list[SettlementResponse]: Minimized sequence list instructions denoting who pays whom and how much.

    Raises:
        HTTPException(403): If the caller lacks authorization markers as an established room member.
    """
    room_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()
    if not room_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ви не є учасником цієї кімнати")

    #Pull raw ledger points first, then pass them into the calculator to resolve minimum transfer paths
    balances = get_room_balances(room_id, db)
    settlements = calculate_settlements(balances)

    return settlements


@router.post("/{room_id}/finish")
def finish_room(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Closes an active trip room, freezes operational metrics, and marks the instance as archived.

    Args:
        room_id (int): Primary column locator key specifying the structural entity record.
        db (Session): Database persistence provider session instance.
        current_user (models.User): Authenticated operator verifying validation permissions.

    Returns:
        dict: Success message showing completion status details.

    Raises:
        HTTPException(404): If the requested room instance row identifier is missing.
        HTTPException(403): If the executor's identity value does not match the room creator field data.
        HTTPException(400): If the tracking status state parameter has already been flag changed to finished.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кімнату не знайдено")

    #Enforce administrative authorization; regular members cannot freeze room metrics
    if room.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Тільки творець може завершити поїздку")

    if room.status == "finished":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Кімната вже завершена")

    room.status = "finished"
    db.commit()

    return {"message": "Поїздку завершено, кімнату архівовано"}