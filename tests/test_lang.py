"""Tests for lang.py and bin/lang/ - language loading and proxy."""

from bin.lang import get_available_languages, load_language
import lang as _lang_mod


# ---------------------------------------------------------------------------
# bin/lang/__init__.py
# ---------------------------------------------------------------------------

def test_get_available_languages_returns_list():
    languages = get_available_languages()
    assert isinstance(languages, list)
    assert len(languages) > 0, "Should find at least one language"


def test_get_available_languages_includes_english():
    languages = get_available_languages()
    lower = [l.lower() for l in languages]
    assert "english" in lower, f"Expected 'english' in {languages}"


def test_load_language_english():
    mod = load_language("english")
    assert mod is not None
    # Should have some constants
    assert hasattr(mod, "BUTTON_SAVE") or hasattr(mod, "APP_TITLE") or len(dir(mod)) > 5


def test_load_language_case_insensitive():
    mod = load_language("English")
    assert mod is not None


def test_load_language_invalid_raises():
    try:
        load_language("zzz_nonexistent_lang_zzz")
        assert False, "Should have raised ImportError"
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# lang.py proxy
# ---------------------------------------------------------------------------

def test_lang_module_has_constants():
    """After import, lang module should have re-exported constants."""
    # lang.reload() is called on import, so attributes should exist
    public_attrs = [a for a in dir(_lang_mod) if not a.startswith("_") and a.isupper()]
    assert len(public_attrs) > 10, f"Expected many constants, got {len(public_attrs)}: {public_attrs[:5]}"


def test_lang_constants_are_strings():
    """Most UPPER_CASE constants should be strings (some may be dicts/lists)."""
    public_attrs = [a for a in dir(_lang_mod) if not a.startswith("_") and a.isupper()]
    string_count = 0
    for attr_name in public_attrs:
        val = getattr(_lang_mod, attr_name)
        if isinstance(val, str):
            string_count += 1
    assert string_count > 10, f"Expected many string constants, got {string_count}"


def test_lang_reload():
    """reload() should not raise."""
    _lang_mod.reload()
    # After reload, constants should still exist
    public_attrs = [a for a in dir(_lang_mod) if not a.startswith("_") and a.isupper()]
    assert len(public_attrs) > 10
