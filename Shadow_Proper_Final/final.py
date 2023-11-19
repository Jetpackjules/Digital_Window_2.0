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

# Parameters (CHANGE THESE AT WILL!)
ROOM_DEPTH: float = 2
ROOM_SIZE: float = monitor_height/1.5
QUAD_SIZE: float = monitor_height/1.5  # Change this value to scale the quad

Background_Color = glm.vec4(0.8, 0.8, 0.8, 1.0)
fullscreen = True
normal_intensity = 1.0  # Adjust this value to scale the normals

shininess = 32.0



distance_from_quad = 1.0 #Since this is ortho this has no bearing on actual render, just has to be a positive number...
camera_pos = glm.vec3(0.0, 0.0, distance_from_quad)

simulated_camera_pos = glm.vec3(0.0, 1.0, 0.0)
light_source_pos = glm.vec3(0.0, 0.0, 0.4)

light_power = 5.0

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
with open('Shadow_Proper_Final/vertex_shader.glsl', 'r') as f:
    vertex_shader_source = f.read()

with open('Shadow_Proper_Final/fragment_shader.glsl', 'r') as f:
    fragment_shader_source = f.read()


vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
check_shader_compilation(vertex_shader)

fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
check_shader_compilation(fragment_shader)

shader_program = compileProgram(vertex_shader, fragment_shader)
check_program_linking(shader_program)
glUseProgram(shader_program)


# MAIN QUAD: ---------------------------------------------------

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

# --------------------------------------------------------------------

# SETTING UP OTHER QUAD AND ITS SHADER: --------------------------------------------


# Adjust the offset as needed
offset = QUAD_SIZE

red_quad_vertices = [
    # Positions                 # UVs
    -QUAD_SIZE/2 - offset,  QUAD_SIZE/2+offset, 0.0,  0.0, 1.0,
    -QUAD_SIZE/2 - offset, -QUAD_SIZE/2-offset, 0.0,  0.0, 0.0,
     QUAD_SIZE/2 + offset, -QUAD_SIZE/2-offset, 0.0,  1.0, 0.0,
     QUAD_SIZE/2 + offset,  QUAD_SIZE/2+offset, 0.0,  1.0, 1.0
]

# Create VBO and EBO for the red quad
red_quad_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, red_quad_VBO)
glBufferData(GL_ARRAY_BUFFER, (GLfloat * len(red_quad_vertices))(*red_quad_vertices), GL_STATIC_DRAW)


red_quad_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, red_quad_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, (GLuint * len(indices))(*indices), GL_STATIC_DRAW)






# ------------------------------------------------------------


# ---------------------
get_shader_deets.print_attribs(shader_program)
get_shader_deets.print_uniforms(shader_program)
# ---------------------


# Vertex Attribute (Position)
position = glGetAttribLocation(shader_program, "inVertex")
glEnableVertexAttribArray(position)
glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))

# Enable and set the pointer for texture coordinates
texCoord = glGetAttribLocation(shader_program, "TexCoordsCustom")  # Change "inTexCoord" to the name used in your shader
print(texCoord)
glEnableVertexAttribArray(texCoord)
glVertexAttribPointer(texCoord, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))


# glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
# glBindBuffer(GL_ARRAY_BUFFER, VBO)



#initing cubemap:
cubemap = cubemap_management.load_cubemap("cubemap")
glActiveTexture(GL_TEXTURE0)  # Use the first texture unit
glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)

# # Initializing normal cubemap
glActiveTexture(GL_TEXTURE1)  # Use the second texture unit
cubemap_normal = cubemap_management.load_cubemap("cubemap_normal")
glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap_normal)
cubemap_normal_location = glGetUniformLocation(shader_program, "cubemap_normalmap")
glUniform1i(cubemap_normal_location, 1)  # 1 refers to GL_TEXTURE1

cubemap_location = glGetUniformLocation(shader_program, "cubemap_albedo")
glUniform1i(cubemap_location, 0)  # 0 refers to GL_TEXTURE0

#KEY INPUT MANAGEMENT:
camera_target = glm.vec3(0.0, 0.0, 0.0)
camera_up = glm.vec3(0.0, 1.0, 0.0)

def key_callback(window, key, scancode, action, mods):
    global light_source_pos, light_power, normal_intensity, shininess, simulated_camera_pos
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
            normal_intensity -= move_speed/3
        if key == glfw.KEY_RIGHT_BRACKET:
            normal_intensity += move_speed/3
        if key == glfw.KEY_M:
            shininess += move_speed*2
        if key == glfw.KEY_N:
            shininess -= move_speed*2

        if key == glfw.KEY_W:
            simulated_camera_pos.y -= move_speed
        if key == glfw.KEY_S:
            simulated_camera_pos.y += move_speed
        if key == glfw.KEY_A:
            simulated_camera_pos.x -= move_speed
        if key == glfw.KEY_D:
            simulated_camera_pos.x += move_speed
        
        get_shader_deets.modify(shader_program, "shininess", shininess)

glfw.set_key_callback(window, key_callback)
simulated_camera_pos_location = glGetUniformLocation(shader_program, "simulated_camera_pos")

# Set the background color to, for example, a light gray
glClearColor(Background_Color.r, Background_Color.g, Background_Color.b, Background_Color.a)

