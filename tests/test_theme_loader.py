"""test_theme_loader.py - unit tests for bin/themes theme loading."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bin.themes import load_theme, apply_theme, get_shader_colors, get_available_themes


def test_get_available_themes_includes_green():
    themes = get_available_themes()
    assert "green" in themes, f"Expected 'green' in {themes}"


def test_load_theme_green():
    data = load_theme("green")
    assert "colors" in data, "Theme missing [colors] section"
    assert "fonts" in data, "Theme missing [fonts] section"
    assert "shader_colors" in data, "Theme missing [shader_colors] section"


def test_load_theme_missing_falls_back():
    data = load_theme("nonexistent_theme_xyz")
    assert "colors" in data, "Fallback to green should have [colors]"


def test_load_theme_colors_are_lists():
    data = load_theme("green")
    bg = data["colors"]["color_gray"]
    assert isinstance(bg, list), f"Expected list, got {type(bg)}"
    assert len(bg) == 4, f"Expected 4-element RGBA, got {len(bg)}"


def test_apply_theme_sets_attributes():
    class FakeWidget:
        pass

    widget = FakeWidget()
    data = load_theme("green")
    apply_theme(widget, data)
    assert hasattr(widget, "color_gray"), "apply_theme should set color_gray"
    assert hasattr(widget, "font_body"), "apply_theme should set font_body"


def test_apply_theme_skips_meta_and_shader_colors():
    class FakeWidget:
        pass

    widget = FakeWidget()
    data = load_theme("green")
    apply_theme(widget, data)
    assert not hasattr(widget, "name"), "apply_theme should skip [meta] section"
    assert not hasattr(widget, "color_a"), "apply_theme should skip [shader_colors]"


def test_get_shader_colors_defaults():
    data = load_theme("green")
    color_a, color_b = get_shader_colors(data)
    assert isinstance(color_a, list) and len(color_a) == 3
    assert isinstance(color_b, list) and len(color_b) == 3


def test_get_shader_colors_empty_data():
    color_a, color_b = get_shader_colors({})
    assert color_a == [0.12, 0.172, 0.153]
    assert color_b == [0.22, 0.272, 0.253]


def test_get_shader_colors_per_shader_override():
    data = {
        "shader_colors": {
            "color_a": [0.1, 0.1, 0.1],
            "color_b": [0.2, 0.2, 0.2],
            "fire": {
                "color_a": [0.6, 0.1, 0.0],
            }
        }
    }
    color_a, color_b = get_shader_colors(data, "fire")
    assert color_a == [0.6, 0.1, 0.0], "Should use per-shader override for color_a"
    assert color_b == [0.2, 0.2, 0.2], "Should fall back to default for color_b"
