from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas.maps import RouteCandidatesResponse, SaveRouteRequest, RouteResponse
from services.security import get_current_user
from services.routing import get_route_candidates

router = APIRouter(prefix="/rooms", tags=["Maps & Routes"])


@router.post("/{room_id}/route-candidates", response_model=RouteCandidatesResponse)
async def fetch_candidates(
        room_id: int,
        lat: float,
        lon: float,
        radius_km: float,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Кімнату не знайдено")

    if room.status == "finished":
        raise HTTPException(status_code=400, detail="Кімната архівована")

    candidates = await get_route_candidates(radius_km, lat, lon, db)
    return candidates


@router.post("/{room_id}/save-route", response_model=RouteResponse)
def save_final_route(
        room_id: int,
        payload: SaveRouteRequest,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    db.query(models.Route).filter(models.Route.room_id == room_id).delete()

    new_route = models.Route(
        room_id=room_id,
        budget=payload.budget,
        radius_km=payload.radius_km,
        locations=[loc.model_dump() for loc in payload.locations]
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    return new_route