import cv2
import numpy as np
from PIL import Image, ImageDraw

# Get the input file path
input_file_path = "Video_Gen\cubemap_video.avi"

# Get the output file path
output_file_path = "Video_Gen\cubemap_video.ogv"


# Constants
CUBE_SIZE = 512
HEIGHT = CUBE_SIZE*3
WIDTH = CUBE_SIZE*4

CIRCLE_RADIUS = CUBE_SIZE // 8
SPEED = 15
FPS = 30  # Frames per second

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('Video_Gen\\cubemap_video.avi', fourcc, FPS, (WIDTH, HEIGHT))
# Initialize video writer
# fourcc = cv2.VideoWriter_fourcc(*'THEO')
# out = cv2.VideoWriter('Video_Gen\\cubemap_video.ogv', fourcc, FPS, (WIDTH, HEIGHT))

# Function to draw the cubemap format
def draw_cubemap(draw):
    # Top cube
    x_start = CUBE_SIZE
    y_start = 0
    draw.rectangle([x_start, y_start, x_start + CUBE_SIZE, y_start + CUBE_SIZE], fill="red")

    # Middle row
    for j in range(4):
        x_start = j * CUBE_SIZE
        y_start = CUBE_SIZE
        draw.rectangle([x_start, y_start, x_start + CUBE_SIZE, y_start + CUBE_SIZE], fill="blue")

    # Bottom cube
    x_start = CUBE_SIZE
    y_start = 2 * CUBE_SIZE
    draw.rectangle([x_start, y_start, x_start + CUBE_SIZE, y_start + CUBE_SIZE], fill="green")

# Generate video
x = 0 + CIRCLE_RADIUS  # Start from the left edge
y = HEIGHT // 2  # Middle of the height
direction = [SPEED, 0]  # Only move in the x direction

while True:
    # Create a red canvas
    img = Image.new('RGB', (WIDTH, HEIGHT), color = 'black')
    draw = ImageDraw.Draw(img)

    # Draw the cubemap
    draw_cubemap(draw)

    # Draw the moving circle
    draw.ellipse([(x - CIRCLE_RADIUS, y - CIRCLE_RADIUS), (x + CIRCLE_RADIUS, y + CIRCLE_RADIUS)], fill="white")

    # Update circle position
    x += direction[0]

    # Loop the circle when it goes out of the right edge and break the loop
    if x - CIRCLE_RADIUS > WIDTH:
        break

    # Convert PIL image to numpy array and write the frame to the video
    frame = np.array(img)
    out.write(frame)

# Release the video writer
out.release()


# Convert the file