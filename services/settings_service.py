"""settings_service.py - Settings read/write, shader prefs, password checks.

No Kivy imports.
"""

import logging

from data import SettingsRepository

LOG = logging.getLogger(__name__)


def get_settings() -> dict:
    """Return the full settings dict."""
    return SettingsRepository.get_all()


def get_setting(key: str, default=None):
    """Return a single setting value."""
    return SettingsRepository.get(key, default)


def set_setting(key: str, value) -> bool:
    """Persist a single setting key."""
    return SettingsRepository.set(key, value)


def has_password() -> bool:
    """Return True if a password is configured."""
    settings = get_settings()
    pw = settings.get("password")
    return bool(pw)


def get_theme_name() -> str:
    """Return the user's selected theme name, or the default."""
    from bin.themes import get_default_theme
    return SettingsRepository.get("theme") or get_default_theme()


def get_shader_prefs() -> tuple[bool, str, list, list]:
    """Return (enabled, shader_name, color_a, color_b) from settings + theme.

    This is the canonical replacement for ``screens._load_shader_prefs()``.
    """
    settings = get_settings()

    from bin.shaders import get_default_shader
    from bin.themes import load_theme, get_shader_colors, get_default_theme

    shader_enabled = settings.get("shader_enabled", True)
    shader_name = settings.get("shader") or get_default_shader() or ""
    theme_name = settings.get("theme") or get_default_theme()
    theme_data = load_theme(theme_name)
    color_a, color_b = get_shader_colors(theme_data, shader_name)
    return shader_enabled, shader_name, color_a, color_b
