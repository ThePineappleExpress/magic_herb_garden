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
    return base / (1.0 - min(blend, 0.999));
}

vec3 overlay(vec3 base, vec3 blend) {
    return mix(
        2.0 * base * blend,
        1.0 - 2.0 * (1.0 - base) * (1.0 - blend),
        step(0.5, base)
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
                
mat2 rotate2D(float r) {
    return mat2(cos(r), sin(r), -sin(r), cos(r));
}
// Pseudo-random number generator
float rand(vec2 co){
    return fract(sin(dot(co.xy,vec2(11.1234,31.420))) * 1175.4846);
}

// Hash function for Voronoi
vec2 hash(vec2 seed) {
    seed = vec2(dot(seed, vec2(127.1, 311.7)), dot(seed, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(seed) * 43758.5453123);
}

// 2D noise
float noise(vec2 pos){
    vec2 grid_cell = floor(pos);
    vec2 frac_pos = fract(pos);
    float corner_bl = rand(grid_cell);
    float corner_br = rand(grid_cell + vec2(1.0, 0.0));
    float corner_tl = rand(grid_cell + vec2(0.0, 1.0));
    float corner_tr = rand(grid_cell + vec2(1.0, 1.0));
    vec2 smooth_step = frac_pos * frac_pos * (3.0 - 2.0 * frac_pos);
    return mix(corner_bl, corner_br, smooth_step.x) + (corner_tl - corner_bl) * smooth_step.y * (1.0 - smooth_step.x) + (corner_tr - corner_br) * smooth_step.x * smooth_step.y;
}

//fbm
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


void main(void) {
    vec2 pixCoord = floor(gl_FragCoord.xy / pixel_scale) * pixel_scale + pixel_scale * 0.5;

    vec2 uv = (pixCoord - 0.5 * resolution.xy) / resolution.y;

    float noise_value = 0.0;
    float time_offset = time * 0.2;

    vec2 fbm_warp = vec2(
        fbm(uv * 3.0 + time_offset),
        fbm(uv * 3.0 - time_offset)
    );

    vec2 wave_offset;
    wave_offset.x = sin(uv.y * 10.0 + time_offset) * 0.15;
    wave_offset.y = cos(uv.x * 10.0 - time_offset) * 0.15;

    vec2 swirls = (1.0 * pixCoord + resolution.xy) / min(resolution.x, resolution.y) * 0.5;
	for(int i = 1; i < 5; i++) {
		swirls += sin(swirls.yx * vec2(1.6, 1.1) * float(i + 11) - time * float(i) * vec2(3.4, 0.5) / 10.0) * 0.1;
	}
	float smoke_distortion = (abs(sin(swirls.y + time * 0.0) + sin(swirls.x + time * 0.0))) * 0.5;
    
    vec2 n = vec2(0);
    vec2 q = vec2(0);
    float d = dot(uv, uv);
    float S = 12.0;
    float a = 0.2;
    mat2 m = rotate2D(5.);
                
    for (float j = 0.; j < 20.; j++) {
        uv *= m;
        n *= m;
        q = uv * S + time + d + j + n;
        a += dot(cos(q) / S, vec2(0.2));
        n -= sin(q);
        S *= 1.2;
    }
        // use the distorted coordinates
    vec2 distorted_uv = uv * (a + 0.2) + a + a - d + wave_offset + fbm_warp + smoke_distortion ;
    
    vec3 base_noise = mix(vec3(0.0), color_b, fbm(distorted_uv * 4.0 + time_offset * 0.1));
    float detail_noise = noise(distorted_uv * 2.4 + time_offset * 0.5);
    float wisps_noise = fbm(distorted_uv * 2.8 - time_offset * 0.8);
    float wisps2_noise = fbm(distorted_uv * 4.2 - time_offset);

    

    vec3 base_layer = mix(color_a, color_b, (base_noise * (a + 0.2) + a + a - d));
    vec3 detail_layer = mix(color_b, color_a, detail_noise * (a + 0.2) + a + a - d);
    vec3 wisps_layer = mix(color_a, color_b, wisps_noise * (a + 0.2) + a + a - d) * 1.5 ;
    vec3 wisps2_layer = mix(color_a, color_b, wisps2_noise);

    vec3 combined = base_layer;
    combined = screen(combined, detail_layer);
    combined = overlay(combined, wisps_layer);
    combined = soft_light(combined, wisps2_layer);

    gl_FragColor = vec4(combined, 1.0);
}
