"""
SafeSense — FastAPI Main Entry Point
AI-powered real-time emergency detection and coordinated response system.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import init_db, SessionLocal
from backend.models.zone import Zone
from backend.models.staff import Staff
from backend.websocket.ws_manager import manager
from backend.routers import detection, incidents, zones, alerts, staff, evacuation


# Seed data for zones and staff
SEED_ZONES = [
    {"id": "zone_a", "name": "Zone A", "floor": "Floor 1", "status": "safe", "guest_count": 12},
    {"id": "zone_b", "name": "Zone B", "floor": "Floor 2", "status": "safe", "guest_count": 8},
    {"id": "zone_c", "name": "Zone C", "floor": "Floor 1", "status": "safe", "guest_count": 15},
    {"id": "zone_d", "name": "Zone D", "floor": "Floor 2", "status": "safe", "guest_count": 6},
    {"id": "zone_e", "name": "Zone E", "floor": "Floor 3", "status": "safe", "guest_count": 20},
    {"id": "zone_f", "name": "Zone F", "floor": "Floor 3", "status": "safe", "guest_count": 10},
]

SEED_STAFF = [
    {"id": "staff_001", "name": "Raj Kumar", "role": "security", "status": "idle", "contact": "+91-9876543210"},
    {"id": "staff_002", "name": "Priya Sharma", "role": "floor_manager", "status": "idle", "contact": "+91-9876543211"},
    {"id": "staff_003", "name": "Amit Patel", "role": "security", "status": "idle", "contact": "+91-9876543212"},
    {"id": "staff_004", "name": "Sneha Reddy", "role": "general_staff", "status": "idle", "contact": "+91-9876543213"},
    {"id": "staff_005", "name": "Vikram Singh", "role": "floor_manager", "status": "idle", "contact": "+91-9876543214"},
    {"id": "staff_006", "name": "Ananya Das", "role": "general_staff", "status": "idle", "contact": "+91-9876543215"},
    {"id": "staff_007", "name": "Rohan Mehta", "role": "admin", "status": "idle", "contact": "+91-9876543216"},
    {"id": "staff_008", "name": "Kavita Joshi", "role": "security", "status": "idle", "contact": "+91-9876543217"},
]


def seed_database():
    """Seed database with initial zones and staff."""
    db = SessionLocal()
    try:
        # Seed zones if empty
        if db.query(Zone).count() == 0:
            for z in SEED_ZONES:
                db.add(Zone(**z))
            print("[DB] Seeded zones")

        # Seed staff if empty
        if db.query(Staff).count() == 0:
            for s in SEED_STAFF:
                db.add(Staff(**s))
            print("[DB] Seeded staff")

        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    print("=" * 50)
    print("  SafeSense — Starting Up")
    print("  AI-Powered Emergency Response System")
    print("=" * 50)
    init_db()
    seed_database()
    print("[OK] Database initialized and seeded")
    print("[OK] WebSocket manager ready")
    print("[OK] API routes registered")
    print(f"[OK] Server running at http://localhost:8000")
    print(f"[OK] API docs at http://localhost:8000/docs")
    print("=" * 50)
    yield
    print("[SHUTDOWN] SafeSense shutting down...")


app = FastAPI(
    title="SafeSense API",
    description="AI-powered real-time emergency detection and coordinated response system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(detection.router)
app.include_router(incidents.router)
app.include_router(zones.router)
app.include_router(alerts.router)
app.include_router(staff.router)
app.include_router(evacuation.router)


# WebSocket endpoint for live dashboard
@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket connection for live dashboard updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            # Echo back for keep-alive or handle client commands
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    return {
        "system": "SafeSense",
        "version": "1.0.0",
        "status": "operational",
        "tagline": "AI-powered real-time emergency detection and coordinated response",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "safesense-backend"}
