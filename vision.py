from ultralytics import YOLO
import cv2
import time
import serial
import math
import os

# Load your trained model
model = YOLO("/home/mohammoud/Desktop/softarm/py/runs/detect/train_bbox_fff_m_finalTarget5552/weights/best.pt")
# Open camera (adjust index if needed)
cap = cv2.VideoCapture(2)

fps_limit = 5
frame_delay = 1.0 / fps_limit  # seconds between frames

# Try to open serial connection to Arduino
arduino = None
port = "/dev/ttyACM0"
if os.path.exists(port):
    try:
        arduino = serial.Serial(port, 9600, timeout=1)
        print("Arduino connected on", port)
    except serial.SerialException as e:
        print("Could not open port:", e)
        arduino = None
else:
    print("No Arduino detected, running vision only.")

# Define the target classes
target_classes = ["cube", "ping pong ball", "water-bottle", "SpiRob"]

# Known real-world widths (cm) for each object
known_widths = {
    "cube": 5.5,
    "ping pong ball": 4.0,
    "water-bottle": 6.5,
    "SpiRob": 7.0
}

cv2.namedWindow("YOLO Detection (Objects Only)")

while True:
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO inference
    results = model(frame, conf=0.25)

    # Annotated frame
    annotated_frame = results[0].plot()

    # Add back line and center dot
    h, w, _ = frame.shape
    mid_x = w // 2
    mid_y = h // 2
    cv2.line(annotated_frame, (mid_x, 0), (mid_x, h), (0, 255, 0), 2)
    cv2.circle(annotated_frame, (mid_x, mid_y), 5, (0, 0, 255), -1)


    # Loop through detections
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        print("Detected:", cls_name)

        if cls_name in target_classes:
            x_center = float(box.xywh[0][0])
            y_center = float(box.xywh[0][1])
            pixel_width = float(box.xywh[0][2])

            # Pixel distance from frame center
            pixel_distance = math.sqrt((x_center - mid_x)**2 + (y_center - mid_y)**2)
            side = "-1" if x_center < mid_x else "1"

            # Use object-specific real-world width
            real_width_cm = known_widths.get(cls_name, 5.0)
            cm_per_pixel = real_width_cm / pixel_width
            real_distance_cm = pixel_distance * cm_per_pixel

            # Calculate radius/diameter depending on object
            if cls_name in ["ping pong ball", "cube"]:
                size_cm = real_width_cm / 2.0  # radius
                size_label = "radius"
            elif cls_name == "water-bottle":
                size_cm = real_width_cm       # short diameter
                size_label = "diameter"
            else:
                size_cm = real_width_cm
                size_label = "size"

            # Print info
            print(f"{cls_name} → {side}, dist ≈ {real_distance_cm:.1f}cm, {size_label} ≈ {size_cm:.1f}cm")

            # Overlay text
            cv2.putText(annotated_frame, f"{side} | {real_distance_cm:.1f}cm | {size_label}:{size_cm:.1f}cm",
                        (int(x_center), int(y_center)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Send to Arduino
            if arduino and arduino.is_open:
                try:
                    arduino.write(f"{side},{real_distance_cm:.1f},{size_cm:.1f}\n".encode())
                except serial.SerialException as e:
                    print("Serial write failed:", e)

    cv2.imshow("YOLO Detection (Objects Only)", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Throttle to 5 FPS
    elapsed = time.time() - start_time
    if elapsed < frame_delay:
        time.sleep(frame_delay - elapsed)

cap.release()
cv2.destroyAllWindows()
