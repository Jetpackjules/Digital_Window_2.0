#version 330 core

uniform float ROOM_SIZE;
uniform mat4 view_matrix;


uniform samplerCube cubemap_albedo;
uniform samplerCube cubemap_normalmap;
uniform samplerCube cubemap_emission;

uniform float room_depth;
uniform float emission_strength;
uniform vec2 resolution;


in vec3 obj_vertex;
flat in vec3 obj_cam;

out vec4 FragColor;

float remap_range(float value, float min_in, float max_in, float min_out, float max_out) {
    return (value - min_in) / (max_in - min_in) * (max_out - min_out) + min_out;
}

vec3 sample_cubemap_better(samplerCube cubemap, vec3 direction) {
    return texture(cubemap, direction).rgb;
}

vec3 correct_cubemap(vec3 direction, vec3 cm_face) {
    // Adjust for side walls being 90 degrees sideways
    if (abs(cm_face.x) > 0.5) {
        direction = vec3(direction.x, -direction.z, direction.y);
    }

    // Adjust for floor and roof being inversed
    if (cm_face.y > 0.5) {
        direction.y = -direction.y; // invert the roof
    } else if (cm_face.y < -0.5) {
        direction.y = -direction.y; // invert the floor
    }

    // Adjust for back wall being upside down
    if (cm_face.z > 0.5) { // Assuming the back wall has cm_face.z > 0
        direction.y = -direction.y; // invert the vertical direction
    }

    return direction;
}

vec3 uvToDirection(vec2 uv, vec3 face) {
    if(face.x != 0.0) {
        return normalize(vec3(face.x, (uv.y - 0.5) * 2.0, (uv.x - 0.5) * 2.0));
    } else if(face.y != 0.0) {
        return normalize(vec3((uv.x - 0.5) * 2.0, face.y, (uv.y - 0.5) * 2.0));
    } else if(face.z != 0.0) {
        return normalize(vec3((uv.x - 0.5) * 2.0, (uv.y - 0.5) * 2.0, face.z));
    }
    return vec3(0.0);
}

void main() {
    vec3 cm_face = vec3(0., 0., 1.);
    vec2 cm_uv = vec2(0,0);
        
	//cm_uv.xy = cm_uv.yx;
		
    if (room_depth != 0.) {
        float depth = room_depth * 2.;
        vec3 cam2pix = obj_vertex - obj_cam;

		
        //camp2pix.z <= 0 --> show floor
        //camp2pix.z > 0 --> show ceiling
        float is_floor = step(cam2pix.y, 0.);  // Use y instead of z
        float ceil_y   = ceil(obj_vertex.y / depth - is_floor) * depth;
        float ceil_t   = (ceil_y - obj_cam.y) / cam2pix.y;
        
        //camp2pix.x <= 0 --> show north
        //camp2pix.x > 0 --> show south
        float is_north = step(cam2pix.x, 0.);
        float wall_f_x = ceil(obj_vertex.x / ROOM_SIZE - is_north) * ROOM_SIZE;
        float wall_f_t = (wall_f_x - obj_cam.x) / cam2pix.x;
        
        //camp2pix.y <= 0 --> show east
        //camp2pix.y > 0 --> show west
        float is_east  = step(cam2pix.z, 0.);
        float wall_e_y = ceil(obj_vertex.z / ROOM_SIZE - is_east*1.) * ROOM_SIZE;
        float wall_e_t = (wall_e_y - obj_cam.z) / cam2pix.z;
        
        vec2 tex_coord;
        float min_t = min(min(ceil_t, wall_e_t), wall_f_t);
        
        if (wall_e_t == min_t) {
            //East / West
            tex_coord = obj_cam.xy + wall_e_t * cam2pix.xy * 1.0;
            cm_face = vec3(0., (is_east == 0.) ? 1. : -1., 0.);
        }
        else if (wall_f_t == min_t) {
            //Front / Back
            tex_coord = obj_cam.zy + wall_f_t * cam2pix.zy * 1.;
            cm_face = vec3((is_north == 0.) ? -1. : 1., 0., 0.);
        }
        else if (ceil_t == min_t) {
            //Ceiling / Floor
            tex_coord = obj_cam.xz + ceil_t * cam2pix.xz;
            cm_face = vec3(0., 0., (is_floor == 0.) ? -1. : 1.);
        }
        
        if (!(ceil_t == min_t)) {
            tex_coord.y /= room_depth*1.;
        }
        
        cm_uv = (tex_coord*.5 + 1.);
        
        cm_uv.x = clamp(cm_uv.x, 0., 1.);
        cm_uv.y = clamp(cm_uv.y, 0., 1.);

    }   


    vec3 directionFromUV = uvToDirection(cm_uv, (cm_face));
    directionFromUV = correct_cubemap(directionFromUV, cm_face);
    vec3 albedo = sample_cubemap_better(cubemap_albedo, directionFromUV);
    FragColor = vec4(albedo, 1.0);


}
