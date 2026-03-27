"""Tests for add_garden._daylight_hours() - astral daylight calculation."""

from datetime import date


def _get_daylight_hours():
    """Import _daylight_hours without triggering Kivy (add_garden imports Kivy)."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parent.parent / "add_garden.py"
    source = src.read_text()
    tree = ast.parse(source)

    lines = source.splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_daylight_hours":
            start = node.lineno - 1
            end = node.end_lineno
            func_source = "".join(lines[start:end])
            # Need logging for the except clause
            ns = {"__builtins__": __builtins__}
            import logging
            ns["logging"] = logging
            ns["LOG"] = logging.getLogger("test_daylight")
            exec(compile(func_source, "<_daylight_hours>", "exec"), ns)
            return ns["_daylight_hours"]
    raise RuntimeError("Could not find _daylight_hours in add_garden.py")


_daylight_hours = _get_daylight_hours()


def test_daylight_summer_solstice_northern():
    """June 21 at ~50°N should have long days (> 14h)."""
    hours = _daylight_hours(50.0, 10.0, "Europe/Berlin", for_date=date(2025, 6, 21))
    assert hours > 14, f"Expected >14h daylight at 50°N in June, got {hours}"
    assert hours < 18, f"Expected <18h daylight at 50°N in June, got {hours}"


def test_daylight_winter_solstice_northern():
    """Dec 21 at ~50°N should have short days (< 9h)."""
    hours = _daylight_hours(50.0, 10.0, "Europe/Berlin", for_date=date(2025, 12, 21))
    assert hours < 9, f"Expected <9h daylight at 50°N in December, got {hours}"
    assert hours > 6, f"Expected >6h daylight at 50°N in December, got {hours}"


def test_daylight_equator_roughly_12h():
    """Equator should have ~12h daylight year-round."""
    hours = _daylight_hours(0.0, 0.0, "UTC", for_date=date(2025, 3, 20))
    assert 11. < hours < 13., f"Expected ~12h at equator, got {hours}"


def test_daylight_equinox():
    """March equinox at any latitude should be close to 12h."""
    hours = _daylight_hours(45.0, 0.0, "UTC", for_date=date(2025, 3, 20))
    assert 11. < hours < 13., f"Expected ~12h at equinox, got {hours}"


def test_daylight_returns_float():
    hours = _daylight_hours(40.0, -74.0, "America/New_York", for_date=date(2025, 6, 1))
    assert isinstance(hours, float), f"Expected float, got {type(hours)}"


def test_daylight_fallback_on_error():
    """Invalid inputs should return the 12.0 fallback."""
    hours = _daylight_hours(None, None, "Invalid/TZ")
    assert hours == 12.0, f"Expected 12.0 fallback, got {hours}"
