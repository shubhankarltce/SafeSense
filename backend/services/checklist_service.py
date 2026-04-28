"""
SafeSense — Checklist Service
Auto-generates response checklists based on detection type.
"""

CHECKLISTS = {
    "fire_smoke": [
        {"id": 1, "text": "Call fire department (dial 101)", "checked": False},
        {"id": 2, "text": "Activate fire suppression if available", "checked": False},
        {"id": 3, "text": "Evacuate affected floor immediately", "checked": False},
        {"id": 4, "text": "Ensure elevators are not used", "checked": False},
        {"id": 5, "text": "Account for all guests in zone", "checked": False},
        {"id": 6, "text": "Security to hold exits open", "checked": False},
    ],
    "person_down": [
        {"id": 1, "text": "Call medical emergency (dial 108)", "checked": False},
        {"id": 2, "text": "Clear area around person", "checked": False},
        {"id": 3, "text": "Do not move person unless danger present", "checked": False},
        {"id": 4, "text": "Staff trained in first aid to respond", "checked": False},
        {"id": 5, "text": "Log incident with timestamp", "checked": False},
    ],
    "crowd_panic": [
        {"id": 1, "text": "Security to affected zone immediately", "checked": False},
        {"id": 2, "text": "PA announcement for calm", "checked": False},
        {"id": 3, "text": "Open all available exits", "checked": False},
        {"id": 4, "text": "Floor manager to visible position", "checked": False},
        {"id": 5, "text": "Begin controlled evacuation", "checked": False},
    ],
    "hazard": [
        {"id": 1, "text": "Identify hazard type", "checked": False},
        {"id": 2, "text": "Cordon off affected area", "checked": False},
        {"id": 3, "text": "Notify maintenance team", "checked": False},
        {"id": 4, "text": "Guide guests away from hazard", "checked": False},
        {"id": 5, "text": "Document hazard with photos", "checked": False},
    ],
}


def get_checklist(detection_type: str):
    """Get the checklist for a given detection type."""
    import copy
    template = CHECKLISTS.get(detection_type, CHECKLISTS.get("hazard"))
    return copy.deepcopy(template)
