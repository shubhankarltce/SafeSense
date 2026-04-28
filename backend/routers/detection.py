"""
SafeSense — Detection Router
Receives detection events from the AI pipeline.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.incident import Incident
from backend.models.zone import Zone
from backend.services.alert_service import dispatch_alert
from backend.services.voice_service import get_severity_from_type

router = APIRouter(prefix="/api/detection", tags=["detection"])

# In-memory pipeline status
pipeline_status = {
    "active": True,
    "cameras_online": 4,
    "last_event": None,
}


class DetectionEvent(BaseModel):
    zone: str
    floor: str
    detection_type: str  # fire_smoke | person_down | crowd_panic | hazard
    confidence: float
    frame_count: int = 5
    guest_count: int = 0
    timestamp: Optional[str] = None


@router.post("/event")
async def receive_detection_event(event: DetectionEvent, db: Session = Depends(get_db)):
    """Receive a detection event from the AI pipeline and trigger alert dispatch."""
    severity = get_severity_from_type(event.detection_type)

    # Create incident record
    incident = Incident(
        zone=event.zone,
        floor=event.floor,
        detection_type=event.detection_type,
        severity=severity,
        confidence=event.confidence,
        guest_count_affected=event.guest_count,
        frame_count=event.frame_count,
        status="active",
    )
    db.add(incident)

    # Update zone status
    zone = db.query(Zone).filter(Zone.id == event.zone.lower().replace(" ", "_")).first()
    if zone:
        zone.status = "danger" if severity in ("critical", "high") else "warning"
        zone.guest_count = event.guest_count
        zone.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)

    # Update pipeline status
    pipeline_status["last_event"] = datetime.now(timezone.utc).isoformat()

    # Dispatch alerts via WebSocket
    alert_result = await dispatch_alert(incident.to_dict(), db)

    return {
        "status": "triggered",
        "incident_id": incident.id,
        "alert_sent": True,
        "severity": severity,
        "voice_message": alert_result.get("voice_message"),
    }


@router.get("/status")
async def get_detection_status():
    """Get current detection pipeline status."""
    return pipeline_status
