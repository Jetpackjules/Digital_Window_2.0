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

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(os.path.join(parent_dir, 'tools'))

# Now you can import the module
import cubemap_management
import get_shader_deets

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
window = glfw.create_window(800, 600, "GLFW Window", None, None)
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

glfw.set_window_pos(window, 400, 200)
glfw.make_context_current(window)

# Load shaders from files
with open('test_shader/vertex_shader.glsl', 'r') as f:
    vertex_shader_source = f.read()

with open('test_shader/fragment_shader.glsl', 'r') as f:
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


uv_location = glGetAttribLocation(shader_program, "inUV")
if uv_location != -1:  # Ensure the attribute was found
    glEnableVertexAttribArray(uv_location)
    glVertexAttribPointer(uv_location, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
else:
    print("Warning: inUV attribute not found in the shader.")

# # # UV attribute
# glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
# glEnableVertexAttribArray(1)




#initing cubemap:
cubemap = cubemap_management.load_cubemap("cubemap")
glActiveTexture(GL_TEXTURE0)  # Use the first texture unit
glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)

cubemap_location = glGetUniformLocation(shader_program, "cubemap_albedo")
glUniform1i(cubemap_location, 0)  # 0 refers to GL_TEXTURE0

camera_pos = glm.vec3(0.0, 0.0, 1.4)
camera_static_pos = glm.vec3(0.0, 0.0, 1.4)


#KEY INPUT MANAGEMENT:
camera_target = glm.vec3(0.0, 0.0, 0.0)
camera_up = glm.vec3(0.0, 1.0, 0.0)

def key_callback(window, key, scancode, action, mods):
    global camera_pos
    move_speed = 0.1  # Adjust this value for faster/slower movement

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_UP:
            camera_pos.y += move_speed
        if key == glfw.KEY_DOWN:
            camera_pos.y -= move_speed
        if key == glfw.KEY_LEFT:
            camera_pos.x -= move_speed
        if key == glfw.KEY_RIGHT:
            camera_pos.x += move_speed

glfw.set_key_callback(window, key_callback)

# Main loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT)

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
    aspect_ratio = 800.0 / 600.0  # Assuming an 800x600 window size
    near_plane = 0.001
    far_plane = 1000.0

    projection_matrix = glm.perspective(fov, aspect_ratio, near_plane, far_plane)

    # Now, you can pass this matrix to your shader:
    location = glGetUniformLocation(shader_program, "projectionMatrix")

    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(projection_matrix))




    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(window)

# Cleanup
glfw.terminate()
