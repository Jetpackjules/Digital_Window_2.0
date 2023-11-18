#version 330 core

uniform float ROOM_SIZE;
uniform bool wall;

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

in vec3 TexCoordsProcessed;

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
    if (wall) {
        // Remap TexCoordsProcessed from [0, 1] to [-1, 1]
        vec2 remappedCoords = TexCoordsProcessed.xy * 2.0 - 1.0;

        // Sample the left face of the cubemap
        vec3 dir = vec3(-1.0, -remappedCoords.y, remappedCoords.x);
        vec3 color = texture(cubemap_normalmap, dir).rgb;

        // Output the color
        FragColor = vec4(color, 1.0);
    
    
    } else {
            
        vec3 cm_face = vec3(0., 0., 1.);
        vec2 cm_uv = vec2(0,0);
                        
        if (room_depth != 0.) {
            float depth = room_depth * ROOM_SIZE;
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
            
            float scaler = 1./ROOM_SIZE;
            cm_uv = (tex_coord*scaler + 1.);

            cm_uv.x = clamp(cm_uv.x, 0., 1.);
            cm_uv.y = clamp(cm_uv.y, 0., 1.);

        }   


        //vec3 directionFromUV = uvToDirection(cm_uv, (cm_face));
        //directionFromUV = correct_cubemap(directionFromUV, cm_face);
        //vec3 albedo = sample_cubemap_better(cubemap_albedo, directionFromUV);
        //FragColor = vec4(albedo, 1.0);

        // Calculate the direction for sampling the cubemap
        vec3 direction = uvToDirection(cm_uv, cm_face);
        direction = correct_cubemap(direction, cm_face);

        // Sample the normal map using the corrected direction
        vec3 normal = sample_cubemap_better(cubemap_normalmap, direction) * normal_intensity;

        // Calculate the view direction
        vec3 viewDir = normalize(simulated_camera_pos - obj_vertex);

        // Calculate the lighting with attenuation
        vec3 lighting = calculateLighting(normal, obj_vertex, viewDir, light_source_pos, light_intensity);

        // Sample the albedo from the cubemap
        vec3 albedo = sample_cubemap_better(cubemap_albedo, direction);

        // Combine the albedo and lighting, and output the final color
        FragColor = vec4(albedo * lighting, 1.0);


    }
}
