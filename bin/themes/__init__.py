"""Theme loader for Magic Herb Tracker.

Discovers .toml theme files in bin/themes/, usr/themes/, and the
platformdirs user-data themes directory.  User themes override
built-in themes with the same name.
"""

import tomllib
import logging
from pathlib import Path

try:
    from platformdirs import user_data_dir
    _PLATFORM_DIR = Path(user_data_dir("MagicHerbTracker", "")) / "themes"
except Exception:
    _PLATFORM_DIR = None

LOG = logging.getLogger(__name__)

_BUILTIN_DIR = Path(__file__).parent
_PROJECT_DIR = _BUILTIN_DIR.parent.parent          # repo root
_LOCAL_USER_DIR = _PROJECT_DIR / "usr" / "themes"   # project-local overrides


def _search_dirs() -> list[Path]:
    """Return theme directories in priority order (highest priority first)."""
    dirs: list[Path] = []
    if _PLATFORM_DIR is not None and _PLATFORM_DIR.is_dir():
        dirs.append(_PLATFORM_DIR)
    if _LOCAL_USER_DIR.is_dir():
        dirs.append(_LOCAL_USER_DIR)
    dirs.append(_BUILTIN_DIR)
    return dirs


def get_available_themes() -> list[str]:
    """Return sorted list of available theme names (stem form, e.g. 'dark')."""
    themes: dict[str, Path] = {}
    for d in reversed(_search_dirs()):       # builtin first, user overrides
        if not d.is_dir():
            continue
        for p in d.glob("*.toml"):
            themes[p.stem] = p
    return sorted(themes.keys())


def get_default_theme() -> str:
    """Return the first available theme name, or 'green' as ultimate fallback."""
    available = get_available_themes()
    return available[0] if available else "green"


def _resolve_theme_path(name: str) -> Path | None:
    """Find the TOML file for a theme name.  Higher-priority dirs win."""
    name_lower = name.lower().replace(" ", "_")
    for d in _search_dirs():
        path = d / f"{name_lower}.toml"
        if path.exists():
            return path
    return None


def load_theme(name: str) -> dict:
    """Load and return a theme dict from a TOML file by name.

    Falls back to the first available theme if the requested one is
    not found.  Returns an empty dict as last resort.
    """
    path = _resolve_theme_path(name)
    if path is None:
        fallback = get_default_theme()
        if fallback != name:
            LOG.warning("Theme '%s' not found, falling back to '%s'", name, fallback)
            path = _resolve_theme_path(fallback)
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
