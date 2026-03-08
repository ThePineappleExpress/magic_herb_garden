"""Shader loader for Magic Herb Tracker.

Discovers .glsl fragment shaders in bin/shaders/ and loads them by name.
"""

import logging
from pathlib import Path

LOG = logging.getLogger(__name__)

_SHADERS_DIR = Path(__file__).parent


def get_available_shaders() -> list[str]:
    """Return sorted list of available shader names (stem form, e.g. 'smoke')."""
    return sorted(p.stem for p in _SHADERS_DIR.glob("*.glsl"))


def load_shader(name: str) -> str | None:
    """Load and return GLSL source code for a shader by name.

    Returns None if the shader file is not found.
    """
    path = _SHADERS_DIR / f"{name.lower()}.glsl"
    if not path.exists():
        LOG.warning("Shader file not found: %s", path)
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        LOG.exception("Failed to read shader from %s", path)
        return None
