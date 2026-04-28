"""
SafeSense — FastAPI Main Entry Point
AI-powered real-time emergency detection and coordinated response system.
"""
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from backend.database import init_db, SessionLocal
from backend.models.zone import Zone
from backend.models.staff import Staff
from backend.websocket.ws_manager import manager
from backend.routers import detection, incidents, zones, alerts, staff, evacuation

# --- Configuration & Constants ---

# Define the path to the frontend directory, assuming it's at the root of the project
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

# --- Database Seeding ---

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
    """Seed database with initial zones and staff if the tables are empty."""
    db = SessionLocal()
    try:
        if db.query(Zone).count() == 0:
            print("[DB] Seeding zones...")
            for z_data in SEED_ZONES:
                db.add(Zone(**z_data))
            db.commit()
            print("[DB] Zones seeded.")
        else:
            print("[DB] Zones table already populated.")

        if db.query(Staff).count() == 0:
            print("[DB] Seeding staff...")
            for s_data in SEED_STAFF:
                db.add(Staff(**s_data))
            db.commit()
            print("[DB] Staff seeded.")
        else:
            print("[DB] Staff table already populated.")
            
    finally:
        db.close()

# --- FastAPI Application Lifecycle ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    print("=" * 50)
    print("  SafeSense — Starting Up")
    print("  AI-Powered Emergency Response System")
    print("=" * 50)
    
    # Initialize database schema
    init_db()
    print("[OK] Database schema initialized.")

    # Seed the database with initial data
    seed_database()
    
    print("[OK] WebSocket manager ready.")
    print("[OK] API routes registered.")
    print(f"[OK] Serving frontend from: {os.path.abspath(FRONTEND_DIR)}")
    print(f"[OK] Server running at http://localhost:8000")
    print(f"[OK] API docs at http://localhost:8000/docs")
    print("=" * 50)
    
    yield
    
    print("\n" + "=" * 50)
    print("[SHUTDOWN] SafeSense is shutting down...")
    print("=" * 50)

# --- FastAPI App Instantiation ---

app = FastAPI(
    title="SafeSense API",
    description="AI-powered real-time emergency detection and coordinated response system",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware ---

# Update the CORS policy to allow the new frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://safesense.replit.app", "https://safesense-7ckn.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- API Routers ---

# Include all the API endpoint routers from the 'routers' directory
app.include_router(detection.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(staff.router, prefix="/api")
app.include_router(evacuation.router, prefix="/api")

# --- WebSocket Endpoint ---

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """Establish a WebSocket connection for the live dashboard."""
    await manager.connect(websocket)
    try:
        # Keep the connection alive and listen for any client messages
        while True:
            # Although we don't expect messages from the client in this design,
            # awaiting receive_text() is necessary to keep the connection open.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"[WebSocket] Client disconnected.")

# --- Static Files and Root Endpoint ---

# Mount the 'static' directory from the frontend to serve CSS, JS, etc.
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def read_index():
    """Serve the main index.html file for the root URL."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/api/health")
async def health_check():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "healthy", "service": "safesense-backend", "version": "1.0.0"}
