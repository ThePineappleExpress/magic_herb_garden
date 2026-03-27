"""lang.py - Language proxy module.

Reads the user's language preference from settings and dynamically loads
the appropriate language module from bin/lang/.  All constants from that
module are re-exported at this module's top level so callers can do:

    import lang
    print(lang.BUTTON_SAVE)

Falls back to English if the preferred language is unavailable.
"""

import importlib
import logging
import sys

LOG = logging.getLogger(__name__)

_DEFAULT_LANG = "english"


def _get_preferred_language() -> str:
    """Read language preference from settings (without importing storage at module level)."""
    try:
        from data import SettingsRepository
        settings = SettingsRepository.get_all()
        return settings.get("language", _DEFAULT_LANG).lower()
    except Exception:
        return _DEFAULT_LANG


def _load_lang_module(name: str):
    """Import and return a language module by name."""
    module_name = f"bin.lang.{name}"
    try:
        return importlib.import_module(module_name)
    except ImportError:
        LOG.warning("Language module '%s' not found, falling back to '%s'", name, _DEFAULT_LANG)
        return importlib.import_module(f"bin.lang.{_DEFAULT_LANG}")


def reload():
    """Reload the language module (e.g. after changing language in settings)."""
    preferred = _get_preferred_language()
    mod = _load_lang_module(preferred)

    # Copy all public attributes from the language module into this module
    this = sys.modules[__name__]
    for attr in dir(mod):
        if not attr.startswith("_"):
            setattr(this, attr, getattr(mod, attr))


# Auto-load on first import
reload()
