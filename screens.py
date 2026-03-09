import logging
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
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


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self._shader_widget = None

        shader_enabled, shader_name, color_a, color_b = _load_shader_prefs()

        if shader_enabled:
            self._shader_widget = ShaderWidget(
                shader_name=shader_name,
                color_a=color_a,
                color_b=color_b,
                size_hint=(1, 1),
                pos_hint={'x': -0.5, 'y': -0.5},
            )
            self.layout.add_widget(self._shader_widget)

        self.add_widget(self.layout)

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

    def toggle_shader(self, enabled: bool, shader_name: str | None = None,
                      color_a: list | None = None, color_b: list | None = None):
        """Enable or disable the shader background."""
        if enabled and self._shader_widget is None:
            # If caller didn't supply details, read from settings/theme
            if shader_name is None or color_a is None or color_b is None:
                _, sn, ca, cb = _load_shader_prefs()
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