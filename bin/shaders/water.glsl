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
vec3 lighten(vec3 base, vec3 blend) {
    return max(base, blend);
}
vec3 darken(vec3 base, vec3 blend) {
    return min(base, blend);
}
// Linear Dodge (Add) - base + blend, brighter than screen, no curve
vec3 linear_dodge(vec3 base, vec3 blend) {
    return clamp(base + blend, 0.0, 1.0);
}
// Linear Burn - darkens by adding darkness; opposite of linear dodge
vec3 linear_burn(vec3 base, vec3 blend) {
    return clamp(base + blend - 1.0, 0.0, 1.0);
}
// Color Burn - darkens base to reflect blend by increasing contrast
vec3 color_burn(vec3 base, vec3 blend) {
    return clamp(1.0 - (1.0 - base) / (clamp(blend, 0.001, 1.0)), 0.0, 1.0);
}
vec3 color_dodge(vec3 base, vec3 blend) {
    return clamp(base / (1.0 - clamp(blend, 0.0, 0.999)), 0.0, 1.0);
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
// Hard Light - overlay with base and blend swapped
vec3 hard_light(vec3 base, vec3 blend) {
    return mix(
        2.0 * base * blend,
        1.0 - 2.0 * (1.0 - base) * (1.0 - blend),
        step(0.5, blend)
    );
}
// Soft Light - gentler overlay; blend < 0.5 darkens softly, > 0.5 lightens softly
vec3 soft_light(vec3 base, vec3 blend) {
    return mix(
        2.0 * base * blend + base * base * (1.0 - 2.0 * blend),
        sqrt(base) * (2.0 * blend - 1.0) + 2.0 * base * (1.0 - blend),
        step(0.5, blend)
    );
}
// Difference - absolute difference; black blend = no change, white = inverts
vec3 difference(vec3 base, vec3 blend) {
    return abs(base - blend);
}
// Exclusion - like difference but lower contrast; 0.5 blend = 50% gray
vec3 exclusion(vec3 base, vec3 blend) {
    return base + blend - 2.0 * base * blend;
}
// Divide - brightens base relative to how dark the blend is
vec3 divide(vec3 base, vec3 blend) {
    return clamp(base / (clamp(blend, 0.001, 1.0)), 0.0, 1.0);
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
            cell_offset = 0.5 + 0.5 * sin(cell_offset * 6.2831 + (time * 0.1));
            vec2 offset_diff = vec2(i, j) + cell_offset - frac_pos;
            min_dist = min(min_dist, dot(offset_diff, offset_diff));
        }
    }
    return 1.0 - sqrt(min_dist);
}

float voronoi_fast(in vec2 uv) {
    vec2 grid_cell = floor(uv);
    vec2 frac_pos = fract(uv);
    float min_dist = 1.0;
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 neighbor_cell = grid_cell + vec2(i, j);
            vec2 cell_offset = hash(neighbor_cell);
            cell_offset = 0.5 + 0.5 * sin(cell_offset * 6.2831 + (time * 0.6));
            vec2 offset_diff = vec2(i, j) + cell_offset - frac_pos;
            min_dist = min(min_dist, dot(offset_diff, offset_diff));
        }
    }
    return 1.0 - sqrt(min_dist);
}


void main(void) {
    vec2 pixCoord = floor(gl_FragCoord.xy / pixel_scale) * pixel_scale + pixel_scale * 0.5;
    vec2 uv = pixCoord / resolution.xy;
    float time_offset = time * 0.01;


    float refract_x_fast = voronoi_fast(uv * 3.0 + time_offset);
    float refract_y_fast = voronoi_fast(uv * 3.0 - time_offset);
    vec2 refracted_uv_fast = uv + vec2(refract_x_fast, refract_y_fast) * 0.3;


    float refract_x_slow = voronoi_slow(uv * 3.0 + vec2(0.0, 2.0) + time_offset);
    float refract_y_slow = voronoi_slow(uv * 3.0 + vec2(2.0, 0.0) - time_offset);
    vec2 refracted_uv_slow = uv + vec2(refract_x_slow, refract_y_slow) * 0.1;

    vec2 fbm_warp = vec2(
        fbm(uv + time_offset * 2.0),
        fbm(uv - time_offset * 2.0)
    ) * 0.6 ;

    vec2 wave_offset;
    wave_offset.x = sin(uv.y * 2.0 + time_offset) * 0.2;
    wave_offset.y = cos(uv.x * 2.0 - time_offset) * 0.2;

    vec2 final_uv_fast = uv + refracted_uv_fast - wave_offset;
    vec2 final_uv_slow = uv + refracted_uv_slow + wave_offset;

    vec2 combined_uv = final_uv_fast+ final_uv_slow;

    float base_voronoi = voronoi_slow(combined_uv - fbm_warp * 2.0 + time_offset);
    float layer_1_voronoi = voronoi_fast(final_uv_slow + fbm_warp * 40.0 + time);
    float layer_2_voronoi = voronoi_fast(final_uv_slow * 4.0- time_offset);
    float layer_3_fbm = fbm(combined_uv - fbm_warp * 20.0 + time_offset);
    float layer_4_voronoi = voronoi_slow(final_uv_fast - fbm_warp * 1.0 + time_offset);
    float layer_5_voronoi = voronoi_slow(final_uv_slow * 5.0 - time);


    vec3 base_layer = mix(color_a, color_b, base_voronoi);
    vec3 layer_1 = mix(color_b, color_a, layer_1_voronoi);
    vec3 layer_2 = mix(color_b, color_a, layer_2_voronoi );
    vec3 layer_3 = mix(color_a, color_b, layer_3_fbm) ;
    vec3 layer_4 = mix(color_b, color_a, layer_4_voronoi);
    vec3 layer_5 = mix(color_b, color_a, layer_5_voronoi); 

    vec3 combined = base_layer;
    combined = linear_dodge(combined, layer_1);
    combined = linear_dodge(combined, layer_2);
    combined = overlay(combined, layer_3);
    combined = soft_light(combined, layer_4);
    combined = soft_light(combined, layer_5);

    float saturation = 0.5;
    float luma = dot(combined, color_a);
    combined = mix(vec3(luma), combined, saturation);
    gl_FragColor = vec4(clamp(combined, 0.0, 1.0), 1.0);
}