#version 330 core

uniform float ROOM_WIDTH;
uniform float ROOM_HEIGHT;
uniform float ROOM_SIZE;

uniform float room_depth;
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
uniform vec3 simulated_camera_pos;

layout(location = 0) in vec3 inVertex;

out vec3 obj_vertex;
flat out vec3 obj_cam;


void main() {
    if (room_depth != 0.0) {
        //vec2 d = vec2(ROOM_SIZE, ROOM_SIZE) / 2.0;
        vec2 d = vec2(ROOM_WIDTH, ROOM_HEIGHT) / 2.0;

        vec3 delta = vec3(d.x, 0.0, d.y);

        obj_vertex = inVertex.xzy - delta;

        obj_cam = (inverse(modelViewMatrix) * vec4(0.0, 0.0, 0.0, 1.0)).xzy - delta;
        
        //adjusting for perspective:
        obj_cam += simulated_camera_pos;
    }

    gl_Position = projectionMatrix * modelViewMatrix * vec4(inVertex, 1.0);
}
