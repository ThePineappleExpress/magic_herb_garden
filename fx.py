import logging
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Rectangle, Callback
from kivy.clock import Clock
from kivy.properties import StringProperty

from bin.shaders import load_shader, get_default_shader

LOG = logging.getLogger(__name__)

# Discover the first available shader at import time (no hardcoded name).
_DEFAULT_SHADER = get_default_shader()
_DEFAULT_FS = load_shader(_DEFAULT_SHADER) if _DEFAULT_SHADER else ""


class ShaderWidget(Widget):
    """Full-screen fragment-shader background widget.

    ``shader_name``  – which .glsl to load (discovered dynamically).
    ``color_a`` / ``color_b`` – RGB lists pushed as uniforms.
    The ``fs`` StringProperty can also be set directly with raw GLSL source.
    """

    fs = StringProperty(_DEFAULT_FS)

    def __init__(
        self,
        shader_name: str | None = None,
        color_a: list | None = None,
        color_b: list | None = None,
        **kwargs,
    ):
        self.canvas = RenderContext()
        self._shader_name = shader_name or _DEFAULT_SHADER or ""
        super().__init__(**kwargs)

        # Load the requested shader source
        if self._shader_name and self._shader_name != _DEFAULT_SHADER:
            source = load_shader(self._shader_name)
            if source:
                self.fs = source
            else:
                LOG.warning(
                    "Shader '%s' not found, using default '%s'",
                    self._shader_name, _DEFAULT_SHADER,
                )
                self._shader_name = _DEFAULT_SHADER or ""

        with self.canvas:
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.canvas.shader.fs = self.fs

        # Uniforms - caller supplies colors from the active theme
        self.canvas['time'] = 0.0
        self.canvas['resolution'] = list(map(float, self.size))
        self.canvas['color_a'] = list(map(float, color_a or [0.12, 0.172, 0.153]))
        self.canvas['color_b'] = list(map(float, color_b or [0.22, 0.272, 0.253]))
        self.canvas['pixel_scale'] = 1.0

        self.bind(size=self._update_rect, pos=self._update_rect)
        self._clock_event = None  # created by start_clock()

    # -- public API ----------------------------------------------------------

    def start_clock(self):
        """Begin ticking the time uniform at 60 fps."""
        if self._clock_event is None:
            self._clock_event = Clock.schedule_interval(self.update_glsl, 1 / 60.0)

    def stop_clock(self):
        """Pause the time uniform ticker (saves CPU when off-screen)."""
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None

    def update_colors(self, color_a: list, color_b: list) -> None:
        """Push new theme colours to the running shader."""
        self.canvas['color_a'] = list(map(float, color_a))
        self.canvas['color_b'] = list(map(float, color_b))

    def set_shader(self, name: str, color_a: list | None = None, color_b: list | None = None) -> bool:
        """Load a shader by name and apply it.  Optionally update colors.

        Returns True on success.
        """
        source = load_shader(name)
        if source is None:
            LOG.warning("Cannot set shader '%s' - file not found", name)
            return False
        self._shader_name = name
        if color_a is not None and color_b is not None:
            self.update_colors(color_a, color_b)
        self.fs = source
        return True

    # -- internals -----------------------------------------------------------

    def on_fs(self, instance, value):
        """When the fs StringProperty changes, push it to the GPU."""
        self.canvas.shader.fs = value

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
        self.canvas['resolution'] = list(map(float, self.size))

    def update_glsl(self, dt):
        self.canvas['time'] = self.canvas['time'] + dt


# Backward-compat alias
SmokeShaderWidget = ShaderWidget