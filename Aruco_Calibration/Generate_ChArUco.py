import numpy as np
import cv2
import cv2.aruco as aruco
import pathlib

# OG PROPER WORKING VERSIONS:
# opencv-contrib-python==4.7.0.68
# opencv-python==4.8.1.78

# FOR THIS CODE ONLY:
# opencv-contrib-python==4.5.1.48
# opencv-python==4.5.1.48

aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
# Dimensions in cm
marker_length = 3.05
square_length = 3.8
arucoParams = aruco.DetectorParameters_create()
board = aruco.CharucoBoard_create(5, 7, square_length, marker_length, aruco_dict)

board_image = board.draw((500*2, 700*2))

# Save the GridBoard as an image
cv2.imwrite('Aruco_Calibration\\boards\\ChArUco_board.png', board_image)

