"""Shader loader for Magic Herb Tracker.

Discovers .glsl fragment shaders in bin/shaders/ and usr/shaders/.
User shaders in usr/shaders/ override built-in shaders with the same name.
"""

import logging
from pathlib import Path

LOG = logging.getLogger(__name__)

_BUILTIN_DIR = Path(__file__).parent
_PROJECT_DIR = _BUILTIN_DIR.parent.parent          # repo root
_USER_DIR = _PROJECT_DIR / "usr" / "shaders"        # user-added shaders


def _search_dirs() -> list[Path]:
    """Return shader directories in priority order (user overrides builtin)."""
    return [d for d in (_USER_DIR, _BUILTIN_DIR) if d.is_dir()]


def get_available_shaders() -> list[str]:
    """Return sorted list of available shader names (stem form, e.g. 'smoke')."""
    shaders: dict[str, Path] = {}
    for d in reversed(_search_dirs()):      # builtin first, user overrides
        for p in d.glob("*.glsl"):
            shaders[p.stem] = p
    return sorted(shaders.keys())


def get_default_shader() -> str | None:
    """Return the name of the first available shader, or None."""
    available = get_available_shaders()
    return available[0] if available else None


def load_shader(name: str) -> str | None:
    """Load and return GLSL source code for a shader by name.

    Searches usr/shaders/ first, then bin/shaders/.
    Returns None if the shader file is not found.
    """
    name_lower = name.lower()
    for d in _search_dirs():
        path = d / f"{name_lower}.glsl"
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                LOG.exception("Failed to read shader from %s", path)
                return None
    LOG.warning("Shader '%s' not found in any search directory", name)
    return None
