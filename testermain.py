from ultralytics import YOLO
import cv2
import numpy as np

# Load the YOLOv8 model
model = YOLO("best.pt")

# Initialize the camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not access the camera.")
    exit()

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to capture frame. Exiting...")
        break

    # Run YOLO object detection
    results = model(frame)

    # Get detections from the first result
    boxes = results[0].boxes

    # Create a copy of the frame to draw bounding boxes
    annotated_frame = frame.copy()

    if boxes is not None:
        for box in boxes:
            conf = float(box.conf[0])
            if conf >= 0.7:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                color = (0, 255, 0)

                # Draw rectangle
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                # Draw label with confidence
                cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Display the annotated frame
    cv2.imshow("YOLOv8 Object Detection", annotated_frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