# setting values...
get_shader_deets.modify(shader_program, "room_depth", ROOM_DEPTH)
get_shader_deets.modify(shader_program, "ROOM_SIZE", ROOM_SIZE)

get_shader_deets.modify(shader_program, "wall", False)


#some cam variables:
near_plane = 0.001
far_plane = 100000.0

# ------------------------------------------------------------------------------ SHADOW SHIT
# Function to compile shaders and create a shader program
def create_shader_program(vertex_source_path, fragment_source_path):
    with open(vertex_source_path, 'r') as file:
        vertex_shader_source = file.read()
    with open(fragment_source_path, 'r') as file:
        fragment_shader_source = file.read()

    vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
    check_shader_compilation(vertex_shader)
    fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
    check_shader_compilation(fragment_shader)

    shader_program = compileProgram(vertex_shader, fragment_shader)
    check_program_linking(shader_program)

    return shader_program

# Initialize the shadow shader program
shadow_shader_program = create_shader_program('Shadow_Proper_Final\shadow_vertex_shader.glsl', 'Shadow_Proper_Final\shadow_fragment_shader.glsl')


# Shadow mapping parameters
SHADOW_WIDTH = 1024
SHADOW_HEIGHT = 1024

# Create depth texture
depthMapFBO = glGenFramebuffers(1)
depthMap = glGenTextures(1)
glActiveTexture(GL_TEXTURE2)  # Use a different texture unit
glBindTexture(GL_TEXTURE_2D, depthMap)
glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, 
             SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
borderColor = [1.0, 1.0, 1.0, 1.0]
glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor)

# Attach depth texture as FBO's depth buffer
glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthMap, 0)
glDrawBuffer(GL_NONE)
glReadBuffer(GL_NONE)
glBindFramebuffer(GL_FRAMEBUFFER, 0)




# Render the scene from the light's perspective
# ... (render your objects here)

# Unbind the shadow map FBO
# glBindFramebuffer(GL_FRAMEBUFFER, 0)


# Main loop
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    # glUseProgram(shader_program)

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
    # DOING LIGHT STUFF:

    # Inside the main loop, before glDrawElements call
    light_source_pos_location = glGetUniformLocation(shader_program, "light_source_pos")
    glUniform3f(light_source_pos_location, light_source_pos.x, light_source_pos.y, light_source_pos.z)

    light_intensity_location = glGetUniformLocation(shader_program, "light_intensity")
    glUniform1f(light_intensity_location, light_power)

    normal_intensity_location = glGetUniformLocation(shader_program, "normal_intensity")
    glUniform1f(normal_intensity_location, normal_intensity)

    # ------------------------------------------------------------

    # PASSING IN FAKE CAM POS:
    # acuro_pos = acuro.get_acuro_pos()
    acuro_pos = tracker.get_face_pos()

    if (acuro_pos is not None):
        simulated_camera_pos.x = round(-acuro_pos[0], 3)
        simulated_camera_pos.z = round(-acuro_pos[1]+monitor_height/2, 3)

        #ADJUST POS FOR WEIRD ACURO SCALING!!
        simulated_camera_pos.y = round(acuro_pos[2], 3)
        
    glUniform3f(simulated_camera_pos_location, simulated_camera_pos.x, simulated_camera_pos.y, simulated_camera_pos.z)





    # RENDERING WALL QUAD(S): ---------------------------------------------------------------

    get_shader_deets.modify(shader_program, "wall", True)
    # Bind the VBO and EBO for the red quad
    glBindBuffer(GL_ARRAY_BUFFER, red_quad_VBO)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, red_quad_EBO)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))

    # Draw the red quad
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
    get_shader_deets.modify(shader_program, "wall", False)

    # RENDERING CENTER QUAD: ---------------------------------------------------------------

    # Bind the VBO and EBO for the red quad
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))

    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
    # --------------------------------------------------------------------------------------- LIGHT STUFF:

    # Bind the shadow map FBO
    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
    glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT)
    glClear(GL_DEPTH_BUFFER_BIT)

    # Use the shadow shader program
    glUseProgram(shadow_shader_program)

    # Set up light's perspective view and projection
    lightProjection = glm.ortho(-10.0, 10.0, -10.0, 10.0, near_plane, far_plane)
    lightView = glm.lookAt(light_source_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
    lightSpaceMatrix = lightProjection * lightView

    # Pass lightSpaceMatrix to shadow shader
    lightSpaceMatrixLoc = glGetUniformLocation(shadow_shader_program, "lightSpaceMatrix")
    glUniformMatrix4fv(lightSpaceMatrixLoc, 1, GL_FALSE, glm.value_ptr(lightSpaceMatrix))
    
    # RENDERING SCNEEE =======================================================================================
    # Bind the default framebuffer
    # glViewport(0, 0, int(monitor_width*100/2.54*monitor_dpi), int(monitor_height*100/2.54*monitor_dpi))
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Use the main shader program
    glUseProgram(shader_program)

    # Bind the shadow map as a texture
    glActiveTexture(GL_TEXTURE2)  # Use a different texture unit
    glBindTexture(GL_TEXTURE_2D, depthMap)
    shadowMapLoc = glGetUniformLocation(shader_program, "shadowMap")
    glUniform1i(shadowMapLoc, 2)  # Corresponds to GL_TEXTURE2




    # Unbind the shadow map FBO
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    glUseProgram(shader_program)


    glfw.swap_buffers(window)

glfw.terminate()
