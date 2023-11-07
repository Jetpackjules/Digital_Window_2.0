import numpy as np
import cv2
import cv2.aruco as aruco
import pathlib


def calibrate_charuco(dirpath, image_format, marker_length, square_length):
    '''Apply camera calibration using aruco.
    The dimensions are in cm.
    '''
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
    board = aruco.CharucoBoard_create(5, 7, square_length, marker_length, aruco_dict)
    arucoParams = aruco.DetectorParameters_create()

    corners_list, id_list = [], []
    img_dir = pathlib.Path(dirpath)
    # Find the ArUco markers inside each image
    for img in img_dir.glob(f'*.{image_format}'):  # Ensure the dot before the extension
        print(f'using image {img}')
        image = cv2.imread(str(img))
        if image is None:
            print(f"Could not read image {img}")
            continue
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(
            img_gray, 
            aruco_dict, 
            parameters=arucoParams
        )

        if ids is not None and len(ids) > 0:
            # Interpolate the Charuco corners
            resp, charuco_corners, charuco_ids = aruco.interpolateCornersCharuco(
                markerCorners=corners,
                markerIds=ids,
                image=img_gray,
                board=board
            )
            # If a Charuco board was found, let's collect image/corner points
            # Requiring at least a certain number of squares
            if resp and resp > 20:
                # Add these corners and ids to our calibration arrays
                corners_list.append(charuco_corners)
                id_list.append(charuco_ids)
        else:
            print(f"No markers detected on {img}")

    # Check if we have enough corners to calibrate
    if len(corners_list) < 1:
        raise ValueError("Not enough corners collected for calibration!")

    # Actual calibration
    ret, mtx, dist, rvecs, tvecs = aruco.calibrateCameraCharuco(
        charucoCorners=corners_list, 
        charucoIds=id_list, 
        board=board, 
        imageSize=img_gray.shape[::-1], 
        cameraMatrix=None, 
        distCoeffs=None)
    
    return [ret, mtx, dist, rvecs, tvecs]

import os
import sys

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(os.path.join(parent_dir, 'tools'))



def create_dir(name):
    #making directory if not existing:
    dir_path = 'Aruco_Calibration\\coefficients\\'+name
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Directory created: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

# -----------------------------------------------------------------


# from ChArUco_calibrate import calibrate_charuco
# from utils import load_coefficients, save_coefficients
import shutil
from coefficient_manager import load_coefficients, save_coefficients


# Parameters
IMAGES_DIR = 'Aruco_Calibration\\images\\og'
IMAGES_FORMAT = 'jpg'
# Dimensions in cm
MARKER_LENGTH = 1.8
SQUARE_LENGTH = 3.6

CAMERA_NAME = "Laptop"

# Calibrate 
ret, mtx, dist, rvecs, tvecs = calibrate_charuco(
    IMAGES_DIR, 
    IMAGES_FORMAT,
    MARKER_LENGTH,
    SQUARE_LENGTH
)

# Make coefficient file if not already present
create_dir(CAMERA_NAME)

# Save coefficients into a file
save_coefficients(mtx, dist, "Aruco_Calibration\\coefficients\\" + CAMERA_NAME+ "\\calibration_charuco.yml")


# UNDISTORTING ALL IMAGES:

# Load coefficients
mtx, dist = load_coefficients('Aruco_Calibration\\coefficients\\' + CAMERA_NAME+ '\\calibration_charuco.yml')

path_parts = IMAGES_DIR.split(os.sep)
path_parts[-1] = 'undistorted'
new_path = os.sep.join(path_parts)
print("NEW PATH: ", new_path)

shutil.rmtree(new_path)

# Recreate the directory after deleting its contents
os.makedirs(new_path)

for image_file in (f for f in os.listdir(IMAGES_DIR) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))):
    print("UNDISTORTING: ", image_file)
    path_to_image = os.path.join(IMAGES_DIR, image_file)
    original = cv2.imread(path_to_image)
    dst = cv2.undistort(original, mtx, dist, None, mtx)
    undistorted_image_path = os.path.join(new_path, 'undist_' + image_file)
    cv2.imwrite(undistorted_image_path, dst)