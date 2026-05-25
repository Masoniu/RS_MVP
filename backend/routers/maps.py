from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas.maps import RouteGenerateRequest, RouteResponse
from services.security import get_current_user
from services.routing import generate_route

router = APIRouter(
    prefix="/rooms",
    tags=["Maps"]
)


@router.post("/{room_id}/route", response_model=RouteResponse)
async def create_room_route(
        room_id: int,
        request: RouteGenerateRequest,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room_member = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()

    if not room_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не є учасником цієї кімнати"
        )

    locations_array = await generate_route(
        budget=request.budget,
        radius_km=request.radius_km,
        lat=request.latitude,
        lon=request.longitude,
        db=db
    )
    db.query(models.Route).filter(models.Route.room_id == room_id).delete()
    new_route = models.Route(
        room_id=room_id,
        budget=request.budget,
        radius_km=request.radius_km,
        locations=locations_array
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)

    return new_route