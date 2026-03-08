#ifdef GL_ES
precision mediump float;
#endif

uniform float time;
uniform vec2 resolution;
uniform vec3 color_a;
uniform vec3 color_b;
uniform float pixel_scale;

// Hand-drawn bezier leaf - 64 arc-length-resampled points
#define LEAF_N 85

vec2 get_leaf_pt(int i) {
    if (i == 0) return vec2(0.49743, 1.00000);
    if (i == 1) return vec2(0.43958, 0.85774);
    if (i == 2) return vec2(0.41327, 0.70727);
    if (i == 3) return vec2(0.41486, 0.55395);
    if (i == 4) return vec2(0.43235, 0.41860);
    if (i == 5) return vec2(0.45598, 0.31945);
    if (i == 6) return vec2(0.48907, 0.21272);
    if (i == 7) return vec2(0.44698, 0.30211);
    if (i == 8) return vec2(0.39520, 0.39002);
    if (i == 9) return vec2(0.33422, 0.47228);
    if (i == 10) return vec2(0.26504, 0.54712);
    if (i == 11) return vec2(0.18853, 0.61497);
    if (i == 12) return vec2(0.04038, 0.69971);
    if (i == 13) return vec2(0.11649, 0.53476);
    if (i == 14) return vec2(0.18863, 0.43976);
    if (i == 15) return vec2(0.27438, 0.35718);
    if (i == 16) return vec2(0.36687, 0.28194);
    if (i == 17) return vec2(0.49055, 0.20004);
    if (i == 18) return vec2(0.36029, 0.26003);
    if (i == 19) return vec2(0.24360, 0.28531);
    if (i == 20) return vec2(0.12422, 0.29039);
    if (i == 21) return vec2(0.00000, 0.26732);
    if (i == 22) return vec2(0.12488, 0.21284);
    if (i == 23) return vec2(0.24104, 0.18521);
    if (i == 24) return vec2(0.36031, 0.17858);
    if (i == 25) return vec2(0.49309, 0.18884);
    if (i == 26) return vec2(0.37358, 0.15493);
    if (i == 27) return vec2(0.28026, 0.11413);
    if (i == 28) return vec2(0.20833, 0.05208);
    if (i == 29) return vec2(0.16558, 0.00000);
    if (i == 30) return vec2(0.21556, 0.01115);
    if (i == 31) return vec2(0.31184, 0.04432);
    if (i == 32) return vec2(0.41194, 0.10855);
    if (i == 33) return vec2(0.49437, 0.17851);
    if (i == 34) return vec2(0.46246, 0.14454);
    if (i == 35) return vec2(0.43511, 0.10166);
    if (i == 36) return vec2(0.43212, 0.05798);
    if (i == 37) return vec2(0.46457, 0.09731);
    if (i == 38) return vec2(0.48490, 0.14367);
    if (i == 39) return vec2(0.49439, 0.16688);
    if (i == 40) return vec2(0.48452, 0.09567);
    if (i == 41) return vec2(0.46513, 0.04954);
    if (i == 42) return vec2(0.46518, 0.03550);
    if (i == 43) return vec2(0.47970, 0.03202);
    if (i == 44) return vec2(0.48979, 0.04345);
    if (i == 45) return vec2(0.50240, 0.09196);
    if (i == 46) return vec2(0.50685, 0.16530);
    if (i == 47) return vec2(0.51465, 0.12435);
    if (i == 48) return vec2(0.54178, 0.08245);
    if (i == 49) return vec2(0.56975, 0.06288);
    if (i == 50) return vec2(0.56324, 0.09218);
    if (i == 51) return vec2(0.54017, 0.13760);
    if (i == 52) return vec2(0.50837, 0.17859);
    if (i == 53) return vec2(0.58771, 0.09675);
    if (i == 54) return vec2(0.69293, 0.04152);
    if (i == 55) return vec2(0.77566, 0.02215);
    if (i == 56) return vec2(0.82135, 0.01656);
    if (i == 57) return vec2(0.78568, 0.05329);
    if (i == 58) return vec2(0.71971, 0.10686);
    if (i == 59) return vec2(0.62861, 0.15273);
    if (i == 60) return vec2(0.50781, 0.19097);
    if (i == 61) return vec2(0.65244, 0.16868);
    if (i == 62) return vec2(0.76997, 0.16580);
    if (i == 63) return vec2(0.88923, 0.18566);
    if (i == 64) return vec2(1.00000, 0.23044);
    if (i == 65) return vec2(0.88491, 0.25592);
    if (i == 66) return vec2(0.76623, 0.26833);
    if (i == 67) return vec2(0.64799, 0.25413);
    if (i == 68) return vec2(0.50950, 0.19998);
    if (i == 69) return vec2(0.64224, 0.28802);
    if (i == 70) return vec2(0.73850, 0.35859);
    if (i == 71) return vec2(0.82743, 0.43762);
    if (i == 72) return vec2(0.90542, 0.52786);
    if (i == 73) return vec2(0.98038, 0.66190);
    if (i == 74) return vec2(0.84053, 0.60094);
    if (i == 75) return vec2(0.74700, 0.54153);
    if (i == 76) return vec2(0.67246, 0.47231);
    if (i == 77) return vec2(0.60660, 0.39391);
    if (i == 78) return vec2(0.55557, 0.30524);
    if (i == 79) return vec2(0.50868, 0.20920);
    if (i == 80) return vec2(0.53843, 0.31283);
    if (i == 81) return vec2(0.56348, 0.41587);
    if (i == 82) return vec2(0.58106, 0.55297);
    if (i == 83) return vec2(0.58293, 0.70614);
    if (i == 84) return vec2(0.55061, 0.85593);
    return vec2(0.49743, 1.00000); // fallback
}
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

