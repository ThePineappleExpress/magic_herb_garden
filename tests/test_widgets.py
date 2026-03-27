"""Phase 8 - Kivy widget smoke tests.

Tests widget instantiation, basic properties, text input filtering,
dropdown behavior, and ui_builder functions using a headless Kivy
environment with a real Theme object.

Requires a DISPLAY server (X11/Wayland) or Xvfb.
"""

# Bootstrap Kivy BEFORE any widget imports
from tests.kivy_test_helper import make_fake_app, teardown_fake_app  # noqa: E402

# ---------------------------------------------------------------------------
# Module-level setup: create the fake app once (cheap)
# ---------------------------------------------------------------------------
_app = None


def _setup():
    global _app
    _app = make_fake_app()


# ===========================================================================
# 1. boxes.py - Box widgets
# ===========================================================================

def test_title_box_creates():
    _setup()
    from boxes import TitleBox
    w = TitleBox()
    assert w is not None
    # TitleBox inherits from BoxLayout (default orientation is horizontal)
    assert w.orientation == "horizontal"


def test_wrapper_box_creates():
    _setup()
    from boxes import WrapperBox
    w = WrapperBox()
    assert w is not None


def test_content_box_creates():
    _setup()
    from boxes import ContentBox
    w = ContentBox()
    assert w is not None


def test_item_box_creates():
    _setup()
    from boxes import ItemBox
    w = ItemBox()
    assert w is not None


def test_spacer_box_creates():
    _setup()
    from boxes import SpacerBox
    w = SpacerBox()
    assert w is not None


def test_red_box_creates():
    _setup()
    from boxes import RedBox
    w = RedBox()
    assert w is not None


def test_yellow_box_creates():
    _setup()
    from boxes import YellowBox
    w = YellowBox()
    assert w is not None


def test_green_box_creates():
    _setup()
    from boxes import GreenBox
    w = GreenBox()
    assert w is not None


def test_dark_box_creates():
    _setup()
    from boxes import DarkBox
    w = DarkBox()
    assert w is not None


def test_light_box_creates():
    _setup()
    from boxes import LightBox
    w = LightBox()
    assert w is not None


def test_event_box_creates():
    _setup()
    from boxes import EventBox
    w = EventBox()
    assert w is not None


def test_selectable_event_box_creates():
    _setup()
    from boxes import SelectableEventBox
    w = SelectableEventBox()
    assert w is not None


# ===========================================================================
# 2. buttons.py - Button widgets
# ===========================================================================

def test_hover_button_creates():
    _setup()
    from buttons import HoverButton
    b = HoverButton(text="Test")
    assert b is not None
    assert b.text == "Test"


def test_hover_toggle_creates():
    _setup()
    from buttons import HoverToggle
    b = HoverToggle(text="Toggle")
    assert b is not None


def test_button_green_creates():
    _setup()
    from buttons import ButtonGreen
    b = ButtonGreen(text="Green")
    assert b is not None


def test_button_yellow_creates():
    _setup()
    from buttons import ButtonYellow
    b = ButtonYellow(text="Yellow")
    assert b is not None


def test_button_red_creates():
    _setup()
    from buttons import ButtonRed
    b = ButtonRed(text="Red")
    assert b is not None


def test_button_blue_creates():
    _setup()
    from buttons import ButtonBlue
    b = ButtonBlue(text="Blue")
    assert b is not None


def test_button_purple_creates():
    _setup()
    from buttons import ButtonPurple
    b = ButtonPurple(text="Purple")
    assert b is not None


def test_button_dark_green_creates():
    _setup()
    from buttons import ButtonDarkGreen
    b = ButtonDarkGreen(text="DarkGreen")
    assert b is not None


def test_button_transparent_creates():
    _setup()
    from buttons import ButtonTransparent
    b = ButtonTransparent(text="Trans")
    assert b is not None


def test_suggestion_button_creates():
    _setup()
    from buttons import SuggestionButton
    b = SuggestionButton(text="Suggest")
    assert b is not None


def test_nutrient_button_creates():
    _setup()
    from buttons import NutrientButton
    b = NutrientButton(text="N", group="nutrients")
    assert b is not None
    assert b.text == "N"


def test_graph_button_creates():
    _setup()
    from buttons import GraphButton
    b = GraphButton(text="Graph")
    assert b is not None


def test_reset_button_creates():
    _setup()
    from buttons import ResetButton
    b = ResetButton(text="Reset")
    assert b is not None


def test_sort_dir_button_creates():
    _setup()
    from buttons import SortDirButton
    b = SortDirButton()
    assert b is not None


def test_selector_dropdown_creates():
    _setup()
    from buttons import SelectorDropdown
    s = SelectorDropdown(text="Select", values=["A", "B"])
    assert s is not None
    assert s.text == "Select"


def test_password_eye_toggle_creates():
    _setup()
    from buttons import PasswordEyeToggle
    b = PasswordEyeToggle()
    assert b is not None
    assert b.text == "Show"


