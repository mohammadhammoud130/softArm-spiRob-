from ultralytics import YOLO
import cv2
import time
import serial
import math
import os

# --- Configuration ---
MODEL_PATH = "/home/mohammoud/Desktop/softarm/py/runs/detect/train_bbox_fff_m_finalTarget5552/weights/best.pt"
model = YOLO(MODEL_PATH)

# Camera and FPS
cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
FPS_LIMIT = 5 # Keep a limit to not process frames unnecessarily fast
FRAME_DELAY = 1.0 / FPS_LIMIT

# --- Arduino Connection ---
arduino = None
ARDUINO_PORT = "/dev/ttyACM0"
if os.path.exists(ARDUINO_PORT):
    try:
        arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
        print("✅ Arduino connected on", ARDUINO_PORT)
    except serial.SerialException as e:
        print(f"⚠️ Could not open port {ARDUINO_PORT}: {e}")
        arduino = None
else:
    print("ℹ️ No Arduino detected. Running in vision-only mode.")

# --- Object Definitions ---
target_classes = ["cube", "ping pong ball", "water-bottle"]
known_widths = {
    "cube": 5.5,
    "ping pong ball": 4.0,
    "water-bottle": 6.5,
}

print("\nStarting detection loop. Press 'Enter' to send data, 'q' to quit.")

# --- Main Loop ---
try:
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame from camera.")
            break

        results = model(frame, conf=0.35)
        annotated_frame = results[0].plot()

        h, w, _ = frame.shape
        arm_center_x = w // 2
        arm_center_y = h // 2
        cv2.circle(annotated_frame, (arm_center_x, arm_center_y), 7, (0, 0, 255), -1)

        # NEW: A list to hold the messages for all objects detected in THIS frame
        latest_detection_messages = []

        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]

            if cls_name not in target_classes:
                continue

            # --- Calculations ---
            x_center_px, y_center_px, width_px, _ = box.xywh[0]

            real_width_cm = known_widths.get(cls_name)
            if not real_width_cm: continue
            cm_per_pixel = real_width_cm / float(width_px)

            pos_x_cm = (float(x_center_px) - arm_center_x) * cm_per_pixel
            distance_cm = math.sqrt(pos_x_cm**2 + ((float(y_center_px) - arm_center_y) * cm_per_pixel)**2)
            size_cm = real_width_cm / 2.0 if cls_name in ["ping pong ball", "cube"] else real_width_cm
            side = -1 if pos_x_cm < 0 else 1
            side_text = "Left" if side == -1 else "Right"

            # --- Create the message but DO NOT send it yet ---
            # FORMAT: "name,side,distance_cm,size_cm\n"
            serial_message = f"{cls_name},{side},{distance_cm:.2f},{size_cm:.2f}\n"

            # NEW: Store the message for later
            latest_detection_messages.append(serial_message)

            # --- Update On-Screen Display ---
            text_line1 = f"Side: {side_text} ({side})"
            text_line2 = f"Dist: {distance_cm:.1f} cm"
            top_left_x = int(box.xyxy[0][0])
            top_left_y = int(box.xyxy[0][1])
            cv2.putText(annotated_frame, text_line1, (top_left_x, top_left_y - 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(annotated_frame, text_line2, (top_left_x, top_left_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Resize and show the frame
        display_frame = cv2.resize(annotated_frame, (960, 720))
        cv2.imshow("Soft Arm Vision", display_frame)

        # --- NEW: Keyboard Input Logic ---
        key = cv2.waitKey(1) & 0xFF

        # If 'q' is pressed, break the loop
        if key == ord('q'):
            print("'q' pressed. Shutting down.")
            break
        # If 'Enter' is pressed, send the stored data
        elif key == 13:  # 13 is the ASCII code for the Enter key
            if not latest_detection_messages:
                print("\n--- No target objects detected. Nothing to send. ---")
            else:
                print("\n--- 'Enter' pressed. Sending data: ---")
                for message in latest_detection_messages:
                    # 1. Send to Arduino
                    if arduino and arduino.is_open:
                        arduino.write(message.encode())
                    # 2. Print to console for confirmation
                    print(f"Sent: {message.strip()}")
                print("------------------------------------")


        # Throttle the loop
        elapsed = time.time() - start_time
        if elapsed < FRAME_DELAY:
            time.sleep(FRAME_DELAY - elapsed)

except KeyboardInterrupt:
    print("\nLoop interrupted by user.")
finally:
    # --- Cleanup ---
    print("Cleaning up and shutting down.")
    cap.release()
    cv2.destroyAllWindows()
    if arduino and arduino.is_open:
        arduino.close()
    print("Program finished.")
