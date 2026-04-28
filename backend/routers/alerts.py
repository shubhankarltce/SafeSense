"""
SafeSense — Alerts Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.alert import Alert
from backend.models.incident import Incident
from backend.services.alert_service import dispatch_alert
from backend.services.voice_service import get_severity_from_type

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class ManualAlert(BaseModel):
    zone: str
    floor: Optional[str] = "Floor 1"
    type: str  # fire | medical | panic | custom
    triggered_by: str


@router.post("/manual")
async def trigger_manual_alert(body: ManualAlert, db: Session = Depends(get_db)):
    """Manually trigger an alert (panic button)."""
    type_map = {"fire": "fire_smoke", "medical": "person_down", "panic": "crowd_panic", "custom": "hazard"}
    detection_type = type_map.get(body.type, "hazard")
    severity = get_severity_from_type(detection_type)

    # Create incident
    incident = Incident(
        zone=body.zone,
        floor=body.floor,
        detection_type=detection_type,
        severity=severity,
        confidence=1.0,
        status="active",
    )
    db.add(incident)

    # Create alert record
    alert = Alert(
        zone=body.zone,
        floor=body.floor,
        alert_type=body.type,
        severity=severity,
        triggered_by=body.triggered_by,
        incident_id=incident.id,
        is_manual=True,
        message=f"Manual {body.type} alert triggered by {body.triggered_by}",
    )
    db.add(alert)
    db.commit()
    db.refresh(incident)

    await dispatch_alert(incident.to_dict(), db)

    return {"status": "alert_sent", "incident_id": incident.id, "alert_id": alert.id}


@router.get("/history")
async def get_alert_history(db: Session = Depends(get_db)):
    """Get alert history."""
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(100).all()
    return [a.to_dict() for a in alerts]
