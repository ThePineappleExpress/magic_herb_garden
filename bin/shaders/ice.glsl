#ifdef GL_ES
precision mediump float;
#endif

uniform float time;
uniform vec2 resolution;
uniform vec3 color_a;
uniform vec3 color_b;
uniform float pixel_scale;

vec3 screen(vec3 base, vec3 blend) {
    return 1.0 - (1.0 - base) * (1.0 - blend);
}
vec3 color_dodge(vec3 base, vec3 blend) {
    return clamp(base / (1.0 - clamp(blend, 0.0, 0.999)), 0.0, 1.0);
}
// Soft Light - gentler overlay; blend < 0.5 darkens softly, > 0.5 lightens softly
vec3 soft_light(vec3 base, vec3 blend) {
    return mix(
        2.0 * base * blend + base * base * (1.0 - 2.0 * blend),
        sqrt(base) * (2.0 * blend - 1.0) + 2.0 * base * (1.0 - blend),
        step(0.5, blend)
    );
}
vec3 multiply(vec3 base, vec3 blend) {
    return base * blend;
}
vec3 overlay(vec3 base, vec3 blend) {
    return mix(
        2.0 * base * blend,
        1.0 - 2.0 * (1.0 - base) * (1.0 - blend),
        step(0.5, base)
    );
}
float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(11.1234, 31.420))) * 1175.4846);
}

vec2 hash(vec2 seed) {
    seed = vec2(dot(seed, vec2(127.1, 311.7)), dot(seed, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(seed) * 43758.5453123);
}

float noise(vec2 pos) {
    vec2 grid_cell = floor(pos);
    vec2 frac_pos = fract(pos);
    float corner_bl = rand(grid_cell);
    float corner_br = rand(grid_cell + vec2(1.0, 0.0));
    float corner_tl = rand(grid_cell + vec2(0.0, 1.0));
    float corner_tr = rand(grid_cell + vec2(1.0, 1.0));
    vec2 smooth_step = frac_pos * frac_pos * (3.0 - 2.0 * frac_pos);
    return mix(corner_bl, corner_br, smooth_step.x) +
           (corner_tl - corner_bl) * smooth_step.y * (1.0 - smooth_step.x) +
           (corner_tr - corner_br) * smooth_step.x * smooth_step.y;
}

float fbm(vec2 pos) {
    float noise_value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    for (int i = 0; i < 5; i++) {
        noise_value += amplitude * noise(pos * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }
    return noise_value;
}

float voronoi_slow(in vec2 uv) {
    vec2 grid_cell = floor(uv);
    vec2 frac_pos = fract(uv);
    float min_dist = 1.0;
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 neighbor_cell = grid_cell + vec2(i, j);
            vec2 cell_offset = hash(neighbor_cell);
            cell_offset = 0.5 + 0.5 * sin(cell_offset * 6.2831 + (time * 0.01));
            vec2 offset_diff = vec2(i, j) + cell_offset - frac_pos;
            min_dist = min(min_dist, dot(offset_diff, offset_diff));
        }
    }
    return sqrt(min_dist);
}

float voronoi_fast(in vec2 uv) {
    vec2 grid_cell = floor(uv);
    vec2 frac_pos = fract(uv);
    float min_dist = 1.0;
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 neighbor_cell = grid_cell + vec2(i, j);
            vec2 cell_offset = hash(neighbor_cell);
            cell_offset = 0.5 + 0.5 * sin(cell_offset * 6.2831 + (time * 0.1));
            vec2 offset_diff = vec2(i, j) + cell_offset - frac_pos;
            min_dist = min(min_dist, dot(offset_diff, offset_diff));
        }
    }
    return sqrt(min_dist);
}

