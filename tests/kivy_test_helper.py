"""Kivy test helper - bootstraps a headless Kivy environment for widget tests.

Must be imported BEFORE any widget modules.  Sets up:
1. Kivy environment variables (suppress console log, disable args parsing)
2. Loads the magicherbtracker.kv so Factory.Theme() is available
3. Provides ``make_fake_app()`` to create a minimal app with a real Theme
"""

import os
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
os.environ.setdefault("KIVY_LOG_LEVEL", "error")

from pathlib import Path

# Ensure Kivy is fully initialised (creates a hidden window on first import)
from kivy.app import App                   # noqa: E402
from kivy.factory import Factory           # noqa: E402
from kivy.lang import Builder              # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_KV_PATH = ROOT / "magicherbtracker.kv"
_KV_LOADED = False


def _ensure_kv():
    """Load the project KV file exactly once so dynamic classes like Theme exist."""
    global _KV_LOADED
    if _KV_LOADED:
        return
    try:
        Factory.Theme
        _KV_LOADED = True
    except Exception:
        Builder.load_file(str(_KV_PATH))
        _KV_LOADED = True


class _FakeApp:
    """Lightweight stand-in for ``App.get_running_app()``."""

    def __init__(self, theme):
        self.theme = theme
        self.lang = None
        self.screen = None
        self.previous_screen = None
        self.current_garden_id = None


def make_fake_app():
    """Create and install a fake running app with a real ``Theme`` widget.

    Returns the fake app object.  After calling this,
    ``App.get_running_app()`` will return the fake.
    """
    _ensure_kv()
    theme = Factory.Theme()
    # Load english as default lang
    try:
        from bin.lang import load_language
        lang_mod = load_language("english")
    except Exception:
        lang_mod = None

    fake = _FakeApp(theme)
    fake.lang = lang_mod
    App.get_running_app = staticmethod(lambda: fake)
    return fake


def teardown_fake_app():
    """Restore ``App.get_running_app`` default (returns None)."""
    App.get_running_app = staticmethod(lambda: None)
