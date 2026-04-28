"""
SafeSense — Zones Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.zone import Zone
from backend.websocket.ws_manager import manager

router = APIRouter(prefix="/api/zones", tags=["zones"])


class ZoneStatusUpdate(BaseModel):
    status: str  # safe | warning | danger
    updated_by: Optional[str] = None


@router.get("")
async def get_zones(db: Session = Depends(get_db)):
    """Get all zones with current status."""
    zones = db.query(Zone).all()
    return [z.to_dict() for z in zones]


@router.get("/{zone_id}/status")
async def get_zone_status(zone_id: str, db: Session = Depends(get_db)):
    """Get specific zone status."""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        return {"error": "Zone not found"}
    return zone.to_dict()


@router.patch("/{zone_id}/status")
async def update_zone_status(zone_id: str, body: ZoneStatusUpdate, db: Session = Depends(get_db)):
    """Manually override zone status."""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        return {"error": "Zone not found"}

    zone.status = body.status
    zone.updated_by = body.updated_by
    zone.last_updated = datetime.now(timezone.utc)
    db.commit()

    await manager.broadcast("zone_status_update", {
        "zone": zone.name,
        "zone_id": zone.id,
        "status": zone.status,
        "guest_count": zone.guest_count,
    })

    return zone.to_dict()
