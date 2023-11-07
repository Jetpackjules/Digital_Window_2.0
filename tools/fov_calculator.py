import math

def calculate_window_fov(width, height, distance, observer_fov):
    """
    Calculate the FOV of a window given its dimensions, distance from the window, and the observer's FOV.

    Parameters:
    - width (float): Width of the window in meters.
    - height (float): Height of the window in meters.
    - distance (float): Distance from the observer to the window in meters.
    - observer_fov (float): Observer's field of view in degrees.

    Returns:
    - float: FOV of the window's view in degrees.
    """
    
    # Calculate half of the observer's FOV in radians
    half_fov_rad = math.radians(observer_fov / 2)
    
    # Calculate the half width of the view at the window's location using tangent function
    half_width_view = math.tan(half_fov_rad) * distance
    
    # Calculate the half FOV of the window's view using the inverse tangent function
    half_window_fov_rad = math.atan((height / 2) / distance)
    
    # Convert the half FOV of the window's view to degrees and multiply by 2 to get the full FOV
    window_fov_deg = math.degrees(half_window_fov_rad) * 2
    # print(distance)
    return window_fov_deg


def calculate_window_fov(width, height, distance, observer_fov):
    """
    Calculate the FOV of a window given its dimensions, distance from the window, and the observer's FOV.

    Parameters:
    - width (float): Width of the window in meters.
    - height (float): Height of the window in meters.
    - distance (float): Distance from the observer to the window in meters.
    - observer_fov (float): Observer's field of view in degrees.

    Returns:
    - float: FOV of the window's view in degrees.
    """
    
    # Calculate half of the observer's FOV in radians
    half_fov_rad = math.radians(observer_fov / 2)
    
    # Calculate the half width of the view at the window's location using tangent function
    half_width_view = math.tan(half_fov_rad) * distance
    
    # Calculate the half FOV of the window's view using the inverse tangent function
    half_window_fov_rad = math.atan((height / 2) / distance)
    
    # Convert the half FOV of the window's view to degrees and multiply by 2 to get the full FOV
    window_fov_deg = math.degrees(half_window_fov_rad) * 2
    # print(distance)
    return window_fov_deg

import math

def calculate_distance_for_fov(quad_size, fov=90):
    # Convert FOV from degrees to radians for math functions
    fov_radians = math.radians(fov)
    
    # Calculate the half-width of the quad using Pythagorean theorem
    half_width = quad_size / 2

    if fov == 90:
        distance = half_width
    else:
        distance = half_width / math.tan(fov_radians / 2)
    
    return distance

# Example usage:
quad_size = 0.18887491727332897
fov = 90  # Replace with your FOV in degrees
distance = calculate_distance_for_fov(quad_size, fov)
print(f"The required distance for the quad to fill the FOV is: {distance}")

# Example usage:
width = 0.5976664807585054  # in meters
height = 0.18887491727332897  # in meters
distance = 0.1  # in meters
observer_fov = 90.0  # in degrees

print("WINDOW FOV: ", calculate_window_fov(width, height, distance, observer_fov))