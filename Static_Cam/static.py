import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import sys
import os
import glm
import OpenGL.GL as gl



ROOM_DEPTH: float = 1
ROOM_SIZE: float = 2
QUAD_SIZE: float = 2  # Change this value to scale the quad

fullscreen = True
normal_intensity = 1.0  # Adjust this value to scale the normals


current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(os.path.join(parent_dir, 'tools'))

simulated_camera_pos = glm.vec3(0.0, 0.0, 0.0)
light_source_pos = glm.vec3(0.0, 0.0, 0.4)

light_power = 5.0
# Now you can import the module
import cubemap_management
import get_shader_deets
import monitor_info
import fov_calculator

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


# Create a window
monitor_width, monitor_height, monitor_dpi = monitor_info.get_monitor_dimensions() #Display size in meters, with pixels per inch as the last var
aspect_ratio = monitor_width / monitor_height

if fullscreen:

    glfw.window_hint(glfw.DECORATED, glfw.FALSE)

    # Create the window with the monitor's dimensions
    window = glfw.create_window(int(monitor_width*100/2.54*monitor_dpi), int(monitor_height*100/2.54*monitor_dpi), "Cubemap Viewer", None, None)

else:
    window = glfw.create_window(800, 600, "GLFW Window", None, None)
    glfw.set_window_pos(window, 400, 200)

if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")


glfw.make_context_current(window)

# Load shaders from files
with open('Static_Cam/vertex_shader.glsl', 'r') as f:
    vertex_shader_source = f.read()

with open('Static_Cam/fragment_shader.glsl', 'r') as f:
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

# ------- rendering

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



# # # UV attribute
# glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
# glEnableVertexAttribArray(1)




# Initializing albedo cubemap
glActiveTexture(GL_TEXTURE0)  # Use the first texture unit

cubemap = cubemap_management.load_cubemap("cubemap")
glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)
cubemap_location = glGetUniformLocation(shader_program, "cubemap_albedo")
glUniform1i(cubemap_location, 0)  # 0 refers to GL_TEXTURE0

# # Initializing normal cubemap
glActiveTexture(GL_TEXTURE1)  # Use the second texture unit

cubemap_normal = cubemap_management.load_cubemap("cubemap_normal")
glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap_normal)
cubemap_normal_location = glGetUniformLocation(shader_program, "cubemap_normalmap")
glUniform1i(cubemap_normal_location, 1)  # 1 refers to GL_TEXTURE1

# Set the background color to, for example, a light gray
glClearColor(0.8, 0.8, 0.8, 1.0)

camera_pos = glm.vec3(0.0, 0.0, 1.4)
camera_static_pos = glm.vec3(0.0, 0.0, 1.4)


#KEY INPUT MANAGEMENT:
camera_target = glm.vec3(0.0, 0.0, 0.0)
camera_up = glm.vec3(0.0, 1.0, 0.0)

def key_callback(window, key, scancode, action, mods):
    global light_source_pos, light_power, normal_intensity
    move_speed = 0.1  # Adjust this value for faster/slower movement

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_UP:
            light_source_pos.z -= move_speed
        if key == glfw.KEY_DOWN:
            light_source_pos.z += move_speed
        if key == glfw.KEY_LEFT:
            light_source_pos.x -= move_speed
        if key == glfw.KEY_RIGHT:
            light_source_pos.x += move_speed
        if key == glfw.KEY_RIGHT_SHIFT:
            light_source_pos.y -= move_speed
        if key == glfw.KEY_ENTER:
            light_source_pos.y += move_speed
        if key == glfw.KEY_0:
            light_power -= move_speed*5
        if key == glfw.KEY_9:
            light_power += move_speed*5
        if key == glfw.KEY_LEFT_BRACKET:
            normal_intensity -= move_speed*2
        if key == glfw.KEY_RIGHT_BRACKET:
            normal_intensity += move_speed*2
        
        if key == glfw.KEY_W:
            camera_static_pos.y -= move_speed
        if key == glfw.KEY_S:
            camera_static_pos.y += move_speed
        if key == glfw.KEY_A:
            camera_static_pos.x -= move_speed
        if key == glfw.KEY_D:
            camera_static_pos.x += move_speed
        
glfw.set_key_callback(window, key_callback)
simulated_camera_pos_location = glGetUniformLocation(shader_program, "simulated_camera_pos")