float voronoi_cell_noise_slow(in vec2 uv) {
    vec2 grid_cell = floor(uv);
    vec2 frac_pos = fract(uv);
    float min_dist = 1.0;
    vec2 closest_cell = vec2(0.0);
    vec2 closest_cell_center = vec2(0.0);
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 neighbor_cell = grid_cell + vec2(i, j);
            vec2 cell_offset = hash(neighbor_cell);
            vec2 cell_offset_animated = 0.5 + 0.5 * sin(cell_offset * 6.2831 + (time * 0.01));
            vec2 offset_diff = vec2(i, j) + cell_offset_animated - frac_pos;
            float dist = dot(offset_diff, offset_diff);
            if (dist < min_dist) {
                min_dist = dist;
                vec2 cell_offset_static = 0.5 + 0.5 * sin(cell_offset * 6.2831);
                closest_cell = neighbor_cell + cell_offset_static;
                closest_cell_center = vec2(i, j) + cell_offset_animated;
            }
        }
    }
    float cell_angle = rand(closest_cell + vec2(7.3, 2.1)) * 6.2831;
    vec2 grad_dir = vec2(cos(cell_angle), sin(cell_angle));
    float gradient = dot(frac_pos - closest_cell_center, grad_dir) * 1.5 + 0.5;
    gradient = clamp(gradient, 0.0, 1.0);
    float cell_shade = rand(closest_cell);
    return mix(cell_shade * 0.4, cell_shade, gradient);
}

float voronoi_cell_noise_fast(in vec2 uv) {
    vec2 grid_cell = floor(uv);
    vec2 frac_pos = fract(uv);
    float min_dist = 1.0;
    vec2 closest_cell = vec2(0.0);
    vec2 closest_cell_center = vec2(0.0);
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 neighbor_cell = grid_cell + vec2(i, j);
            vec2 cell_offset = hash(neighbor_cell);
            vec2 cell_offset_animated = 0.5 + 0.5 * sin(cell_offset * 6.2831 + (time * 0.1));
            vec2 offset_diff = vec2(i, j) + cell_offset_animated - frac_pos;
            float dist = dot(offset_diff, offset_diff);
            if (dist < min_dist) {
                min_dist = dist;
                vec2 cell_offset_static = 0.5 + 0.5 * sin(cell_offset * 6.2831);
                closest_cell = neighbor_cell + cell_offset_static;
                closest_cell_center = vec2(i, j) + cell_offset_animated;
            }
        }
    }
    float cell_angle = rand(closest_cell + vec2(7.3, 2.1)) * 6.2831;
    vec2 grad_dir = vec2(cos(cell_angle), sin(cell_angle));
    float gradient = dot(frac_pos - closest_cell_center, grad_dir) * 1.5 + 0.5;
    gradient = clamp(gradient, 0.0, 1.0);
    float cell_shade = rand(closest_cell);
    return mix(cell_shade * 0.4, cell_shade, gradient);
}

vec2 voronoi_cell_edge_fast(in vec2 uv) {
    vec2 grid_cell = floor(uv);
    vec2 frac_pos = fract(uv);
    float min_dist = 1.0;
    float min_dist2 = 1.0;
    vec2 closest_cell = vec2(0.0);
    vec2 closest_cell_center = vec2(0.0);
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 neighbor_cell = grid_cell + vec2(i, j);
            vec2 cell_offset = hash(neighbor_cell);
            vec2 cell_offset_animated = 0.5 + 0.5 * sin(cell_offset * 6.2831 + (time * 0.1));
            vec2 offset_diff = vec2(i, j) + cell_offset_animated - frac_pos;
            float dist = dot(offset_diff, offset_diff);
            if (dist < min_dist) {
                min_dist2 = min_dist; 
                min_dist = dist;
                vec2 cell_offset_static = 0.5 + 0.5 * sin(cell_offset * 6.2831);
                closest_cell = neighbor_cell + cell_offset_static;
                closest_cell_center = vec2(i, j) + cell_offset_animated;
            } else if (dist < min_dist2) {
                min_dist2 = dist;
            }
        }
    }

    float cell_angle = rand(closest_cell + vec2(7.3, 2.1)) * 6.2831;
    vec2 grad_dir = vec2(cos(cell_angle), sin(cell_angle));
    float gradient = dot(frac_pos - closest_cell_center, grad_dir) * 1.5 + 0.5;
    gradient = clamp(gradient, 0.0, 1.0);
    float cell_shade = rand(closest_cell);
    float cell_noise = mix(cell_shade * 0.4, cell_shade, gradient);
    float edge_band = 1.0 - smoothstep(0.0, 1.7, sqrt(min_dist2) - sqrt(min_dist));
    float edge_glow = edge_band * gradient;
    return vec2(cell_noise, edge_glow);
}

