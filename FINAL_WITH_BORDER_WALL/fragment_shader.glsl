#version 330 core

uniform float ROOM_SIZE;

uniform samplerCube cubemap_albedo;
uniform samplerCube cubemap_normalmap;
uniform samplerCube cubemap_emission;

uniform float room_depth;
uniform float emission_strength;

uniform vec3 simulated_camera_pos;

in vec3 obj_vertex;
flat in vec3 obj_cam;

out vec4 FragColor;

uniform vec3 light_source_pos;
uniform float light_intensity;
uniform float normal_intensity;
uniform vec3 light_color = vec3(1., 1., 1.);


uniform float shininess = 32.0; // Or any other value you want for shininess


float calculateShadowFactor(vec3 fragPos, vec3 normal) {
    // Your shadow calculation code goes here.
    // For now, let's return 1.0 to indicate no shadow.
    return 1.0;
}


vec3 calculateLighting(vec3 normal, vec3 fragPos, vec3 viewDir, vec3 lightPos, float lightIntensity) {
    vec3 lightDir = normalize(lightPos - fragPos);
    float distance = length(lightPos - fragPos);
    
    // Attenuation coefficients
    const float constant = 1.0;
    const float linear = 0.09;
    const float quadratic = 0.032;
    
    // Attenuation
    float attenuation = 1.0 / (constant + linear * distance + quadratic * (distance * distance));
    
    // Now apply the attenuation to the light intensity
    lightIntensity *= attenuation;
    
    // Rest of the lighting calculations...
    vec3 halfVec = normalize(lightDir + viewDir);
    normal = normalize(normal * 2.0 - 1.0); // Unpack the normal from [0,1] to [-1,1]
    float diff = max(dot(normal, lightDir), 0.0);
    float spec = pow(max(dot(normal, halfVec), 0.0), shininess);
    vec3 diffuse = diff * light_color.rgb * lightIntensity;
    vec3 specular = spec * light_color.rgb * lightIntensity;
    float shadowFactor = calculateShadowFactor(fragPos, normal);
    
    return (diffuse + specular) * shadowFactor;
}



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

vec3 uvToDirection(vec2 uv, vec3 face, bool isMiddleThird) {
    // Scale down the direction changes within the middle third
    if (isMiddleThird) {
        uv = (uv - 0.33) / 0.33;
    }

    if(face.x != 0.0) {
        return isMiddleThird ? normalize(vec3(face.x, (uv.y - 0.5) * 2.0, (uv.x - 0.5) * 2.0)) 
                             : vec3(face.x, 0.0, 0.0);
    } else if(face.y != 0.0) {
        return isMiddleThird ? normalize(vec3((uv.x - 0.5) * 2.0, face.y, (uv.y - 0.5) * 2.0)) 
                             : vec3(0.0, face.y, 0.0);
    } else if(face.z != 0.0) {
        return isMiddleThird ? normalize(vec3((uv.x - 0.5) * 2.0, (uv.y - 0.5) * 2.0, face.z)) 
                             : vec3(0.0, 0.0, face.z);
    }
    return vec3(0.0);
}



void main() {
    vec3 cm_face = vec3(0., 0., 1.);
    vec2 cm_uv = vec2(0,0);

    float adjustedRoomSize = ROOM_SIZE / 3.0;
    vec3 camRelativePos = obj_vertex - obj_cam;
    vec3 normalizedPos = camRelativePos / ROOM_SIZE + 0.5; // Normalize position to [0, 1]

    // Check if we are in the middle third in both X and Y directions
    bool isMiddleThirdX = normalizedPos.x > 1.0/3.0 && normalizedPos.x < 2.0/3.0;
    bool isMiddleThirdY = normalizedPos.y > 1.0/3.0 && normalizedPos.y < 2.0/3.0;
    bool isMiddleThird = isMiddleThirdX && isMiddleThirdY;

    if (room_depth != 0.) {
        float depth = room_depth * adjustedRoomSize;
        vec3 cam2pix = obj_vertex - obj_cam;

        float is_floor = step(cam2pix.y, 0.);
        float ceil_y = ceil(obj_vertex.y / depth - is_floor) * depth;
        float ceil_t = (ceil_y - obj_cam.y) / cam2pix.y;

        float is_north = step(cam2pix.x, 0.);
        float wall_f_x = ceil(obj_vertex.x / adjustedRoomSize - is_north) * adjustedRoomSize;
        float wall_f_t = (wall_f_x - obj_cam.x) / cam2pix.x;

        float is_east = step(cam2pix.z, 0.);
        float wall_e_y = ceil(obj_vertex.z / adjustedRoomSize - is_east) * adjustedRoomSize;
        float wall_e_t = (wall_e_y - obj_cam.z) / cam2pix.z;

        vec2 tex_coord;
        float min_t = min(min(ceil_t, wall_e_t), wall_f_t);

        if (wall_e_t == min_t) {
            tex_coord = obj_cam.xy + wall_e_t * cam2pix.xy * 1.0;
            cm_face = vec3(0., (is_east == 0.) ? 1. : -1., 0.);
        } else if (wall_f_t == min_t) {
            tex_coord = obj_cam.zy + wall_f_t * cam2pix.zy * 1.;
            cm_face = vec3((is_north == 0.) ? -1. : 1., 0., 0.);
        } else if (ceil_t == min_t) {
            tex_coord = obj_cam.xz + ceil_t * cam2pix.xz;
            cm_face = vec3(0., 0., (is_floor == 0.) ? -1. : 1.);
        }

        if (isMiddleThird) {
            tex_coord = (tex_coord - vec2(ROOM_SIZE / 3.0)) / (ROOM_SIZE / 3.0);
        } else {
            tex_coord = fract(tex_coord / ROOM_SIZE);
        }

        cm_uv = tex_coord;
    }
    vec3 direction = uvToDirection(cm_uv, cm_face, isMiddleThird);
    direction = correct_cubemap(direction, cm_face);

    vec3 normal = sample_cubemap_better(cubemap_normalmap, direction) * normal_intensity;
    vec3 viewDir = normalize(simulated_camera_pos - obj_vertex);
    vec3 lighting = calculateLighting(normal, obj_vertex, viewDir, light_source_pos, light_intensity);

    vec3 albedo;
    if (!isMiddleThird) {
        // Set albedo to red for quads not in the middle third
        albedo = vec3(1.0, 0.0, 0.0);
    } else {
        // Sample the albedo from the cubemap for the middle third
        albedo = sample_cubemap_better(cubemap_albedo, direction);
    }

    FragColor = vec4(albedo * lighting, 1.0);
}