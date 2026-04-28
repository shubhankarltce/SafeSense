"""
SafeSense — Incidents Router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.incident import Incident
from backend.websocket.ws_manager import manager

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


class ResolveBody(BaseModel):
    resolved_by: str
    notes: Optional[str] = None


@router.get("")
async def get_incidents(
    limit: int = Query(50, ge=1, le=200),
    zone: Optional[str] = None,
    type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all logged incidents with optional filters."""
    query = db.query(Incident).order_by(Incident.timestamp.desc())
    if zone:
        query = query.filter(Incident.zone == zone)
    if type:
        query = query.filter(Incident.detection_type == type)
    if from_date:
        query = query.filter(Incident.timestamp >= from_date)
    if to_date:
        query = query.filter(Incident.timestamp <= to_date)
    incidents = query.limit(limit).all()
    return [i.to_dict() for i in incidents]


@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get single incident details."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"error": "Incident not found"}
    return incident.to_dict()


@router.patch("/{incident_id}/resolve")
async def resolve_incident(incident_id: str, body: ResolveBody, db: Session = Depends(get_db)):
    """Mark incident as resolved."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"error": "Incident not found"}

    incident.status = "resolved"
    incident.resolved_at = datetime.now(timezone.utc)
    incident.resolved_by = body.resolved_by
    incident.notes = body.notes
    if incident.timestamp:
        incident.response_time = (datetime.now(timezone.utc) - incident.timestamp).total_seconds()
    db.commit()

    await manager.broadcast("incident_resolved", incident.to_dict())

    return {
        "status": "resolved",
        "resolved_at": incident.resolved_at.isoformat(),
    }