void main(void) {
    vec2 pixCoord = floor(gl_FragCoord.xy / pixel_scale) * pixel_scale + pixel_scale * 0.5;
    vec2 uv = pixCoord / resolution.xy;
    float time_offset = time * 0.01;

    float refract_x_fast = voronoi_fast(uv * 3.0 + time_offset);
    float refract_y_fast = voronoi_fast(uv * 3.0 - time_offset);
    vec2 refracted_uv_fast = uv + vec2(refract_x_fast, refract_y_fast) * 0.5;


    float refract_x_slow = voronoi_slow(uv * 3.0 + vec2(0.0, 2.0) + time_offset);
    float refract_y_slow = voronoi_slow(uv * 3.0 + vec2(2.0, 0.0) - time_offset);
    vec2 refracted_uv_slow = uv + vec2(refract_x_slow, refract_y_slow) * 0.5;

    vec2 fbm_warp = vec2(
        fbm(uv * 3.0 + time_offset),
        fbm(uv * 3.0 - time_offset)
    ) * 0.1;

    vec2 wave_offset;
    wave_offset.x = sin(uv.y * 10.0 + time_offset) * 0.2;
    wave_offset.y = cos(uv.x * 10.0 - time_offset) * 0.2;

    float cell_offset_x = voronoi_cell_edge_fast(uv * 3.0 + vec2(0.0, 2.0) + time_offset).x;
    float cell_offset_y = voronoi_cell_edge_fast(uv * 3.0 + vec2(2.0, 0.0) - time_offset).x;
    vec2 cell_offset = uv + vec2(cell_offset_x, cell_offset_y) * 0.5;

    vec2 final_uv_fast = uv + fbm_warp * refracted_uv_fast;
    vec2 final_uv_slow = uv + fbm_warp * refracted_uv_slow;

    float background = fbm(final_uv_slow + cell_offset * 1.5 + (time_offset * 2.0)) * 0.6;

    float base_voronoi = voronoi_slow(final_uv_fast * 2.0 + cell_offset + (time_offset / 2.0));
    float base_overlay = voronoi_cell_noise_slow(final_uv_fast * 2.0 + cell_offset + (time_offset / 2.0));

    float layer_1_voronoi = voronoi_fast(final_uv_fast * 4.5 + time_offset + wave_offset);
    float layer_1_overlay = voronoi_cell_noise_fast(final_uv_fast * 4.5 + time_offset + wave_offset);

    float layer_2_fbm = fbm(final_uv_slow * 1.0 + time_offset + wave_offset);

    float layer_3_voronoi = voronoi_fast(final_uv_fast + cell_offset - time_offset);
    vec2 layer_3_data = voronoi_cell_edge_fast(final_uv_fast + cell_offset - time_offset);

    float layer_3_overlay = layer_3_data.x;
    float layer_3_edge = layer_3_data.y;

    vec3 background_layer = mix(color_b, color_a, background);
    vec3 base_layer = mix(color_b, vec3(0.0), overlay(vec3(base_voronoi), vec3(base_overlay))) * 0.5;
    vec3 layer_1 = mix(color_a, color_b, overlay(vec3(layer_1_voronoi), vec3(layer_1_overlay))) * 0.5;
    vec3 layer_2 = mix(color_b, color_a, layer_2_fbm ) * 2.0;
    vec3 layer_3 = mix(color_a, color_b, overlay(vec3(layer_3_voronoi), vec3(layer_3_overlay))) * 2.0;

    layer_3 = mix(layer_3, vec3(1.0), layer_3_edge * 1.2);
    layer_2 = mix(layer_3, layer_1, layer_3_edge * 0.5);
    vec3 combined = background_layer;
    combined = screen(combined, base_layer);
    combined = soft_light(combined, layer_1);
    combined = soft_light(combined, layer_2);

    gl_FragColor = vec4(clamp(combined, 0.0, 1.0), 1.0);
}