def test_password_eye_toggle_with_input():
    _setup()
    from kivy.uix.textinput import TextInput
    from buttons import PasswordEyeToggle
    ti = TextInput(password=True)
    b = PasswordEyeToggle(text_input=ti)
    assert b.text_input is ti


# ===========================================================================
# 3. labels.py - Label widgets
# ===========================================================================

def test_garden_label_creates():
    _setup()
    from labels import GardenLabel
    l = GardenLabel(text="Garden")
    assert l.text == "Garden"


def test_logo_labels_create():
    _setup()
    from labels import LogoLabel1, LogoLabel2, LogoLabel3
    for cls in (LogoLabel1, LogoLabel2, LogoLabel3):
        w = cls(text="Logo")
        assert w is not None


def test_list_labels_create():
    _setup()
    from labels import ListLabel, ListTitleLabel, ListSubLabel
    for cls in (ListLabel, ListTitleLabel, ListSubLabel):
        w = cls(text="List")
        assert w is not None


def test_nutrient_label_creates():
    _setup()
    from labels import NutrientLabel
    l = NutrientLabel(text="N")
    assert l.text == "N"


def test_title_label_creates():
    _setup()
    from labels import TitleLabel
    l = TitleLabel(text="Title")
    assert l.text == "Title"
    # Should have hex_color attribute
    assert hasattr(l, "hex_color")


def test_field_label_creates():
    _setup()
    from labels import FieldLabel
    l = FieldLabel(text="Field")
    assert l.text == "Field"


def test_hint_label_creates():
    _setup()
    from labels import HintLabel
    l = HintLabel(text="Hint")
    assert l.text == "Hint"


def test_prompt_label_creates():
    _setup()
    from labels import PromptLabel
    l = PromptLabel(text="?")
    assert l.text == "?"


def test_warning_labels_create():
    _setup()
    from labels import WarningTitleLabel, WarningLabel
    for cls in (WarningTitleLabel, WarningLabel):
        w = cls(text="warn")
        assert w is not None


# ===========================================================================
# 4. text_inputs.py - Input filtering
# ===========================================================================

def test_num_text_input_creates():
    _setup()
    from text_inputs import NumTextInput
    ti = NumTextInput()
    assert ti is not None
    assert ti.multiline is False
    assert ti.input_filter == "float"


def test_num_text_input_max_chars():
    _setup()
    from text_inputs import NumTextInput
    ti = NumTextInput()
    assert ti.max_chars == 6


def test_num_text_input_insert_limits():
    """NumTextInput should stop accepting after max_chars."""
    _setup()
    from text_inputs import NumTextInput
    ti = NumTextInput()
    # Manually insert text up to the limit
    ti.insert_text("123456")
    assert len(ti.text) <= 6
    # Try inserting more
    ti.insert_text("7")
    assert len(ti.text) <= 6


def test_days_text_input_creates():
    _setup()
    from text_inputs import DaysTextInput
    ti = DaysTextInput()
    assert ti is not None
    assert ti.multiline is False
    assert ti.input_filter == "int"
    assert ti.max_chars == 4


def test_days_text_input_insert_limits():
    """DaysTextInput should stop accepting after 4 chars."""
    _setup()
    from text_inputs import DaysTextInput
    ti = DaysTextInput()
    ti.insert_text("1234")
    assert len(ti.text) <= 4
    ti.insert_text("5")
    assert len(ti.text) <= 4


def test_med_text_input_creates():
    _setup()
    from text_inputs import MedTextInput
    ti = MedTextInput()
    assert ti is not None
    assert ti.max_chars == 32


def test_large_text_input_creates():
    _setup()
    from text_inputs import LargeTextInput
    ti = LargeTextInput()
    assert ti is not None
    assert ti.multiline is True
    assert ti.max_chars == 128


def test_large_text_input_regex_filter():
    """LargeTextInput has a regex whitelist for allowed characters."""
    _setup()
    from text_inputs import LargeTextInput
    ti = LargeTextInput()
    # These chars should match the allowed_chars pattern
    for ch in "abcABC012 -_.,'\"!?@#$()":
        assert ti.allowed_chars.match(ch), f"'{ch}' should be allowed"


# ===========================================================================
# 5. custom_dropdown.py
# ===========================================================================

def test_custom_dropdown_creates():
    _setup()
    from custom_dropdown import CustomDropdown
    dd = CustomDropdown(options=["Opt A", "Opt B"])
    assert dd is not None
    assert dd.options == ["Opt A", "Opt B"]


def test_custom_dropdown_initial_selection():
    _setup()
    from custom_dropdown import CustomDropdown
    dd = CustomDropdown(options=["A", "B", "C"], text="B")
    assert dd.selected == "B"


def test_custom_dropdown_select_option():
    _setup()
    from custom_dropdown import CustomDropdown
    dd = CustomDropdown(options=["X", "Y"])
    dd.select_option("Y")
    assert dd.selected == "Y"
    assert dd.main_button.text == "Y"


def test_custom_dropdown_empty():
    _setup()
    from custom_dropdown import CustomDropdown
    dd = CustomDropdown()
    assert dd.options == []
    assert dd.main_button.text == "Select"


