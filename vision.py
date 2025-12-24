from ultralytics import YOLO
import cv2
import time
import serial
import math
import os

# --- Configuration ---
MODEL_PATH = "epoch_61-mAP50_0p9034.pt"
model = YOLO(MODEL_PATH)

# Camera and FPS
cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
FPS_LIMIT = 5
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

print("\nStarting detection loop... Press 'q' in the window to quit.")

# --- Main Loop ---
try:
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame from camera.")
            break

        # Run YOLO inference
        results = model(frame, conf=0.35)
        annotated_frame = results[0].plot() # This draws the bounding box and class name

        h, w, _ = frame.shape
        arm_center_x = w // 2
        arm_center_y = h // 2
        cv2.circle(annotated_frame, (arm_center_x, arm_center_y), 7, (0, 0, 255), -1)

        # Loop through all detected objects
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]

            if cls_name not in target_classes:
                continue

            # --- Get Object Info ---
            x_center_px, y_center_px, width_px, _ = box.xywh[0]

            # --- Calculate all values in Centimeters ---
            real_width_cm = known_widths.get(cls_name)
            if not real_width_cm: continue
            cm_per_pixel = real_width_cm / float(width_px)

            pos_x_cm = (float(x_center_px) - arm_center_x) * cm_per_pixel
            pos_y_cm = (float(y_center_px) - arm_center_y) * cm_per_pixel
            distance_cm = math.sqrt(pos_x_cm**2 + pos_y_cm**2)

            size_cm = real_width_cm / 2.0 if cls_name in ["ping pong ball", "cube"] else real_width_cm

            # --- Prepare and Send Serial Data in CM ---
            serial_message = f"{cls_name},{pos_x_cm:.2f},{pos_y_cm:.2f},{distance_cm:.2f},{size_cm:.2f}\n"

            if arduino and arduino.is_open:
                try:
                    arduino.write(serial_message.encode())
                    # Only print if you need to debug; can be noisy
                    # print(f"Sent (cm): {serial_message.strip()}")
                except serial.SerialException as e:
                    print(f"❌ Serial write failed: {e}")
            else:
                 # Only print if you need to debug
                print(f"Would Send (cm): {serial_message.strip()}")


            # NEW: Show the calculated info on the screen
            # ----------------------------------------------------
            text_line1 = f"Dist: {distance_cm:.1f} cm"
            text_line2 = f"Pos: ({pos_x_cm:.1f}, {pos_y_cm:.1f}) cm"

            # Get the top-left corner of the bounding box to position the text
            top_left_x = int(box.xyxy[0][0])
            top_left_y = int(box.xyxy[0][1])

            # Draw the text just above the bounding box
            cv2.putText(annotated_frame, text_line1,
                        (top_left_x, top_left_y - 35), # Position for line 1
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2) # Yellow color

            cv2.putText(annotated_frame, text_line2,
                        (top_left_x, top_left_y - 10), # Position for line 2
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2) # Yellow color
            # ----------------------------------------------------


        # Resize the frame for a larger display window
        display_frame = cv2.resize(annotated_frame, (960, 720))
        cv2.imshow("Soft Arm Vision (Large)", display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

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
