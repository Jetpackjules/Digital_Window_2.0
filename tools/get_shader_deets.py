import OpenGL.GL as GL
from OpenGL.GL import *


def print_uniforms(shader_program):
    # Get the number of active uniforms in the shader program
    num_uniforms = GL.glGetProgramiv(shader_program, GL.GL_ACTIVE_UNIFORMS)

    print(" Index | Uniform")
    print("------------------------------------------------")
    
    for i in range(num_uniforms):
        # Get the name, size, and type of the uniform at index 'i'
        name, size, uniform_type = GL.glGetActiveUniform(shader_program, i)
        location = GL.glGetUniformLocation(shader_program, name)

        print(f"{location} | {name.decode('utf-8')}")

    print("##############################################################################")


def print_attribs(shader_program):
    # Assuming shader_program is your shader program's handle
    nAttribs = glGetProgramiv(shader_program, GL_ACTIVE_ATTRIBUTES)
    maxLength = glGetProgramiv(shader_program, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)

    print(" Index | Attribute")
    print("------------------------------------------------")

    for i in range(nAttribs):
        name, size, type = glGetActiveAttrib(shader_program, i, maxLength)
        location = glGetAttribLocation(shader_program, name)
        print(f" {location:<5} | {name.decode('utf-8')}")

    print("##############################################################################")


def modify(shader_program, name, val):
    location = glGetUniformLocation(shader_program, name)
    if location == -1:
        print(f"Error: Uniform '{name}' not found in the shader program.")
    else:
        glUniform1f(location, val) 
