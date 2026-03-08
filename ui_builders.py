"""ui_builders.py - Reusable layout builder functions.

These create the standard screen scaffolding used across most screens:
left sidebar with stripes logo + title, and a right content area.
"""

from kivy.app import App

from boxes import (
    ContentBox, ItemBox, SpacerBox, WrapperBox,
    RedBox, YellowBox, GreenBox,
)
from labels import TitleLabel


def create_stripes_logo():
    """Create the red/yellow/green stripes column."""
    stripes = ContentBox(orientation="horizontal")
    stripes.add_widget(ItemBox(size_hint_x=0.45))
    stripes.add_widget(RedBox())
    stripes.add_widget(YellowBox())
    stripes.add_widget(GreenBox())
    stripes.add_widget(ItemBox(size_hint_x=0.45))
    return stripes


def create_initial_layout(screen, app, title_text="", left_size=0.2,
                          show_day_box=True, show_info_header=True):
    """Build the standard two-column screen layout.

    Returns (screen_wrapper, layout) where:
      - screen_wrapper is the outermost horizontal BoxLayout
      - layout is the right-side vertical content area to add widgets to

    The left column contains the stripes logo and title.
    """
    screen_wrapper = WrapperBox(orientation="horizontal", size_hint_x=1)

    # -- Left sidebar ---------------------------------------------------------
    sidebar = SpacerBox(size_hint_x=left_size)
    sidebar.add_widget(create_stripes_logo())
    sidebar.add_widget(SpacerBox(size_hint_x=0.3))

    title = TitleLabel(text=title_text)
    sidebar.add_widget(title)

    sidebar.add_widget(SpacerBox(size_hint_x=0.3))
    screen_wrapper.add_widget(sidebar)

    # -- Right content area ---------------------------------------------------
    layout = WrapperBox(orientation="vertical")

    # Add content to screen via add_content (above shader background)
    screen.add_content(screen_wrapper)

    return screen_wrapper, layout


def create_event_item(event_data, on_select=None):
    """Create a single event row widget from event data dict."""
    from boxes import SelectableEventBox
    from labels import FieldLabel

    row = SelectableEventBox(
        orientation="horizontal",
        size_hint_y=None,
        height=40,
        spacing=4,
    )

    ts_label = FieldLabel(text=event_data.get("ts", ""), size_hint_x=0.2)
    type_label = FieldLabel(text=event_data.get("type", ""), size_hint_x=0.15)
    notes_label = FieldLabel(text=event_data.get("notes", "")[:60], size_hint_x=0.65)

    row.add_widget(ts_label)
    row.add_widget(type_label)
    row.add_widget(notes_label)

    if on_select:
        row.bind(on_press=lambda *_: on_select(event_data))

    return row


def create_timeline_shell(screen, app, title_text=""):
    """Create the shell for the timeline screen with tabs."""
    screen_wrapper, layout = create_initial_layout(
        screen, app, title_text=title_text, left_size=0.1,
        show_day_box=False, show_info_header=False,
    )
    return screen_wrapper, layout


def create_nutrients_panel():
    """Create a nutrients display panel."""
    from labels import FieldLabel

    panel = ContentBox(orientation="vertical")
    panel.add_widget(FieldLabel(text="Nutrients", bold=True))
    return panel


def create_water_fields():
    """Create water input fields layout."""
    from labels import FieldLabel
    from text_inputs import NumTextInput

    layout = ContentBox(orientation="vertical")
    return layout


def create_feeding_fields():
    """Create feeding input fields layout."""
    from labels import FieldLabel
    from text_inputs import NumTextInput

    layout = ContentBox(orientation="vertical")
    return layout
