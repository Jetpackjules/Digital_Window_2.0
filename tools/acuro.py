import cv2
import numpy as np
import threading
import coefficient_manager

# Constants
markerLength = 0.07  # meters
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Camera setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fx = fy = 1400  # This is a rough estimate and might need adjustment
cx = WIDTH / 2
cy = HEIGHT / 2
cameraMatrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
distCoeffs = np.zeros((5,1), dtype=np.float64)

# # overriding for custom matrixes:
# cameraMatrix, distCoeffs = coefficient_manager.load_coefficients("Aruco_Calibration\\coefficients\\Laptop\\calibration_charuco.yml")

def get_acuro_pos():
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)
    
    if len(corners) > 0:
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, markerLength, cameraMatrix, distCoeffs)
        # Doing some math to properly scale distance to camera:
        tvecs[0][0][2] = -0.004947+0.3674*tvecs[0][0][2]
        return tvecs[0][0]  # Return the position of the first detected acuro
        
    return None

def calculate_distance(position):
    return np.sqrt(position[0]**2 + position[1]**2 + position[2]**2)

def cam_loop():
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)
        mirrored_frame = cv2.flip(frame, 1)  # Create a mirrored version for display
        
        if len(corners) > 0:
            # Flip the corners to match the mirrored frame
            flipped_corners = []
            for corner in corners:
                flipped_corner = corner.copy()
                flipped_corner[0,:,0] = WIDTH - flipped_corner[0,:,0]
                flipped_corners.append(flipped_corner)

            mirrored_frame = cv2.aruco.drawDetectedMarkers(mirrored_frame, flipped_corners, ids)  # Draw on the mirrored frame
            
            position = get_acuro_pos()
            if position is not None:
                # Calculate the overall distance
                distance = calculate_distance(position)

                # Display the Depth, X offset, Y offset, and Overall Distance
                #adjusting for weird depth overestimation...
                new_depth = position[2]

                text = f"Depth: {new_depth:.2f}m, X offset: {position[0]:.2f}m, Y offset: {position[1]:.2f}m, Distance: {distance:.2f}m"
                font_scale = 0.5
                font_thickness = 1
                font_color = (0, 255, 0)  # GREEN
                bg_color = (0, 0, 0)  # BLACK
                font = cv2.FONT_HERSHEY_SIMPLEX
                
                # Calculate text size
                (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
                
                # Define text and background rectangle positions
                text_offset_x = 10
                text_offset_y = 30
                box_coords = ((text_offset_x, text_offset_y + 5), (text_offset_x + text_width, text_offset_y - text_height - 5))
                
                # Draw a black background rectangle
                cv2.rectangle(mirrored_frame, box_coords[0], box_coords[1], bg_color, cv2.FILLED)
                
                # Display the text on the frame
                cv2.putText(mirrored_frame, text, (text_offset_x, text_offset_y), font, font_scale, font_color, font_thickness, lineType=cv2.LINE_AA)
        
        cv2.imshow('Webcam Feed', mirrored_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def display_webcam():
    webcam_thread = threading.Thread(target=cam_loop)
    webcam_thread.start()

display_webcam()
# Example usage:
# position = get_acuro_pos()
# if position is not None:
#     distance = calculate_distance(position)
#     print(f"Detected Acuro Position (x, y, z): {position}, Overall Distance: {distance}")


# Main thread doing other tasks
import keyboard
import time

while True:
    
    # Check if space key is pressed
    if keyboard.is_pressed('space'):
        # Retrieve the latest face position
        position = get_acuro_pos()
        # Unpack the position tuple
        x, y, z = position
        # Round each coordinate to 2 decimal places
        x_rounded = round(x, 2)
        y_rounded = round(y, 2)
        z_rounded = round(z, 2)
        # Print the rounded position
        print(f"Detected Acuro Position (x, y, z): ({x_rounded}, {y_rounded}, {z_rounded})")
        # Add a small delay to prevent multiple prints on a single key press
        time.sleep(0.2)