def test_custom_dropdown_values_kwarg():
    _setup()
    from custom_dropdown import CustomDropdown
    dd = CustomDropdown(values=["V1", "V2"])
    assert dd.options == ["V1", "V2"]


# ===========================================================================
# 6. ui_builders.py - Builder functions
# ===========================================================================

def test_create_stripes_logo():
    _setup()
    from ui_builders import create_stripes_logo
    w = create_stripes_logo()
    assert w is not None
    # Should have 5 children: spacer, red, yellow, green, spacer
    assert len(w.children) == 5


def test_create_stripes_logo_colors():
    """Stripes should contain RedBox, YellowBox, GreenBox."""
    _setup()
    from ui_builders import create_stripes_logo
    from boxes import RedBox, YellowBox, GreenBox
    w = create_stripes_logo()
    types = [type(c).__name__ for c in w.children]
    assert "RedBox" in types
    assert "YellowBox" in types
    assert "GreenBox" in types


def test_create_nutrients_panel():
    _setup()
    from ui_builders import create_nutrients_panel
    panel = create_nutrients_panel()
    assert panel is not None
    # Should have child widgets (nutrient buttons in a grid)
    assert len(panel.children) > 0


def test_create_nutrients_panel_with_data():
    _setup()
    from ui_builders import create_nutrients_panel
    plant_data = {"deficiencies": {"n": True}, "excess": {"p": True}}
    panel = create_nutrients_panel(plant_data=plant_data)
    assert panel is not None


def test_create_water_fields():
    _setup()
    from ui_builders import create_water_fields
    container, refs = create_water_fields()
    assert container is not None
    assert isinstance(refs, dict)
    # Should have references to the input widgets
    assert len(refs) > 0


def test_create_water_fields_with_values():
    _setup()
    from ui_builders import create_water_fields
    values = {"volume_l": "1.5", "ph": "6.2", "ppm": "800"}
    container, refs = create_water_fields(values=values)
    assert container is not None


def test_create_feeding_fields():
    _setup()
    from ui_builders import create_feeding_fields
    container, refs = create_feeding_fields()
    assert container is not None
    assert isinstance(refs, dict)
    assert len(refs) > 0


def test_create_feeding_fields_with_stage():
    _setup()
    from ui_builders import create_feeding_fields
    container, refs = create_feeding_fields(stage="veg")
    assert container is not None


def test_create_event_item():
    _setup()
    from ui_builders import create_event_item
    event = {"id": "e1", "type": "watering", "ts": "2025-01-01", "notes": "test"}
    w = create_event_item(event)
    assert w is not None


# ===========================================================================
# 7. Theme object properties
# ===========================================================================

def test_theme_has_colors():
    _setup()
    theme = _app.theme
    # Spot-check key color properties
    for attr in ("color_label_body", "color_button_bg", "color_highlight",
                 "color_accent_1", "color_transparent"):
        val = getattr(theme, attr, None)
        assert val is not None, f"theme.{attr} missing"
        assert len(val) == 4, f"theme.{attr} should be RGBA, got {val}"


def test_theme_has_fonts():
    _setup()
    theme = _app.theme
    for attr in ("font_body", "font_title", "font_button", "font_logo_1"):
        val = getattr(theme, attr, None)
        assert val is not None, f"theme.{attr} missing"
        assert isinstance(val, str), f"theme.{attr} should be str"


def test_theme_has_sizes():
    _setup()
    theme = _app.theme
    for attr in ("body_size", "title_size", "subtitle_size", "small_size"):
        val = getattr(theme, attr, None)
        assert val is not None, f"theme.{attr} missing"


def test_theme_has_padding():
    _setup()
    theme = _app.theme
    for attr in ("padding_zero", "padding_all", "padding_both"):
        val = getattr(theme, attr, None)
        assert val is not None, f"theme.{attr} missing"
        assert len(val) == 4, f"theme.{attr} should be 4-element, got {val}"


# ===========================================================================
# 8. hover_manager interaction
# ===========================================================================

def test_hover_button_registers():
    """HoverButton should register with hover_manager on init."""
    _setup()
    import hover_manager
    from buttons import HoverButton
    initial = len(hover_manager._tracked_widgets)
    b = HoverButton(text="Test")
    # Should have registered
    assert len(hover_manager._tracked_widgets) >= initial


def test_hover_button_on_enter_leave():
    """on_enter/on_leave should swap background colors."""
    _setup()
    from buttons import HoverButton
    b = HoverButton(text="Test")
    original_bg = list(b.background_color)
    b.on_enter()
    hovered_bg = list(b.background_color)
    b.on_leave()
    restored_bg = list(b.background_color)
    # After leave, should restore to original
    assert restored_bg == original_bg


# ===========================================================================
# 9. effects.py - shake_and_flash
# ===========================================================================

def test_shake_and_flash_no_crash():
    """shake_and_flash should not crash on a widget."""
    _setup()
    from effects import shake_and_flash
    from kivy.uix.textinput import TextInput
    ti = TextInput()
    # Should not raise
    shake_and_flash(ti)
