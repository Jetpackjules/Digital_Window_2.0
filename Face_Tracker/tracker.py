import cv2
import dlib
import numpy as np
import threading
import time

# Constants for face detection
KNOWN_WIDTH = 0.16  # Average width of human face in meters
FOCAL_LENGTH = 800  # This needs to be calibrated for your camera

# Initialize dlib's face detector (HOG-based)
detector = dlib.get_frontal_face_detector()

# Camera setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fx = fy = FOCAL_LENGTH  # Use the same focal length for both x and y for simplicity
cx = WIDTH / 2
cy = HEIGHT / 2
cameraMatrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)

# Shared variable for thread communication
face_position = None
lock = threading.Lock()
running = True  # Flag to control the camera loop

def get_face_pos():
    with lock:
        return face_position


def cam_loop():
    global face_position, running
    while running:
        try:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 0)

            for rect in rects:
                # Draw the face bounding box on the frame
                (x, y, w, h) = (rect.left(), rect.top(), rect.width(), rect.height())
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Calculate the distance in meters (z)
                z_meters = (KNOWN_WIDTH * FOCAL_LENGTH) / w

                # Approximate the physical space represented by a pixel at the known distance
                pixel_per_meter = w / KNOWN_WIDTH
                x_meters = (x + w / 2 - cx) / pixel_per_meter
                y_meters = (y + h / 2 - cy) / pixel_per_meter


                with lock:
                    face_position = [x_meters, y_meters, z_meters]

            # Display the resulting frame
            cv2.imshow('Webcam Feed', frame)

            # Break the loop with 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break
        except Exception as e:
            print(f"An error occurred: {e}")

    cap.release()
    cv2.destroyAllWindows()

def display_webcam():
    webcam_thread = threading.Thread(target=cam_loop)
    webcam_thread.daemon = True  # Daemonize thread
    webcam_thread.start()

# Start the webcam display
display_webcam()

# Main thread doing other tasks
# while running:
#     # Retrieve the latest face position
#     position = get_face_pos()
#     if position:
#         # Unpack the position tuple
#         x, y, z = position
#         # Round each coordinate to 2 decimal places
#         x_rounded = round(x, 2)
#         y_rounded = round(y, 2)
#         z_rounded = round(z, 2)
#         # Print the rounded position
#         print(f"Detected Face Position (x, y, z): ({x_rounded}, {y_rounded}, {z_rounded})")
#     # Sleep to prevent this loop from using 100% CPU
#     time.sleep(0.1)

print("Stopping the webcam display...")
# No need to join the thread since it's daemonized
cv2.destroyAllWindows()