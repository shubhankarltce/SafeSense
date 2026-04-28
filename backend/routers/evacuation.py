"""
SafeSense — Evacuation Router
Dynamic safe path calculation based on zone danger status.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.zone import Zone

router = APIRouter(prefix="/api/evacuation", tags=["evacuation"])

# Floor plan graph: zone connections and exits
ZONE_GRAPH = {
    "zone_a": {"neighbors": ["zone_b", "zone_c"], "exits": ["Exit A"]},
    "zone_b": {"neighbors": ["zone_a", "zone_d", "zone_e"], "exits": ["Exit C"]},
    "zone_c": {"neighbors": ["zone_a", "zone_d"], "exits": ["Exit B"]},
    "zone_d": {"neighbors": ["zone_b", "zone_c", "zone_f"], "exits": ["Exit D"]},
    "zone_e": {"neighbors": ["zone_b", "zone_f"], "exits": ["Exit A", "Exit B"]},
    "zone_f": {"neighbors": ["zone_d", "zone_e"], "exits": ["Exit C"]},
}


def find_safe_routes(danger_zones: list) -> list:
    """Calculate safe evacuation routes avoiding danger zones using BFS."""
    routes = []
    all_zones = list(ZONE_GRAPH.keys())
    safe_zones = [z for z in all_zones if z not in danger_zones]

    for zone_id in all_zones:
        # Find shortest path to any exit avoiding danger zones
        if zone_id in danger_zones:
            # Even danger zones need evacuation routes
            pass

        best_route = bfs_to_exit(zone_id, danger_zones)
        if best_route:
            routes.append(best_route)

    return routes


def bfs_to_exit(start_zone: str, danger_zones: list) -> dict:
    """BFS to find shortest safe path from a zone to the nearest exit."""
    from collections import deque

    queue = deque([(start_zone, [start_zone])])
    visited = set()

    while queue:
        current, path = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        zone_info = ZONE_GRAPH.get(current, {})
        exits = zone_info.get("exits", [])

        if exits and current not in danger_zones:
            return {
                "from_zone": start_zone,
                "to_exit": exits[0],
                "path": path,
                "status": "clear",
            }

        for neighbor in zone_info.get("neighbors", []):
            if neighbor not in visited and neighbor not in danger_zones:
                queue.append((neighbor, path + [neighbor]))

    # No safe route found — return blocked
    zone_info = ZONE_GRAPH.get(start_zone, {})
    return {
        "from_zone": start_zone,
        "to_exit": zone_info.get("exits", ["Unknown"])[0] if zone_info.get("exits") else "Unknown",
        "path": [start_zone],
        "status": "blocked",
    }


@router.get("/routes")
async def get_evacuation_routes(db: Session = Depends(get_db)):
    """Get current safe evacuation routes based on zone status."""
    zones = db.query(Zone).all()
    danger_zones = [z.id for z in zones if z.status == "danger"]
    safe_zones = [z.id for z in zones if z.status == "safe"]
    warning_zones = [z.id for z in zones if z.status == "warning"]

    routes = find_safe_routes(danger_zones)

    return {
        "safe_zones": safe_zones,
        "warning_zones": warning_zones,
        "danger_zones": danger_zones,
        "routes": routes,
    }
