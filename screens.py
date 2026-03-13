import logging
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from fx import ShaderWidget

LOG = logging.getLogger(__name__)


def _load_shader_prefs() -> tuple[bool, str, list, list]:
    """Return (enabled, shader_name, color_a, color_b) from saved settings + theme."""
    try:
        import storage
        settings = storage.load_settings()
    except Exception:
        settings = {}

    from bin.shaders import get_default_shader
    from bin.themes import load_theme, get_shader_colors, get_default_theme

    shader_enabled = settings.get("shader_enabled", True)
    shader_name = settings.get("shader") or get_default_shader() or ""
    theme_name = settings.get("theme") or get_default_theme()
    theme_data = load_theme(theme_name)
    color_a, color_b = get_shader_colors(theme_data, shader_name)
    return shader_enabled, shader_name, color_a, color_b


# Module-level cache — computed once, shared by all screens
_SHADER_PREFS_CACHE: tuple | None = None


def _get_shader_prefs() -> tuple[bool, str, list, list]:
    global _SHADER_PREFS_CACHE
    if _SHADER_PREFS_CACHE is None:
        _SHADER_PREFS_CACHE = _load_shader_prefs()
    return _SHADER_PREFS_CACHE


def invalidate_shader_prefs_cache():
    """Call after the user changes shader/theme settings."""
    global _SHADER_PREFS_CACHE
    _SHADER_PREFS_CACHE = None


def _get_screen_bg_color() -> list:
    """Return the current theme's screen background color (RGBA)."""
    from kivy.app import App
    app = App.get_running_app()
    if app and hasattr(app, 'theme') and app.theme:
        return list(app.theme.color_screen_bg)
    return [0.12, 0.172, 0.153, 1]


class _SolidBg(Widget):
    """Full-size widget that draws a single solid-color rectangle."""

    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self._color = bg_color or _get_screen_bg_color()
        with self.canvas:
            self._c_instr = Color(*self._color)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def update_color(self, color: list):
        self._color = color
        self._c_instr.rgba = color


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self._shader_widget = None
        self._solid_bg = None

        shader_enabled, shader_name, color_a, color_b = _get_shader_prefs()

        if shader_enabled:
            self._shader_widget = ShaderWidget(
                shader_name=shader_name,
                color_a=color_a,
                color_b=color_b,
                size_hint=(1, 1),
                pos_hint={'x': -0.5, 'y': -0.5},
            )
            self.layout.add_widget(self._shader_widget)
        else:
            self._solid_bg = _SolidBg(size_hint=(1, 1))
            self.layout.add_widget(self._solid_bg)

        self.add_widget(self.layout)

    def on_enter(self):
        """Start the shader clock when this screen becomes active."""
        if self._shader_widget is not None:
            self._shader_widget.start_clock()

    def on_leave(self):
        """Stop the shader clock when navigating away."""
        if self._shader_widget is not None:
            self._shader_widget.stop_clock()

    def add_content(self, widget):
        """Add your actual content on top of the shader."""
        self.layout.add_widget(widget)

    def set_shader(self, name: str, color_a: list | None = None, color_b: list | None = None) -> bool:
        """Switch the running shader to *name*. Returns True on success."""
        if self._shader_widget is None:
            return False
        return self._shader_widget.set_shader(name, color_a, color_b)

    def update_shader_colors(self, color_a: list, color_b: list) -> None:
        """Push new theme colours to the running shader (e.g. after theme change)."""
        if self._shader_widget is not None:
            self._shader_widget.update_colors(color_a, color_b)
        if self._solid_bg is not None:
            self._solid_bg.update_color(_get_screen_bg_color())

    def toggle_shader(self, enabled: bool, shader_name: str | None = None,
                      color_a: list | None = None, color_b: list | None = None):
        """Enable or disable the shader background."""
        if enabled and self._shader_widget is None:
            # Remove solid fallback if present
            if self._solid_bg is not None:
                self.layout.remove_widget(self._solid_bg)
                self._solid_bg = None
            # If caller didn't supply details, read from settings/theme
            if shader_name is None or color_a is None or color_b is None:
                _, sn, ca, cb = _get_shader_prefs()
                shader_name = shader_name or sn
                color_a = color_a or ca
                color_b = color_b or cb
            self._shader_widget = ShaderWidget(
                shader_name=shader_name,
                color_a=color_a,
                color_b=color_b,
                size_hint=(1, 1),
                pos_hint={'x': -0.5, 'y': -0.5},
            )
            # Insert as first widget so content stays on top
            self.layout.add_widget(self._shader_widget, index=len(self.layout.children))
        elif not enabled and self._shader_widget is not None:
            self.layout.remove_widget(self._shader_widget)
            self._shader_widget = None
            # Add solid themed background
            self._solid_bg = _SolidBg(size_hint=(1, 1))
            self.layout.add_widget(self._solid_bg, index=len(self.layout.children))
        elif not enabled and self._shader_widget is None and self._solid_bg is None:
            # Shader was already off but no fallback existed
            self._solid_bg = _SolidBg(size_hint=(1, 1))
            self.layout.add_widget(self._solid_bg, index=len(self.layout.children))