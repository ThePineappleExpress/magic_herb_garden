"""Theme loader for Magic Herb Tracker.

Discovers .toml theme files in bin/themes/ and usr/themes/.
User themes override built-in themes with the same name.
"""

import tomllib
import logging
from pathlib import Path

from platformdirs import user_data_dir

LOG = logging.getLogger(__name__)

_BUILTIN_DIR = Path(__file__).parent
# User themes live alongside user data, outside the app bundle.
_USER_DIR = Path(user_data_dir("MagicHerbTracker", "")) / "themes"


def get_available_themes() -> list[str]:
    """Return sorted list of available theme names (stem form, e.g. 'forest_dark')."""
    themes = {}
    for d in (_BUILTIN_DIR, _USER_DIR):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.toml")):
            themes[p.stem] = p
    return sorted(themes.keys())


def _resolve_theme_path(name: str) -> Path | None:
    """Find the TOML file for a theme name. User dir takes priority."""
    name_lower = name.lower().replace(" ", "_")
    user_path = _USER_DIR / f"{name_lower}.toml"
    if user_path.exists():
        return user_path
    builtin_path = _BUILTIN_DIR / f"{name_lower}.toml"
    if builtin_path.exists():
        return builtin_path
    return None


def load_theme(name: str) -> dict:
    """Load and return a theme dict from a TOML file by name.

    Falls back to 'forest_dark' if the requested theme is not found.
    Returns an empty dict as last resort.
    """
    path = _resolve_theme_path(name)
    if path is None and name != "forest_dark":
        LOG.warning("Theme '%s' not found, falling back to forest_dark", name)
        path = _resolve_theme_path("forest_dark")
    if path is None:
        LOG.error("No theme files found")
        return {}
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        LOG.exception("Failed to load theme from %s", path)
        return {}


def apply_theme(theme_widget, theme_data: dict) -> None:
    """Apply parsed TOML theme data to a Kivy Theme widget via setattr.

    Iterates all sections except [meta] and [shader_colors], setting
    each key as an attribute on the widget.
    """
    skip_sections = {"meta", "shader_colors"}
    for section, values in theme_data.items():
        if section in skip_sections:
            continue
        if not isinstance(values, dict):
            continue
        for key, value in values.items():
            try:
                setattr(theme_widget, key, value)
            except Exception:
                LOG.warning("Failed to set theme property %s.%s", section, key)


def get_shader_colors(theme_data: dict, shader_name: str | None = None) -> tuple[list, list]:
    """Extract shader color_a and color_b from theme data.

    Checks for per-shader override first, then falls back to defaults.
    Returns (color_a, color_b) as 3-element RGB lists.
    """
    sc = theme_data.get("shader_colors", {})
    defaults = (
        sc.get("color_a", [0.12, 0.172, 0.153]),
        sc.get("color_b", [0.22, 0.272, 0.253]),
    )
    if shader_name and isinstance(sc.get(shader_name), dict):
        override = sc[shader_name]
        return (
            override.get("color_a", defaults[0]),
            override.get("color_b", defaults[1]),
        )
    return defaults
