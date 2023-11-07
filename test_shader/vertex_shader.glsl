#version 330 core

uniform float ROOM_SIZE = 3.0;

uniform float room_depth;
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;

layout(location = 0) in vec3 inVertex;

out vec3 obj_vertex;
flat out vec3 obj_cam;


void main() {
    if (room_depth != 0.0) {
        vec2 d = vec2(ROOM_SIZE, ROOM_SIZE) / 2.0;
        vec3 delta = vec3(d.x, 0.0, d.y);

        obj_vertex = inVertex.xzy - delta;

        // Offset along the Y-axis by half the room size
        //obj_vertex.y += ROOM_SIZE / 2.0;


        obj_cam = (inverse(modelViewMatrix) * vec4(0.0, 0.0, 0.0, 1.0)).xzy - delta;
        //obj_cam.y += ROOM_SIZE / 2.0;
    }

    gl_Position = projectionMatrix * modelViewMatrix * vec4(inVertex, 1.0);
}
