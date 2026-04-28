"""
SafeSense — Voice Service
Generates context-aware voice messages for emergency guidance.
"""

MESSAGE_TEMPLATES = {
    "fire_smoke": "Fire confirmed on {floor}, {zone}. {exit_info}. Guide guests to the nearest stairwell immediately. Do not use elevators.",
    "person_down": "Person down detected in {zone}, {floor}. Medical team report to {zone} now. Clear the surrounding area.",
    "crowd_panic": "Crowd disturbance detected in {zone}, {floor}. Security proceed to {zone}. All other staff hold positions and await instructions.",
    "hazard": "Hazard detected in {zone}, {floor}. Maintenance team report immediately. Staff guide guests away from the area.",
}

EXIT_MAP = {
    "Zone A": "Exit A is clear",
    "Zone B": "Exit C is clear",
    "Zone C": "Exit B is clear",
    "Zone D": "Exit D is clear",
    "Zone E": "Exit A and Exit B are clear",
    "Zone F": "Exit C is clear",
}


def generate_voice_message(detection_type: str, zone: str, floor: str) -> str:
    """Generate a context-aware voice message based on the detection event."""
    template = MESSAGE_TEMPLATES.get(detection_type, MESSAGE_TEMPLATES["hazard"])
    exit_info = EXIT_MAP.get(zone, "Follow nearest illuminated exit signs")
    return template.format(zone=zone, floor=floor, exit_info=exit_info)


def get_severity_from_type(detection_type: str) -> str:
    """Determine severity level from detection type."""
    severity_map = {
        "fire_smoke": "critical",
        "person_down": "high",
        "crowd_panic": "critical",
        "hazard": "medium",
    }
    return severity_map.get(detection_type, "medium")
