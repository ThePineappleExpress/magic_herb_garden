"""Language loader for Magic Herb Tracker.

Discovers available language modules in this directory and loads them by name.
"""

import importlib
from pathlib import Path

_LANG_DIR = Path(__file__).parent


def get_available_languages() -> list[str]:
    """Return sorted list of available language names (capitalized)."""
    names = []
    for p in sorted(_LANG_DIR.glob("*.py")):
        if p.name.startswith("_"):
            continue
        names.append(p.stem.capitalize())
    return names


def load_language(name: str):
    """Load and return a language module by name (case-insensitive)."""
    module_name = f"bin.lang.{name.lower()}"
    return importlib.import_module(module_name)
