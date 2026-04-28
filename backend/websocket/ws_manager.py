"""
SafeSense — WebSocket Connection Manager
Handles real-time dashboard updates via WebSocket.
"""
from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio


class ConnectionManager:
    """Manages WebSocket connections for live dashboard updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcast event to all connected dashboard clients."""
        message = json.dumps({"event": event_type, "data": data})
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, event_type: str, data: Dict[str, Any]):
        """Send event to a specific client."""
        message = json.dumps({"event": event_type, "data": data})
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)


# Singleton instance
manager = ConnectionManager()