# Function to set up 2D orthographic projection for the minimap
def setup_2d_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-ROOM_SIZE, ROOM_SIZE, -ROOM_SIZE, ROOM_SIZE, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def draw_minimap():
    setup_2d_projection()

    # Clear the minimap with a different background color
    glClearColor(0.1, 0.1, 0.1, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw one edge of the quad as a red line
    glColor3f(1, 0, 0)  # Red color
    glBegin(GL_LINES)
    glVertex2f(-QUAD_SIZE / 2, 0)  # Start point of the line
    glVertex2f(QUAD_SIZE / 2, 0)   # End point of the line
    glEnd()

    # Draw the camera position as a green dot
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(0, 1, 0)  # Green color
    glVertex2f(camera_pos.x, -camera_pos.z)  # Use X and Z for top-down view
    glEnd()

    # Draw the light position as a yellow dot
    glBegin(GL_POINTS)
    glColor3f(1, 1, 0)  # Yellow color
    glVertex2f(light_source_pos.x, -light_source_pos.z)  # Use X and Z for top-down view
    glEnd()

# Create a second window for the minimap
minimap_window = glfw.create_window(400, 400, "Minimap", None, window)
if not minimap_window:
    glfw.terminate()
    raise Exception("glfw minimap window can not be created!")

# glfw.make_context_current(minimap_window)
glfw.set_key_callback(minimap_window, key_callback)

# Main loop
while not glfw.window_should_close(window):
    glfw.make_context_current(window)

    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear color and depth buffers


    # setting FOV:
    fov = glm.radians(65.0)  # For example, 45 degrees. Adjust this value to "zoom in" or "zoom out".
    location = glGetUniformLocation(shader_program, "fov")
    glUniform1f(location, fov)

    # setting values...
    get_shader_deets.modify(shader_program, "room_depth", ROOM_DEPTH)
    get_shader_deets.modify(shader_program, "ROOM_SIZE", ROOM_SIZE)


    location = glGetUniformLocation(shader_program, "resolution")
    glUniform2f(location, 600, 800)

    # Retrieve and print the value to confirm
    buffer = (GLfloat * 2)()
    glGetUniformfv(shader_program, 0, buffer)
    # print("Confirmed vec2 value:", buffer[0], buffer[1])

    normal_intensity_location = glGetUniformLocation(shader_program, "normal_intensity")
    glUniform1f(normal_intensity_location, normal_intensity)

    #model matrix computation (position fo quad, I believe...): -----------------------
    # model_matrix = glm.translate(glm.mat4(1.0), glm.vec3(1.0, 1.0, 1.0))
    model_matrix = glm.mat4(1.0)


    # Define the View matrix
    # Let's assume the camera is at (0, 0, 5) and looking at the origin (0, 0, 0)
    # The up vector is along the y-axis
    
    #camera_pos += glm.vec3(0.00001, 0.00001, 0.0)

    view_matrix = glm.lookAt(camera_pos, camera_target, camera_up)


    # Compute the ModelView matrix
    modelViewMatrix = view_matrix * model_matrix

    # Now, you can pass this matrix to your shader:
    location = glGetUniformLocation(shader_program, "modelViewMatrix")
    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(modelViewMatrix))

    #projection matrix computation: --------------------
    
    # Define the Perspective Projection matrix
    # Parameters: Field of View (in degrees), Aspect Ratio, Near clipping plane, Far clipping plane
    fov = glm.radians(90.0)  # Convert to radians
    # aspect_ratio = 800 / 600.0  # Assuming an 800x600 window size
    near_plane = 0.001
    far_plane = 1000.0

    projection_matrix = glm.perspective(fov, aspect_ratio, near_plane, far_plane)

    # Now, you can pass this matrix to your shader:
    location = glGetUniformLocation(shader_program, "projectionMatrix")

    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(projection_matrix))

    # PASSING IN FAKE CAM POS:
    
    glUniform3f(simulated_camera_pos_location, simulated_camera_pos.x, simulated_camera_pos.y, simulated_camera_pos.z)

    light_source_pos_location = glGetUniformLocation(shader_program, "light_source_pos")
    glUniform3f(light_source_pos_location, light_source_pos.x, light_source_pos.z, light_source_pos.y)

    light_intensity_location = glGetUniformLocation(shader_program, "light_intensity")
    glUniform1f(light_intensity_location, light_power)  # for example, 5 times brighter

    camera_static_pos_loc = glGetUniformLocation(shader_program, "simulated_camera_pos")
    glUniform3f(camera_static_pos_loc, camera_static_pos.x, camera_static_pos.z, camera_static_pos.y)

    
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(window)

    # Render the minimap
    glfw.make_context_current(minimap_window)
    draw_minimap()
    glfw.swap_buffers(minimap_window)

    glfw.poll_events()

# Cleanup
glfw.destroy_window(minimap_window)

glfw.terminate()


