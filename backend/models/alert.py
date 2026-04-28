"""
SafeSense — Alert Model
"""
from sqlalchemy import Column, String, DateTime, Boolean
from backend.database import Base
from datetime import datetime, timezone
import uuid


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    zone = Column(String, nullable=False)
    floor = Column(String, nullable=True)
    alert_type = Column(String, nullable=False)  # fire, medical, panic, custom
    severity = Column(String, default="medium")
    triggered_by = Column(String, nullable=True)  # staff ID or "system"
    incident_id = Column(String, nullable=True)
    is_manual = Column(Boolean, default=False)
    message = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "zone": self.zone,
            "floor": self.floor,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "triggered_by": self.triggered_by,
            "incident_id": self.incident_id,
            "is_manual": self.is_manual,
            "message": self.message,
        }
