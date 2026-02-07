from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Rectangle, Callback
from kivy.clock import Clock
from kivy.properties import StringProperty

class SmokeShaderWidget(Widget):
    fs = StringProperty('''
    #ifdef GL_ES
    precision mediump float;
    #endif

    uniform float time;
    uniform vec2 resolution;
    // Screen
    vec3 screen(vec3 base, vec3 blend) {
        return 1.0 - (1.0 - base) * (1.0 - blend);
    }                        
    // Color Dodge
    vec3 colorDodge(vec3 base, vec3 blend) {
        return base / (1.0 - min(blend, 0.999));
    }    
    // Pseudo-random number generator
    float rand(vec2 co){
        return fract(sin(dot(co.xy,vec2(11.1234,31.420))) * 1175.4846);
    }
    // 2D noise
    float noise(vec2 p){
        vec2 i = floor(p);
        vec2 f = fract(p);
        float a = rand(i);
        float b = rand(i + vec2(1.0, 0.0));
        float c = rand(i + vec2(0.0, 1.0));
        float d = rand(i + vec2(1.0, 1.0));
        vec2 u = f*f*(3.0-2.0*f);
        return mix(a, b, u.x) +
               (c - a)* u.y * (1.0 - u.x) +
               (d - b) * u.x * u.y;
    }
    //fbm
    float fbm(vec2 p) {
        float value = 0.0;
        float amplitude = 0.5;
        float frequency = 1.0;
        for (int i = 0; i < 5; i++) {
            value += amplitude * noise(p * frequency);
            frequency *= 2.0;
            amplitude *= 0.5;
        }
        return value;
    }
    float fbm2(vec2 p) {
        float value = 0.0;
        float amplitude = 0.5;
        float frequency = 1.0;
        for (int i = 0; i < 5; i++) {
            value += amplitude * noise(p * frequency);
            frequency *= rand(vec2(2.0, 5.0));
            amplitude *= rand(vec2(0.2, 0.7));
        }
        return value;
    }
    void main(void) {
        vec2 uv = gl_FragCoord.xy / resolution.xy;
        float n = 0.0;
        float t = time * 0.05;
                        
        // make a wavy offset
        vec2 offset;
        offset.x = sin(uv.y * 10.0 + t) * 0.02;
        offset.y = cos(uv.x * 10.0 - t) * 0.02;

        // use the distorted coordinates
        vec2 distortedUV = uv + offset;
        float baseN   = fbm(distortedUV * 0.2 + t);
        float detailN = noise(distortedUV * 0.4 + t * 0.5);
        float wispsN  = fbm(distortedUV * 0.8 - t * 0.8);
        float wisps2N  = fbm(distortedUV * 1.6 - t);
                        
        float baseAlpha   = 1.0;
        float detailAlpha = 1.0;
        float wispsAlpha  = 1.0;
        float wisps2Alpha  = 1.0;

        vec3 baseColor   = vec3(0.12, 0.172, 0.153); 
        vec3 detailColor = vec3(0.2, 0.5, 0.3);   
        vec3 wispsColor  = vec3(0.92, 0.972, 0.953);   
        vec3 wisps2Color  = vec3(0.12, 0.172, 0.153);   

        vec3 base   = baseColor   * (baseN   * baseAlpha);
        vec3 detail = detailColor * (detailN * detailAlpha);
        vec3 wisps  = wispsColor  * (wispsN  * wispsAlpha);
        vec3 wisps2  = wisps2Color  * (wisps2N  * wisps2Alpha);
        vec3 combined = base;
        combined = colorDodge(combined, detail);
        combined = colorDodge(combined, wisps);
        combined = colorDodge(combined, wisps2);

    
        gl_FragColor = vec4(combined, 1.0);
    }
    ''')

    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        super().__init__(**kwargs)
        with self.canvas:
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # Set the shader code directly
        self.canvas.shader.fs = self.fs
        self.canvas['time'] = 0.0
        self.canvas['resolution'] = list(map(float, self.size))
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.bind(size=self._update_uniforms, pos=self._update_uniforms)
        Clock.schedule_interval(self.update_glsl, 1/60.)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def _update_uniforms(self, *args):
        self.canvas['resolution'] = list(map(float, self.size))

    def update_glsl(self, dt):
        self.canvas['time'] = self.canvas['time'] + dt

    def on_fs(self, instance, value):
        self.canvas.shader.fs = value

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
        self.canvas['resolution'] = list(map(float, self.size))

    def update_glsl(self, dt):
        self.canvas['time'] = self.canvas['time'] + dt

    def on_fs(self, instance, value):
        self.canvas['fragment_shader'] = value