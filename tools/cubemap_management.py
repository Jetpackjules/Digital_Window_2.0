import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PIL import Image
import os

def convert_jpg_to_png(folder_path):
    """
    Convert all .jpg files in the specified folder to .png format.
    
    Args:
        folder_path (str): Path to the folder containing the images.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg"):
            jpg_path = os.path.join(folder_path, filename)
            png_path = os.path.join(folder_path, filename[:-4] + ".png")
            img = Image.open(jpg_path)
            img.save(png_path)
            print(f'Converted "{jpg_path}" to "{png_path}"')

def load_cubemap(folder_path, new_size=(512*2.0, 512*2.0)):
    # Set the directory you want to rename files in

    # REMOVE "_NORMAL" PREFIX! 
    for filename in os.listdir(folder_path):
        if filename.startswith("normal_"):
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, filename.replace("normal_", "", 1))
            os.rename(old_file, new_file)
            print(f'Renamed "{old_file}" to "{new_file}"')
    """
    Load a cubemap from a folder containing six images.
    
    Args:
        folder_path (str): Path to the folder containing the cubemap images.
        
    Returns:
        GLuint: OpenGL texture ID for the loaded cubemap.
    """

    # Convert .jpg files to .png if any
    convert_jpg_to_png(folder_path)

    # Define the face names in the order: [negx, posx, negy, posy, negz, posz]
    face_names = ["negx.png", "posx.png", "negy.png", "posy.png", "negz.png", "posz.png"]


    textureID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, textureID)

    # List to store images for visualization
    images_for_visualization = []

    for i, face_name in enumerate(face_names):
        img_path = os.path.join(folder_path, face_name)
        img = Image.open(img_path)
        img = img.resize(new_size, Image.ANTIALIAS)  # Resize the image on-the-fly
        img_data = img.tobytes("raw", "RGB", 0, -1)
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 
                     0, GL_RGB, img.width, img.height, 
                     0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        # Append image to the list for visualization
        images_for_visualization.append(img)

    # Set texture parameters
    # Set texture parameters
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)


    # Create a single image from the list and display it
    total_width = sum([img.width for img in images_for_visualization])
    max_height = max([img.height for img in images_for_visualization])
    combined_img = Image.new('RGB', (total_width, max_height))
    # combined_img.show()

    return textureID

