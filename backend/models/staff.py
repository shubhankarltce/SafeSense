"""
SafeSense — Staff Model
"""
from sqlalchemy import Column, String, DateTime
from backend.database import Base
from datetime import datetime, timezone


class Staff(Base):
    __tablename__ = "staff"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # security, floor_manager, general_staff, admin
    status = Column(String, default="idle")  # idle, notified, responding, on_scene, completed
    assigned_zone = Column(String, nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    contact = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "assigned_zone": self.assigned_zone,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "contact": self.contact,
        }
