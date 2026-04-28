
"""
SafeSense - Core AI Detection Module (Phase 2: Smarter Detection)
This script performs real-time object detection and tracking on a video stream.
It uses YOLOv8 for detection and DeepSORT for tracking, and includes logic
for multi-frame validation and crowd analysis.
"""
import cv2
import os
import time
import requests
import numpy as np
from datetime import datetime, timezone
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

# --- Configuration ---
BACKEND_API_URL = "http://localhost:8000/api/detection/event"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "yolov8n.pt")
VIDEO_SOURCE = os.path.join(os.path.dirname(__file__), "test_videos", "fire_smoke_test.mp4")

# Detection & Tracking Parameters
CONFIDENCE_THRESHOLD = 0.60
FRAME_CONSISTENCY_COUNT = 5

# --- State Tracking ---
detection_tracker = {}
guest_tracker = DeepSort(max_age=5) # Track people for 5 frames if they disappear
zone_guest_count = {}


def send_detection_event(detection_data):
    """
    Sends a confirmed detection event to the backend API.
    """
    try:
        payload = {
            "zone": "Zone A",
            "floor": "Floor 1", 
            "detection_type": detection_data['class_name'],
            "confidence": detection_data['confidence'],
            "frame_count": FRAME_CONSISTENCY_COUNT,
            "guest_count": zone_guest_count.get("Zone A", 0), # Include current guest count
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        print(f"[EVENT] Sending confirmed detection: {payload['detection_type']}")
        response = requests.post(BACKEND_API_URL, json=payload, headers={'Content-Type': 'application/json'}, timeout=5)
        if response.status_code == 200:
            print(f"[SUCCESS] Backend acknowledged event. Incident ID: {response.json().get('incident_id')}")
        else:
            print(f"[ERROR] Backend returned status {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not connect to backend API: {e}")

def process_detections(results, frame):
    """
    Processes YOLOv8 detections, tracks guests, and applies multi-frame validation.
    """
    global detection_tracker, zone_guest_count

    detected_classes_in_frame = set()
    person_detections = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            confidence = box.conf[0]
            if confidence >= CONFIDENCE_THRESHOLD:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]

                if class_name == 'person':
                    x1, y1, x2, y2 = box.xyxy[0]
                    person_detections.append(([int(x1), int(y1), int(x2-x1), int(y2-y1)], confidence, class_name))
                else:
                    target_class = None
                    if 'fire' in class_name:
                        target_class = 'fire_smoke'
                    
                    if target_class:
                        # Multi-frame validation logic (as before)
                        # ... (omitted for brevity, will be added back)
                        pass

    # Update guest tracker with person detections
    tracked_guests = guest_tracker.update_tracks(person_detections, frame=frame)
    zone_guest_count["Zone A"] = len(tracked_guests)

    # (Optional) Visualize guest tracking
    for guest in tracked_guests:
        if not guest.is_confirmed():
            continue
        track_id = guest.track_id
        ltrb = guest.to_ltrb()
        cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), (0, 255, 0), 2)
        cv2.putText(frame, f"Guest-{track_id}", (int(ltrb[0]), int(ltrb[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display guest count
    cv2.putText(frame, f"Guests in Zone: {zone_guest_count['Zone A']}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Crowd Panic Logic (placeholder)
    if zone_guest_count.get("Zone A", 0) > 5: # Example threshold
        # In a real implementation, analyze motion vectors from optical flow
        pass

    process_detections_validation(results)


def process_detections_validation(results):
    """
    Processes YOLOv8 detection results, applying multi-frame validation.
    """
    global detection_tracker
    
    detected_classes_in_frame = set()

    for result in results:
        boxes = result.boxes
        for box in boxes:
            confidence = box.conf[0]
            if confidence >= CONFIDENCE_THRESHOLD:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                target_class = None
                if 'fire' in class_name:
                    target_class = 'fire_smoke'
                elif class_name == 'person':
                    target_class = 'person_down'

                if target_class:
                    detected_classes_in_frame.add(target_class)
                    if target_class not in detection_tracker:
                        detection_tracker[target_class] = {'count': 1, 'last_seen': time.time(), 'confidence': float(confidence)}
                        print(f"[DETECT] Potential '{target_class}' detected. Watching...")
                    else:
                        tracker = detection_tracker[target_class]
                        tracker['count'] += 1
                        tracker['last_seen'] = time.time()
                        
                        if tracker['count'] >= FRAME_CONSISTENCY_COUNT:
                            print(f"[CONFIRMED] '{target_class}' confirmed after {FRAME_CONSISTENCY_COUNT} frames.")
                            send_detection_event({'class_name': target_class, 'confidence': tracker['confidence']})
                            del detection_tracker[target_class]

    current_time = time.time()
    for class_name in list(detection_tracker.keys()):
        if class_name not in detected_classes_in_frame or (current_time - detection_tracker[class_name]['last_seen'] > 2):
            print(f"[RESET] Resetting tracker for '{class_name}'.")
            del detection_tracker[class_name]


def main():
    """
    Main function to initialize the model and start the video processing loop.
    """
    print("Starting SafeSense AI Detection Module (Phase 2)...")

    if not os.path.exists(MODEL_PATH) or not os.path.exists(VIDEO_SOURCE):
        print("[ERROR] Model or video file not found.")
        return

    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print("[ERROR] Could not open video source.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, stream=True, verbose=False)
        
        # Process detections, track guests, and handle validation
        process_detections(results, frame)

        # Display the frame
        cv2.imshow("SafeSense AI Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Detection module stopped.")


if __name__ == "__main__":
    main()
