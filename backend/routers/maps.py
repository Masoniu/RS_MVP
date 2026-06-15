"""
File: routers/maps.py

Router for managing map route candidates and saving finalized walking paths inside rooms.

Responsible for:
- retrieving categorized location candidates near specified coordinates using external geographical services
- clearing old route permutations and persisting user-selected path arrays bound to specific trip instances
- verifying active room lifecycles before granting write or fetch access to routing metrics
"""

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
    """
    Fetches raw category candidate pools (parks, cafes, museums) around center points for a room.

    Args:
        room_id (int): Primary key identifier matching the targeted room entity.
        lat (float): Latitude coordinate component for the target area center point.
        lon (float): Longitude coordinate component for the target area center point.
        radius_km (float): Search perimeter bounds defined in kilometer values.
        db (Session): Database engine session query execution context.
        current_user (models.User): Authenticated user footprint claiming read authorization.

    Returns:
        dict: Categorized structural map arrays matching the RouteCandidatesResponse payload spec.

    Raises:
        HTTPException(404): If the requested room index cannot be resolved in active tables.
        HTTPException(400): If the tracking state properties have already shifted to archived status.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Кімнату не знайдено")

    if room.status == "finished":
        raise HTTPException(status_code=400, detail="Кімната архівована")

    #Upstream calls reach out via business logic handlers to pull coordinate-validated elements
    candidates = await get_route_candidates(radius_km, lat, lon, db)
    return candidates


@router.post("/{room_id}/save-route", response_model=RouteResponse)
def save_final_route(
        room_id: int,
        payload: SaveRouteRequest,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Overwrites old active routes for a room and commits a new chosen sequence array layout.

    Args:
        room_id (int): Primary tracking identity integer of the related trip room row.
        payload (SaveRouteRequest): Input schema mapping target locations, structural budget, and scope radius.
        db (Session): Database persistence connector transaction instance runner.
        current_user (models.User): Authenticated profile executing target route alterations.

    Returns:
        models.Route: The newly initialized and persisted database route record state object.
    """
    #Explicit clean execution step to prevent multiple parallel route records existing for one room
    db.query(models.Route).filter(models.Route.room_id == room_id).delete()

    #Convert list metadata into raw JSON lists to store compound points safely within unified table schemas
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