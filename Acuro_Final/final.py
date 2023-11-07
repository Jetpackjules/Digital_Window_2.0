import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import sys
import os
import glm
import OpenGL.GL as gl
current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(os.path.join(parent_dir, 'tools'))
sys.path.append(os.path.join(parent_dir, 'Face_Tracker'))

# Importing tool files:
import cubemap_management
import get_shader_deets
import monitor_info
# import acuro
import fov_calculator
import tracker


#Window info:
monitor_width, monitor_height, monitor_dpi = monitor_info.get_monitor_dimensions() #Display size in meters, with pixels per inch as the last var
aspect_ratio = monitor_width / monitor_height

# Parameters (CHANGE THESE AT WILL!)
ROOM_DEPTH: float = 2
ROOM_SIZE: float = monitor_height
QUAD_SIZE: float = monitor_height  # Change this value to scale the quad

Background_Color = glm.vec4(0.8, 0.8, 0.8, 1.0)
fullscreen = True




fov = glm.radians(90)
# distance_from_quad = fov_calculator.calculate_distance_for_fov(monitor_height, 90)
distance_from_quad = 1.1
camera_pos = glm.vec3(0.0, 0.0, distance_from_quad)

simulated_camera_pos = glm.vec3(0.0, 1.0, 0.0)


# Initialize GLFW
if not glfw.init():
    raise Exception("glfw can not be initialized!")


def check_shader_compilation(shader):
    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if status != GL_TRUE:
        log = glGetShaderInfoLog(shader)
        print("Shader compilation failed:")
        print(log)

        exit()
    print("SHADER COMPILED")
    print(glGetShaderInfoLog(shader))

def check_program_linking(program):
    status = glGetProgramiv(program, GL_LINK_STATUS)
    if status != GL_TRUE:
        log = glGetProgramInfoLog(program)
        print("Program linking failed:")
        print(log)
        
        exit()
    print("SHADER LINKED")



if fullscreen:

    glfw.window_hint(glfw.DECORATED, glfw.FALSE)

    # Create the window with the monitor's dimensions
    window = glfw.create_window(int(monitor_width*100/2.54*monitor_dpi), int(monitor_height*100/2.54*monitor_dpi), "Cubemap Viewer", None, None)
else:
    window = glfw.create_window(int(monitor_width*50/2.54*monitor_dpi),  int(monitor_height*50/2.54*monitor_dpi), "GLFW Window", None, None)
    glfw.set_window_pos(window, 400, 200)

if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")


glfw.make_context_current(window)

# Load shaders from files
with open('Acuro_Final/vertex_shader.glsl', 'r') as f:
    vertex_shader_source = f.read()

with open('Acuro_Final/fragment_shader.glsl', 'r') as f:
    fragment_shader_source = f.read()


vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
check_shader_compilation(vertex_shader)

fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
check_shader_compilation(fragment_shader)

shader_program = compileProgram(vertex_shader, fragment_shader)
check_program_linking(shader_program)
glUseProgram(shader_program)


vertices = [
    # Positions                 # UVs
    -QUAD_SIZE/2,  QUAD_SIZE/2, 0.0,  0.0, 1.0,
    -QUAD_SIZE/2, -QUAD_SIZE/2, 0.0,  0.0, 0.0,
     QUAD_SIZE/2, -QUAD_SIZE/2, 0.0,  1.0, 0.0,
     QUAD_SIZE/2,  QUAD_SIZE/2, 0.0,  1.0, 1.0
]

indices = [
    0, 1, 2,
    2, 3, 0
]

# UV attribute
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
glEnableVertexAttribArray(1)


VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, (GLfloat * len(vertices))(*vertices), GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, (GLuint * len(indices))(*indices), GL_STATIC_DRAW)


# ---------------------
get_shader_deets.print_attribs(shader_program)
get_shader_deets.print_uniforms(shader_program)
# ---------------------


# Vertex Attribute (Position)
position = glGetAttribLocation(shader_program, "inVertex")
if position != -1:  # Ensure the attribute was found
    glEnableVertexAttribArray(position)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
else:
    print("Warning: inVertex attribute not found in the shader.")


#initing cubemap:
cubemap = cubemap_management.load_cubemap("cubemap")
glActiveTexture(GL_TEXTURE0)  # Use the first texture unit
glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)

