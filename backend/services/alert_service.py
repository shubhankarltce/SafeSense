"""
SafeSense — Alert Service
Handles alert dispatch, role-based routing, and notification coordination.
"""
from backend.websocket.ws_manager import manager
from backend.services.voice_service import generate_voice_message, get_severity_from_type
from backend.services.checklist_service import get_checklist
from datetime import datetime, timezone


# In-memory state for active incident tracking
active_checklists = {}


async def dispatch_alert(incident_data: dict, db=None):
    """
    Full alert dispatch pipeline:
    1. Determine severity
    2. Generate voice message
    3. Get checklist
    4. Broadcast to dashboard via WebSocket
    """
    detection_type = incident_data.get("detection_type", "hazard")
    zone = incident_data.get("zone", "Unknown")
    floor = incident_data.get("floor", "Unknown")
    incident_id = incident_data.get("id", "unknown")

    severity = get_severity_from_type(detection_type)
    voice_message = generate_voice_message(detection_type, zone, floor)
    checklist = get_checklist(detection_type)

    # Store active checklist
    active_checklists[incident_id] = checklist

    # Broadcast new incident to all dashboard clients
    await manager.broadcast("new_incident", {
        "incident": incident_data,
        "severity": severity,
        "voice_message": voice_message,
    })

    # Broadcast zone status update
    await manager.broadcast("zone_status_update", {
        "zone": zone,
        "floor": floor,
        "status": "danger" if severity in ("critical", "high") else "warning",
    })

    # Broadcast checklist
    await manager.broadcast("checklist_update", {
        "incident_id": incident_id,
        "detection_type": detection_type,
        "checklist": checklist,
    })

    # Broadcast alert triggered
    await manager.broadcast("alert_triggered", {
        "incident_id": incident_id,
        "zone": zone,
        "floor": floor,
        "type": detection_type,
        "severity": severity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "voice_message": voice_message,
    })

    # Determine role-based alerts
    role_alerts = get_role_alerts(detection_type, zone, floor, incident_data.get("guest_count", 0))
    await manager.broadcast("staff_status_update", {
        "incident_id": incident_id,
        "role_alerts": role_alerts,
    })

    return {
        "severity": severity,
        "voice_message": voice_message,
        "checklist_items": len(checklist),
        "alerts_sent": True,
    }


def get_role_alerts(detection_type: str, zone: str, floor: str, guest_count: int) -> dict:
    """Generate role-specific alert information."""
    return {
        "security": {
            "alert_type": "critical",
            "info": f"Emergency in {zone}, {floor}. Type: {detection_type}. Guests in zone: {guest_count}",
        },
        "floor_manager": {
            "alert_type": "high",
            "info": f"Zone {zone} status changed. Evacuation checklist triggered.",
        },
        "general_staff": {
            "alert_type": "medium",
            "info": f"Emergency active. Stand by for instructions. Avoid {zone}.",
        },
    }
