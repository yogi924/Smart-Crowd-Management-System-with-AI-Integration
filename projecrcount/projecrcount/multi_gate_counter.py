
# multi_gate_counter.py
from ultralytics import YOLO
import cv2
import requests
import threading

# Gate-specific configuration
VIDEO_SOURCES = {
    1: "C:\\Users\\rekha\\OneDrive\\Desktop\\pc.mp4",
    2: "C:\\Users\\rekha\\OneDrive\\Desktop\\pc2.mp4",
    3: "C:\\Users\\rekha\\OneDrive\\Desktop\\pc3.mp4"
}

RECT_AREAS = {
    1: ((100, 100), (700, 400)),
    2: ((100, 100), (700, 400)),
    3: ((100, 100), (700, 400))
}

SERVER_URL = "http://127.0.0.1:5000/update_count"

# Load model once
model = YOLO('yolov8n.pt')

def is_inside_area(cx, cy, rect):
    (x1, y1), (x2, y2) = rect
    return x1 <= cx <= x2 and y1 <= cy <= y2

def process_gate_video(gate_id, video_path):
    cap = cv2.VideoCapture(video_path)
    rect = RECT_AREAS[gate_id]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, classes=[0])
        people_count = 0

        for box in results[0].boxes.xyxy:
            x1, y1, x2, y2 = box.tolist()
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

            if is_inside_area(cx, cy, rect):
                people_count += 1
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

        # Draw ROI and count
        cv2.rectangle(frame, rect[0], rect[1], (255, 0, 0), 2)
        cv2.putText(frame, f"Gate {gate_id} Count: {people_count}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        # Post to server
        try:
            requests.post(SERVER_URL, json={'gate_id': gate_id, 'count': people_count})
        except Exception as e:
            print(f"[Gate {gate_id}] Server Error:", e)

        cv2.imshow(f"Gate {gate_id} Counter", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(f"Gate {gate_id} Counter")

# Launch all gate threads
threads = []
for gid, path in VIDEO_SOURCES.items():
    t = threading.Thread(target=process_gate_video, args=(gid, path))
    t.start()
    threads.append(t)

# Wait for all to complete
for t in threads:
    t.join()
