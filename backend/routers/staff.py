"""
SafeSense — Staff Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.staff import Staff
from backend.websocket.ws_manager import manager

router = APIRouter(prefix="/api/staff", tags=["staff"])


class StaffStatusUpdate(BaseModel):
    status: str  # notified | responding | on_scene | completed


@router.get("")
async def get_staff(db: Session = Depends(get_db)):
    """Get all staff and their current status."""
    staff = db.query(Staff).all()
    return [s.to_dict() for s in staff]


@router.patch("/{staff_id}/status")
async def update_staff_status(staff_id: str, body: StaffStatusUpdate, db: Session = Depends(get_db)):
    """Update staff response status."""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        return {"error": "Staff not found"}

    staff.status = body.status
    staff.last_updated = datetime.now(timezone.utc)
    db.commit()

    await manager.broadcast("staff_status_update", {
        "staff_id": staff.id,
        "name": staff.name,
        "role": staff.role,
        "status": staff.status,
    })

    return staff.to_dict()
