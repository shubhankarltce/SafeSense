"""
SafeSense — Incident Model
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from backend.database import Base
from datetime import datetime, timezone
import uuid


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    zone = Column(String, nullable=False)
    floor = Column(String, nullable=False)
    detection_type = Column(String, nullable=False)  # fire_smoke, person_down, crowd_panic, hazard
    severity = Column(String, nullable=False, default="medium")  # low, medium, high, critical
    confidence = Column(Float, default=0.0)
    guest_count_affected = Column(Integer, default=0)
    response_time = Column(Float, nullable=True)  # seconds
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    staff_assigned = Column(String, nullable=True)
    status = Column(String, default="active")  # active, resolved
    frame_count = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "zone": self.zone,
            "floor": self.floor,
            "detection_type": self.detection_type,
            "severity": self.severity,
            "confidence": self.confidence,
            "guest_count_affected": self.guest_count_affected,
            "response_time": self.response_time,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "notes": self.notes,
            "staff_assigned": self.staff_assigned,
            "status": self.status,
            "frame_count": self.frame_count,
        }
