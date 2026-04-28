"""
SafeSense — Zone Model
"""
from sqlalchemy import Column, String, Integer, DateTime
from backend.database import Base
from datetime import datetime, timezone


class Zone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    floor = Column(String, nullable=False)
    status = Column(String, default="safe")  # safe, warning, danger
    guest_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_by = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "floor": self.floor,
            "status": self.status,
            "guest_count": self.guest_count,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "updated_by": self.updated_by,
        }
