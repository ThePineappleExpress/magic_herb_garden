from datetime import datetime, date
from helpers import get_difference_days, _coerce_to_date, parse_ts_to_datetime, rgba_to_hex


# ---------------------------------------------------------------------------
# _coerce_to_date
# ---------------------------------------------------------------------------

def test_coerce_iso_string():
    d = _coerce_to_date("2025-01-02")
    assert isinstance(d, date) and d.year == 2025 and d.day == 2


def test_coerce_datetime():
    dt = datetime(2025, 5, 6, 12, 0)
    assert _coerce_to_date(dt) == date(2025, 5, 6)


def test_coerce_date_passthrough():
    d = date(2025, 3, 15)
    assert _coerce_to_date(d) == d


def test_coerce_none():
    assert _coerce_to_date(None) is None


def test_coerce_empty_string():
    assert _coerce_to_date("") is None


def test_coerce_whitespace_string():
    assert _coerce_to_date("   ") is None


def test_coerce_iso_with_time():
    d = _coerce_to_date("2025-06-15T10:30:00")
    assert d == date(2025, 6, 15)


def test_coerce_iso_with_z():
    d = _coerce_to_date("2025-06-15T10:30:00Z")
    assert d == date(2025, 6, 15)


def test_coerce_non_string_non_date():
    assert _coerce_to_date(12345) is None


# ---------------------------------------------------------------------------
# get_difference_days
# ---------------------------------------------------------------------------

def test_get_difference_days():
    d1 = "2025-01-10"
    d2 = "2025-01-01"
    assert get_difference_days(d1, d2) == 9


def test_get_difference_invalid():
    assert get_difference_days(None, "2025-01-01") is None


def test_get_difference_negative():
    assert get_difference_days("2025-01-01", "2025-01-10") == -9


def test_get_difference_same_day():
    assert get_difference_days("2025-05-05", "2025-05-05") == 0


def test_get_difference_both_none():
    assert get_difference_days(None, None) is None


# ---------------------------------------------------------------------------
# parse_ts_to_datetime
# ---------------------------------------------------------------------------

def test_parse_ts_iso_string():
    result = parse_ts_to_datetime("2025-06-15T10:30:00")
    assert isinstance(result, datetime)
    assert result.year == 2025 and result.month == 6 and result.day == 15
    assert result.hour == 10 and result.minute == 30


def test_parse_ts_with_z_suffix():
    result = parse_ts_to_datetime("2025-01-01T00:00:00Z")
    assert isinstance(result, datetime)
    assert result.year == 2025


def test_parse_ts_none_returns_none():
    assert parse_ts_to_datetime(None) is None


def test_parse_ts_empty_returns_none():
    assert parse_ts_to_datetime("") is None


def test_parse_ts_invalid_returns_none():
    assert parse_ts_to_datetime("not-a-date") is None


def test_parse_ts_date_only():
    result = parse_ts_to_datetime("2025-03-20")
    assert isinstance(result, datetime)
    assert result.year == 2025 and result.month == 3 and result.day == 20


def test_parse_ts_with_timezone():
    result = parse_ts_to_datetime("2025-06-15T10:30:00+02:00")
    assert isinstance(result, datetime)
    assert result.hour == 10


def test_parse_ts_strips_whitespace():
    result = parse_ts_to_datetime("  2025-06-15T10:30:00  ")
    assert isinstance(result, datetime)
    assert result.year == 2025


# ---------------------------------------------------------------------------
# rgba_to_hex
# ---------------------------------------------------------------------------

def test_rgba_to_hex_red():
    assert rgba_to_hex([1, 0, 0, 1]) == "#ff0000"


def test_rgba_to_hex_green():
    assert rgba_to_hex([0, 1, 0, 1]) == "#00ff00"


def test_rgba_to_hex_blue():
    assert rgba_to_hex([0, 0, 1, 1]) == "#0000ff"


def test_rgba_to_hex_white():
    assert rgba_to_hex([1, 1, 1, 1]) == "#ffffff"


def test_rgba_to_hex_black():
    assert rgba_to_hex([0, 0, 0, 1]) == "#000000"


def test_rgba_to_hex_partial_values():
    result = rgba_to_hex([0.5, 0.5, 0.5, 1])
    # 0.5 * 255 = 127.5 → int(127) = 127 → 0x7f
    assert result == "#7f7f7f"


def test_rgba_to_hex_ignores_alpha():
    # Alpha channel should not appear in output (6-char hex, not 8)
    result = rgba_to_hex([1, 0, 0, 0.5])
    assert result == "#ff0000"
    assert len(result) == 7  # "#" + 6 hex chars
