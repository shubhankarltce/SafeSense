import requests
import time
import random

# --- Configuration ---
BASE_URL = "http://localhost:8000"

# Health check endpoint
HEALTH_CHECK_URL = f"{BASE_URL}/api/health"

# Detection endpoint
DETECTION_URL = f"{BASE_URL}/api/detection/"

# List of possible zones for random alerts
ZONES = ["zone_a", "zone_b", "zone_c", "zone_d", "zone_e", "zone_f"]

# List of possible detection types
DETECTION_TYPES = ["fire", "smoke", "fire", "smoke", "fire"] # Skewed towards fire

# --- Helper Functions ---

def check_backend_health():
    """Check if the backend server is running and healthy."""
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("?? Backend is healthy and ready.")
            return True
        else:
            print(f"?? Backend is reachable but not healthy (Status: {response.status_code}). Response: {response.text}")
            return False
    except requests.ConnectionError:
        print("?? Backend connection failed. Is the server running?")
        return False
    except requests.Timeout:
        print("?? Backend health check timed out.")
        return False

def trigger_detection(zone_id: str, detection_type: str):
    """Send a detection event to the backend API."""
    payload = {
        "zone_id": zone_id,
        "detection_type": detection_type
    }
    try:
        response = requests.post(DETECTION_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"??  Successfully triggered '{detection_type}' alert in '{zone_id}'.")
            print(f"??  Response: {response.json().get('message')}")
        else:
            print(f"??  Failed to trigger alert. Status: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"??  API request failed: {e}")

# --- Main Simulation Logic ---

def run_simulation():
    """Run the main AI detection simulation."""
    print("=" * 50)
    print("?? SafeSense AI Demo Simulator Initializing...")
    print("=" * 50)

    # 1. Wait for the backend to be ready
    print("?? Waiting for backend server to become available...")
    while not check_backend_health():
        time.sleep(3)
    
    print("\n" + "-" * 50)

    # 2. Trigger a specific, predictable incident for demonstration
    print("?? Running initial scenario: Fire in Zone A (Lobby)")
    trigger_detection("zone_a", "fire")
    print("?? Initial scenario complete. Check the dashboard!")

    print("\n" + "-" * 50)
    print("?? Starting random event simulation loop (every 30-90s)...")
    print("?? Press Ctrl+C to stop the simulator.")
    print("-" * 50)

    # 3. Loop to trigger random incidents periodically
    try:
        while True:
            # Wait for a random interval before the next event
            sleep_duration = random.randint(30, 90)
            print(f"\n?? Next random event in {sleep_duration} seconds...")
            time.sleep(sleep_duration)
            
            # Choose a random zone and detection type
            random_zone = random.choice(ZONES)
            random_type = random.choice(DETECTION_TYPES)
            
            print(f"?? Triggering new random event: '{random_type.upper()}' in '{random_zone}'")
            trigger_detection(random_zone, random_type)

    except KeyboardInterrupt:
        print("\n?? Simulator stopped by user. Goodbye!")
    except Exception as e:
        print(f"?? An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_simulation()
