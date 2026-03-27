"""test_shader_loader.py - unit tests for bin/shaders shader loading."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bin.shaders import load_shader, get_available_shaders


def test_get_available_shaders_includes_smoke():
    shaders = get_available_shaders()
    assert "smoke" in shaders, f"Expected 'smoke' in {shaders}"


def test_load_shader_smoke():
    source = load_shader("smoke")
    assert source is not None, "smoke.glsl should load"
    assert "void main" in source, "Shader should contain main function"
    assert "uniform vec3 color_a" in source, "Shader should declare color_a uniform"
    assert "uniform vec3 color_b" in source, "Shader should declare color_b uniform"


def test_load_shader_missing_returns_none():
    source = load_shader("nonexistent_shader_xyz")
    assert source is None


def test_load_shader_smoke_has_no_hardcoded_colors():
    source = load_shader("smoke")
    assert "vec3(0.12" not in source, "Shader should use color_a uniform, not hardcoded vec3"
    assert "vec3(0.22" not in source, "Shader should use color_b uniform, not hardcoded vec3"