float rand(vec2 seed) {
    return fract(sin(dot(seed, vec2(127.1, 311.7))) * 43758.5453);
}

float seg_dist(vec2 point, vec2 seg_start, vec2 seg_end) {
    vec2 seg_vec = seg_end - seg_start;
    float proj_t = clamp(dot(point - seg_start, seg_vec) / dot(seg_vec, seg_vec), 0.0, 1.0);
    return length(point - seg_start - seg_vec * proj_t);
}


mat2 rot2(float angle) {
    float cos_a = cos(angle), sin_a = sin(angle);
    return mat2(cos_a, -sin_a, sin_a, cos_a);
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
        frequency /= 2.0;
        amplitude *= 0.6;
    }
    return noise_value;
}

float leaf_sdf(vec2 point) {
    float min_dist = 1.0e6;
    float winding = 0.0;
    for (int i = 0; i < LEAF_N; i++) {
        int prev_i = (i == 0) ? (LEAF_N - 1) : (i - 1);
        vec2 pt_prev = get_leaf_pt(prev_i);
        vec2 pt_curr = get_leaf_pt(i);
        min_dist = min(min_dist, seg_dist(point, pt_prev, pt_curr));
        if (pt_prev.y <= point.y) {
            if (pt_curr.y > point.y) {
                float cross_val = (pt_curr.x - pt_prev.x) * (point.y - pt_prev.y)
                                - (pt_curr.y - pt_prev.y) * (point.x - pt_prev.x);
                if (cross_val > 0.0) winding += 1.0;
            }
        } else {
            if (pt_curr.y <= point.y) {
                float cross_val = (pt_curr.x - pt_prev.x) * (point.y - pt_prev.y)
                                - (pt_curr.y - pt_prev.y) * (point.x - pt_prev.x);
                if (cross_val < 0.0) winding -= 1.0;
            }
        }
    }
    bool is_inside = (abs(winding) > 0.5);
    return is_inside ? -min_dist : min_dist;
}

const int N_DROPS = 12;

void main(void) {
    vec2 pixCoord = floor(gl_FragCoord.xy / pixel_scale) * pixel_scale + pixel_scale * 0.5;
    vec2 uv = pixCoord / resolution.xy;
    float time_offset = time * 0.1;

    vec3 background = color_b;
    float accumulated_alpha = 0.0;
    vec3 accumulated_color = vec3(0.0);

    vec2 fbm_warp = vec2(
        fbm(uv * 1.0 + time_offset),
        fbm(uv * 1.0 - time_offset)
    ) * 0.1;

    vec2 wave_offset;
    wave_offset.x = sin(fbm_warp.y + time_offset);
    wave_offset.y = cos(fbm_warp.x - time_offset);

    vec2 uv_offset = uv + fbm_warp + wave_offset + time_offset;

    float fbm_noise = fbm(uv_offset + time_offset * 0.1);
    vec3 fbm_overlay = mix(vec3(0.0), color_b, fbm_noise * 1.1);

    for (int drop_idx = 0; drop_idx < N_DROPS; drop_idx++) {
        float drop_f = float(drop_idx);

        float lane_center_x = rand(vec2(drop_f, 77.0));

        float fall_speed = 0.01 + rand(vec2(drop_f, 2.0)) * 0.11;
        float start_phase = rand(vec2(drop_f, 12.0));
        float leaf_scale = 0.3 + rand(vec2(drop_f, 10.0)) * 0.1;
        float lean_angle = (rand(vec2(drop_f, 45.0)) - 0.5) * 1.2;
        float sway_amplitude = (rand(vec2(drop_f, 180.0)) - 0.5) * 0.4; 
        float sway_speed = 0.03 + rand(vec2(drop_f, 0.02)) * 0.5;
        float brightness = 0.1 + rand(vec2(drop_f, 0.1)) * 0.65;
        

        float leaf_center_y = mod(start_phase - fall_speed * (time_offset * 5.0), 1.4);
        if (abs(uv.y - leaf_center_y) > leaf_scale * 1.0) continue;
        vec2 leaf_center = vec2(lane_center_x, leaf_center_y);
        float rotation = lean_angle + sway_amplitude * sin(time * sway_speed + start_phase * 6.2831);

        vec2 leaf_local_uv = uv - leaf_center;
        leaf_local_uv.x *= resolution.x / resolution.y;
        leaf_local_uv = rot2(-rotation) * leaf_local_uv;
        leaf_local_uv.x /= (resolution.x / resolution.y);
        leaf_local_uv = leaf_local_uv / leaf_scale + vec2(0.5, 0.5) + fbm_warp;

        float signed_dist = leaf_sdf(leaf_local_uv);
        float leaf_opacity = (1.0 - smoothstep(-0.005, 0.0, signed_dist)) * brightness;
        float fade_margin = leaf_scale * 1.0;
        float fade_enter = smoothstep(0.0, 1.0 - fade_margin, leaf_center_y);
        float fade_exit = smoothstep(0.0, fade_margin, leaf_center_y);
        leaf_opacity *= fade_enter * fade_exit;

        float blend_weight = leaf_opacity * (1.0 - accumulated_alpha);
        accumulated_color += (color_a - fbm_overlay ) * blend_weight * rand(vec2(0.0, 1.0));
        accumulated_alpha = clamp(accumulated_alpha + blend_weight, 0.0, 1.0);
    }

    vec3 leafs_layer = mix(fbm_overlay, accumulated_color / max(accumulated_alpha, 0.1), accumulated_alpha);
    
    vec3 combined = leafs_layer;
    combined = overlay(combined, mix(color_a, color_b, fbm_overlay));
    gl_FragColor = vec4(clamp(combined, 0.0, 1.0), 1.0);
}
