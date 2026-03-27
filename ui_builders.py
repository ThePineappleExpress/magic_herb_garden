"""ui_builders.py - Reusable layout builder functions.

These create the standard screen scaffolding used across most screens:
left sidebar with stripes logo + title, and a right content area.

Also provides builders for water/feeding input panels and nutrient
display/edit grids, shared between add_event.py and plant_details.py.
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


def create_nutrients_panel(plant_data=None, get_nutrient_fn=None):
    """Create a nutrients display/edit panel.

    Parameters
    ----------
    plant_data : dict or None
        If provided, renders a **read-only** nutrient status grid with
        color-coded boxes (YellowBox for deficient/excess, GreenBox normal).
        Used by plant_details.py.
    get_nutrient_fn : callable or None
        ``fn(plant_dict, key) -> "deficient"|"excess"|False``.  Required when
        *plant_data* is provided.  If omitted with *plant_data*, falls back to
        a trivial lookup.

    When *plant_data* is ``None`` the panel contains interactive
    ``NutrientButton`` / ``ResetButton`` widgets for toggling
    deficiency/excess state (used by add_event.py).

    Returns
    -------
    nutrients_box : Widget
        The complete nutrients container ready to be added to a parent layout.
    """
    from labels import FieldLabel, NutrientLabel
    import lang

    app = App.get_running_app()

    NUTRIENTS = ["n", "p", "k", "ca", "mg", "s", "fe", "mn", "zn", "cu", "b", "mo"]

    nutrients_box = WrapperBox(orientation="vertical", size_hint_y=0.4)

    # Title row
    title_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
    nutrients_box.add_widget(title_box)
    title = FieldLabel(text=lang.NUTRIENTS, valign="bottom", halign="left")
    title.color = app.theme.color_field_label
    title.font_size = app.theme.body_size
    title_box.add_widget(title)

    # Data grid
    data_box = ContentBox(orientation="horizontal", size_hint_y=0.8, spacing=0)
    nutrients_box.add_widget(data_box)

    if plant_data is not None:
        # Read-only display mode (plant_details.py)
        if get_nutrient_fn is None:
            def get_nutrient_fn(d, k):
                if d.get("deficiencies", {}).get(k):
                    return "deficient"
                if d.get("excess", {}).get(k):
                    return "excess"
                return False

        for nutrient in NUTRIENTS:
            col = GreenBox(orientation="vertical", spacing=0, padding=0, size_hint=(1, 1))
            data_box.add_widget(col)
            for text in ["+", nutrient.capitalize(), "-"]:
                if text == "+":
                    if get_nutrient_fn(plant_data, nutrient) == "excess":
                        sub = YellowBox(orientation="vertical")
                    else:
                        sub = GreenBox(orientation="vertical")
                elif text == "-":
                    if get_nutrient_fn(plant_data, nutrient) == "deficient":
                        sub = YellowBox(orientation="vertical")
                    else:
                        sub = GreenBox(orientation="vertical")
                else:
                    sub = GreenBox(orientation="vertical", size_hint_x=1)
                    label = NutrientLabel(
                        text=nutrient.capitalize(), valign="middle",
                        halign="center", size_hint_x=1,
                    )
                    label.font_name = app.theme.font_logo_2
                    label.color = app.theme.color_button_bg
                    label.font_size = app.theme.subtitle_size
                    label.text_size = label.size
                    label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
                    sub.add_widget(label)
                col.add_widget(sub)
    else:
        # Interactive toggle mode (add_event.py)
        from buttons import NutrientButton, ResetButton

        for nutrient in NUTRIENTS:
            col = GreenBox(orientation="vertical", spacing=0, padding=0, size_hint=(1, 1))
            data_box.add_widget(col)
            for text in ["+", nutrient.capitalize(), "-"]:
                if text == "+":
                    btn = NutrientButton(text=text, group=nutrient, size_hint=(1, 1 / 3))
                elif text == "-":
                    btn = NutrientButton(text=text, group=nutrient, size_hint=(1, 1 / 3))
                else:
                    btn = ResetButton(text=text, group=nutrient, size_hint=(1, 1 / 3))
                col.add_widget(btn)

    return nutrients_box


def create_water_fields(values=None):
    """Create a row of water input or display fields.

    Parameters
    ----------
    values : dict or None
        If ``None``, creates editable ``NumTextInput`` widgets (add_event.py).
        If a dict, creates read-only ``FieldLabel`` widgets showing values.
        Expected keys: ``"volume"``, ``"temp"``, ``"ph"``, ``"ppm"``.

    Returns
    -------
    (water_row, refs) : tuple
        *water_row* is the container widget.
        *refs* is a dict mapping attribute names to the value widgets:
        ``{"water_volume_input": w, "water_temp_input": w, "ph_input": w, "ppm_input": w}``
    """
    from labels import FieldLabel
    from text_inputs import NumTextInput
    import lang

    app = App.get_running_app()

    water_row = WrapperBox(orientation="horizontal", size_hint_y=0.2)
    refs = {}
    field_defs = [
        ("Volume", "water_volume_input", "volume"),
        ("Temp", "water_temp_input", "temp"),
        ("pH", "ph_input", "ph"),
        ("PPM", "ppm_input", "ppm"),
    ]
    for title, attr, val_key in field_defs:
        wbox = WrapperBox(orientation="vertical")

        title_box = ContentBox(orientation="horizontal")
        label = FieldLabel(text=title, valign="bottom", halign="left")
        label.color = app.theme.color_water_label
        label.font_size = app.theme.small_size
        title_box.add_widget(label)
        wbox.add_widget(title_box)

        value_box = ContentBox(orientation="horizontal")
        if values is not None:
            raw = values.get(val_key)
            display = str(raw) if raw not in (None, "") else "\u2013"
            value_label = FieldLabel(text=display, valign="top", halign="left")
        else:
            value_label = NumTextInput(hint_text=lang.HINT_NUM_DEFAULT)
        value_label.font_size = app.theme.subtitle_size
        value_label.color = app.theme.color_field_value
        value_box.add_widget(value_label)
        wbox.add_widget(value_box)

        water_row.add_widget(wbox)
        refs[attr] = value_label

    return water_row, refs


def create_feeding_fields(values=None, stage=None):
    """Create feeding input/display rows.

    Parameters
    ----------
    values : dict or None
        If ``None``, creates editable ``NumTextInput`` / ``CustomDropdown``
        widgets (add_event.py).
        If a dict, creates read-only ``FieldLabel`` widgets.
        Expected keys: ``"grow_mix"``, ``"root_mix"``, ``"soil_boost"``,
        ``"vit_boost"``, ``"bloom_mix"``, ``"bloom_boost"``, ``"calmag"``,
        ``"fungi"``.
    stage : str or None
        Plant stage (``"vegetative"`` / ``"flowering"``).  In display mode,
        stage-irrelevant fields show ``"–"``.

    Returns
    -------
    (container, refs) : tuple
        *container* holds both feeding rows.
        *refs* maps attribute names to value widgets.
    """
    from labels import FieldLabel
    from text_inputs import NumTextInput
    from custom_dropdown import CustomDropdown
    import lang

    app = App.get_running_app()

    container = WrapperBox(orientation="vertical")
    refs = {}

    # Row 1: Veg / Root / Soil / Vit
    row1 = WrapperBox(orientation="horizontal", size_hint_y=0.33)
    container.add_widget(row1)

    row1_defs = [
        ("Veg", "grow_mix_input", "grow_mix"),
        ("Root", "root_mix_input", "root_mix"),
        ("Soil", "soil_boost_input", "soil_boost"),
        ("Vit", "vit_boost_input", "vit_boost"),
    ]
    for title, attr, val_key in row1_defs:
        wbox = WrapperBox(orientation="vertical")

        title_box = ContentBox(orientation="horizontal")
        label = FieldLabel(text=title, valign="bottom", halign="left")
        label.color = app.theme.color_feed_label
        label.font_size = app.theme.small_size
        title_box.add_widget(label)
        wbox.add_widget(title_box)

        value_box = ContentBox(orientation="horizontal")
        if values is not None:
            # Display mode - stage-conditional dimming for Veg
            raw = values.get(val_key)
            if val_key == "grow_mix" and stage != "vegetative":
                raw = None
            display = str(raw) if raw not in (None, "") else "\u2013"
            value_label = FieldLabel(text=display, valign="top", halign="left")
            value_label.font_size = app.theme.subtitle_size
            value_label.color = app.theme.color_field_value
        else:
            value_label = NumTextInput(hint_text=lang.HINT_NUM_DEFAULT)
            value_label.font_size = app.theme.subtitle_size
            value_label.color = app.theme.color_field_value
        value_box.add_widget(value_label)
        wbox.add_widget(value_box)

        row1.add_widget(wbox)
        refs[attr] = value_label

    # Row 2: Flower / Tops / CalMag / Fungi
    row2 = WrapperBox(orientation="horizontal", size_hint_y=0.33)
    container.add_widget(row2)

    row2_defs = [
        ("Flower", "bloom_mix_input", "bloom_mix"),
        ("Tops", "bloom_boost_input", "bloom_boost"),
        ("CalMag", "calmag_input", "calmag"),
        ("Fungi", "fungi_dropdown", "fungi"),
    ]
    for title, attr, val_key in row2_defs:
        wbox = WrapperBox(orientation="vertical")

        title_box = ContentBox(orientation="horizontal")
        label = FieldLabel(text=title, valign="bottom", halign="left")
        label.color = app.theme.color_feed_label
        label.font_size = app.theme.small_size
        title_box.add_widget(label)
        wbox.add_widget(title_box)

        value_box = ContentBox(orientation="horizontal")
        if values is not None:
            # Display mode
            raw = values.get(val_key)
            if val_key in ("bloom_mix", "bloom_boost") and stage != "flowering":
                raw = None
            if val_key == "fungi":
                display = "Yes" if raw else "No"
                value_label = FieldLabel(text=display, valign="top", halign="left")
                value_label.font_size = app.theme.subtitle_size
                value_label.color = (
                    app.theme.color_field_label if display == "Yes"
                    else app.theme.color_label_body
                )
            else:
                display = str(raw) if raw not in (None, "") else "\u2013"
                value_label = FieldLabel(text=display, valign="top", halign="left")
                value_label.font_size = app.theme.subtitle_size
                value_label.color = app.theme.color_field_value
        else:
            # Input mode
            if title == "Fungi":
                value_label = CustomDropdown(selected="no", values=["yes", "no"])
            else:
                value_label = NumTextInput(hint_text=lang.HINT_NUM_DEFAULT)
                value_label.font_size = app.theme.subtitle_size
                value_label.color = app.theme.color_field_value
        value_box.add_widget(value_label)
        wbox.add_widget(value_box)

        row2.add_widget(wbox)
        refs[attr] = value_label

    return container, refs