# Set the texture wrapping parameter for the s and t (u and v) axes (this should grow the cubemap if the quad is bigger????)
# glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
# glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
# glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

cubemap_location = glGetUniformLocation(shader_program, "cubemap_albedo")
glUniform1i(cubemap_location, 0)  # 0 refers to GL_TEXTURE0

#KEY INPUT MANAGEMENT:
camera_target = glm.vec3(0.0, 0.0, 0.0)
camera_up = glm.vec3(0.0, 1.0, 0.0)

def key_callback(window, key, scancode, action, mods):
    global simulated_camera_pos, fov, camera_pos, new_fov
    move_speed = 0.1  # Adjust this value for faster/slower movement

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_UP:
            simulated_camera_pos.z += move_speed
        if key == glfw.KEY_DOWN:
            simulated_camera_pos.z -= move_speed
        if key == glfw.KEY_LEFT:
            simulated_camera_pos.x -= move_speed
        if key == glfw.KEY_RIGHT:
            simulated_camera_pos.x += move_speed
        if key == glfw.KEY_0:
            simulated_camera_pos.y -= move_speed
            print(simulated_camera_pos.y)
            # new_fov -= 1
            # print(new_fov)
            pass
            # fov = glm.radians(new_fov)
            # distance_from_quad = fov_calculator.calculate_distance_for_fov(monitor_height, new_fov)
            # camera_pos = glm.vec3(0.0, 0.0, distance_from_quad)
            # print("NEW DISTANCE: ", distance_from_quad)


glfw.set_key_callback(window, key_callback)
simulated_camera_pos_location = glGetUniformLocation(shader_program, "simulated_camera_pos")

# Set the background color to, for example, a light gray
glClearColor(Background_Color.r, Background_Color.g, Background_Color.b, Background_Color.a)

# setting values...
get_shader_deets.modify(shader_program, "room_depth", ROOM_DEPTH)
get_shader_deets.modify(shader_program, "ROOM_SIZE", ROOM_SIZE)

#some cam variables:
near_plane = 0.001
far_plane = 1000.0

# Main loop
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)

    #model matrix computation (position for quad, I believe...): -----------------------
    model_matrix = glm.mat4(1.0)

    # Define the View matrix
    # Let's assume the camera is at (0, 0, x) and looking at the origin (0, 0, 0)
    # The up vector is along the y-axis
    view_matrix = glm.lookAt(camera_pos, camera_target, camera_up)

    # Compute the ModelView matrix
    modelViewMatrix = view_matrix * model_matrix

    # Now, you can pass this matrix to your shader:
    location = glGetUniformLocation(shader_program, "modelViewMatrix")
    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(modelViewMatrix))

    # projection matrix computation: --------------------
    
    projection_matrix = glm.perspective(fov, aspect_ratio, near_plane, far_plane)

    # Now, you can pass this matrix to your shader:
    location = glGetUniformLocation(shader_program, "projectionMatrix")
    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(projection_matrix))

    # -------------------------------------------------------------
    # TRYING ORTHOGRAPHIC PROJECTION MATRIX:::

    # Define the orthographic projection parameters
    left = -monitor_width / 2
    right = monitor_width / 2
    bottom = -monitor_height / 2
    top = monitor_height / 2

    # Create the orthographic projection matrix
    ortho_projection_matrix = glm.ortho(left, right, bottom, top, near_plane, far_plane)

    # Use the orthographic projection matrix for rendering the quad
    location = glGetUniformLocation(shader_program, "projectionMatrix")
    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(ortho_projection_matrix))

    # ------------------------------------------------------------




    # PASSING IN FAKE CAM POS:
    # acuro_pos = acuro.get_acuro_pos()
    acuro_pos = tracker.get_face_pos()

    if (acuro_pos is not None):
        simulated_camera_pos.x = round(-acuro_pos[0], 3)
        simulated_camera_pos.z = round(-acuro_pos[1]+monitor_height/2, 3)
        simulated_camera_pos.y = round(acuro_pos[2]/2, 3)
        # print(simulated_camera_pos.xyz)
    glUniform3f(simulated_camera_pos_location, simulated_camera_pos.x, simulated_camera_pos.y, simulated_camera_pos.z)

    #Draw the actual quad:
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(window)

glfw.terminate()
