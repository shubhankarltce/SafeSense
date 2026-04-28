"""
SafeSense — Demo Simulator
Sends simulated detection events to the backend for demo/testing.
Run this script to simulate a full emergency scenario.
"""
import asyncio
import aiohttp
import json
import time
from datetime import datetime, timezone

API_BASE = "http://localhost:8000"

DEMO_SCENARIOS = [
    {
        "delay": 3,
        "event": {
            "zone": "Zone B",
            "floor": "Floor 2",
            "detection_type": "fire_smoke",
            "confidence": 0.87,
            "frame_count": 5,
            "guest_count": 8,
        },
        "description": "🔥 Fire detected in Zone B, Floor 2",
    },
    {
        "delay": 15,
        "event": {
            "zone": "Zone A",
            "floor": "Floor 1",
            "detection_type": "person_down",
            "confidence": 0.73,
            "frame_count": 30,
            "guest_count": 12,
        },
        "description": "🚑 Person down in Zone A, Floor 1",
    },
    {
        "delay": 25,
        "event": {
            "zone": "Zone D",
            "floor": "Floor 2",
            "detection_type": "crowd_panic",
            "confidence": 0.81,
            "frame_count": 10,
            "guest_count": 6,
        },
        "description": "🚨 Crowd panic in Zone D, Floor 2",
    },
]


async def run_demo():
    """Run the full demo scenario sequence."""
    print("=" * 60)
    print("  SafeSense — Demo Simulator")
    print("  Sending simulated emergency events to backend")
    print("=" * 60)
    print()

    async with aiohttp.ClientSession() as session:
        # Check backend health
        try:
            async with session.get(f"{API_BASE}/api/health") as resp:
                if resp.status == 200:
                    print("[✓] Backend is healthy")
                else:
                    print("[✗] Backend not responding. Start it first!")
                    return
        except aiohttp.ClientConnectorError:
            print("[✗] Cannot connect to backend at localhost:8000")
            print("    Run: uvicorn backend.main:app --reload --port 8000")
            return

        print()
        print("[▶] Starting demo scenario...")
        print()

        for i, scenario in enumerate(DEMO_SCENARIOS):
            delay = scenario["delay"] if i > 0 else 2
            print(f"[⏳] Waiting {delay}s before next event...")
            await asyncio.sleep(delay)

            print(f"[→] {scenario['description']}")

            async with session.post(
                f"{API_BASE}/api/detection/event",
                json=scenario["event"],
                headers={"Content-Type": "application/json"},
            ) as resp:
                result = await resp.json()
                print(f"    Status: {result.get('status')}")
                print(f"    Incident ID: {result.get('incident_id')}")
                print(f"    Severity: {result.get('severity')}")
                if result.get("voice_message"):
                    print(f"    🔊 Voice: {result['voice_message']}")
                print()

        print("=" * 60)
        print("  Demo complete! Check the dashboard for live updates.")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
