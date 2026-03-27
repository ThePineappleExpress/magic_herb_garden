"""plant_screen.py - Base class for plant-specific screens.

Provides the shared sidebar + plant header layout (name, strain with gene
coloring, notes, days-passed counter) and the common _update_ui logic.
Subclasses add their own content below the header.
"""

import datetime

from kivy.app import App

from boxes import ContentBox, SpacerBox, WrapperBox
from labels import FieldLabel, TitleLabel
from buttons import ButtonGreen, ButtonYellow, ButtonRed
from photo_widgets import PhotoStrip
from helpers import get_difference_days
from screens import BaseScreen
from ui_builders import create_stripes_logo
import lang


class BasePlantScreen(BaseScreen):
    """Common base for PlantDetailsScreen and AddEventScreen.

    Subclasses must:
      - Call ``_build_sidebar_and_header(title_text)`` from ``__init__`` to get
        (screen_wrapper, content_wrapper) — then add their own widgets to
        content_wrapper.
      - Override ``_update_ui()`` calling ``super()._update_ui()`` first, then
        do screen-specific work.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plant = None
        self.genes = ""

    def _build_sidebar_and_header(self, title_text):
        """Build the sidebar + plant header. Returns (screen_wrapper, content_wrapper).

        The content_wrapper already contains a spacer and the header; the
        subclass should add its own widgets below.
        """
        app = App.get_running_app()

        screen_wrapper = WrapperBox(orientation="horizontal")

        # -- Sidebar --
        sidebar = SpacerBox(size_hint_x=0.2)
        sidebar.add_widget(create_stripes_logo())
        sidebar.add_widget(SpacerBox(size_hint_x=0.3))
        title = TitleLabel(text=title_text.format(color=TitleLabel().hex_color))
        sidebar.add_widget(title)
        sidebar.add_widget(SpacerBox(size_hint_x=0.3))
        screen_wrapper.add_widget(sidebar)

        # -- Content area --
        content_wrapper = WrapperBox(orientation="vertical", size_hint=(1, 1))
        content_wrapper.add_widget(SpacerBox(size_hint_y=0.1))

        # -- Plant header --
        header = WrapperBox(orientation="horizontal", size_hint_y=0.3)
        content_wrapper.add_widget(header)

        title_box = ContentBox(orientation="vertical")
        header.add_widget(title_box)
        title_box.add_widget(SpacerBox(size_hint_y=0.2))

        name_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        self.name_label = FieldLabel(text="", valign="middle", halign="left")
        self.name_label.font_size = app.theme.subtitle_size
        self.name_label.color = app.theme.color_field_value
        name_box.add_widget(self.name_label)
        title_box.add_widget(name_box)

        strain_box = ContentBox(orientation="horizontal", size_hint_y=0.3)
        self.strain_label = FieldLabel(text="", valign="middle", halign="left")
        self.strain_label.font_size = app.theme.logo_size_2
        self.strain_label.color = app.theme.color_field_value
        strain_box.add_widget(self.strain_label)
        title_box.add_widget(strain_box)

        notes_box = ContentBox(orientation="horizontal", size_hint_y=0.15)
        self.notes_label = FieldLabel(text="", valign="middle", halign="left")
        self.notes_label.font_size = app.theme.body_size
        self.notes_label.color = app.theme.color_field_value
        notes_box.add_widget(self.notes_label)
        title_box.add_widget(notes_box)

        water_data_box = ContentBox(orientation="horizontal", size_hint_y=0.15)
        self.last_water_label = FieldLabel(text="", valign="middle", halign="left")
        self.last_water_label.font_size = app.theme.body_size
        water_data_box.add_widget(self.last_water_label)
        title_box.add_widget(water_data_box)

        header.add_widget(SpacerBox(size_hint_x=0.1))

        days_passed_box = ContentBox(orientation="vertical", size_hint_x=0.2)
        header.add_widget(days_passed_box)
        days_passed_box.add_widget(SpacerBox(size_hint_y=0.3))

        days_title_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        days_passed_box.add_widget(days_title_box)
        days_title = FieldLabel(text=lang.DAY_LABEL, valign="middle", halign="right")
        days_title.font_size = app.theme.subtitle_size
        days_title_box.add_widget(days_title)

        days_value_box = ContentBox(orientation="horizontal", size_hint_y=0.5)
        days_passed_box.add_widget(days_value_box)
        self.days_passed_value = FieldLabel(text="", valign="middle", halign="right")
        self.days_passed_value.font_size = app.theme.logo_size_1
        self.days_passed_value.color = app.theme.color_field_value
        days_value_box.add_widget(self.days_passed_value)

        days_stage_box = ContentBox(orientation="vertical", size_hint_y=0.1)
        days_passed_box.add_widget(days_stage_box)
        self.days_stage_value = FieldLabel(text="", valign="middle", halign="right")
        self.days_stage_value.font_size = app.theme.body_size
        self.days_stage_value.color = app.theme.color_field_value
        days_stage_box.add_widget(self.days_stage_value)

        content_wrapper.add_widget(SpacerBox(size_hint_y=0.02))

        return screen_wrapper, content_wrapper

    def _update_ui(self):
        """Update plant header labels and gene coloring. Call super() first in overrides."""
        app = App.get_running_app()
        plant = self.plant or {}
        self.genes = plant.get("genes", "")
        self.name_label.text = " | ".join([plant.get("seedbank", ""), self.genes])

        self.strain_label.text = plant.get("strain", "")
        genes = (self.genes or "").strip().lower()
        if genes == "sativa":
            self.strain_label.color = app.theme.color_strain_sativa
        elif genes == "indica":
            self.strain_label.color = app.theme.color_strain_indica
        elif genes == "hybrid":
            self.strain_label.color = app.theme.color_strain_hybrid
        else:
            self.strain_label.color = app.theme.color_strain_unknown

        self.notes_label.text = plant.get("notes") or ""
        days_passed = get_difference_days(datetime.datetime.now(), plant.get("date_planted", ""))
        self.days_passed_value.text = str(days_passed) if days_passed is not None else lang.DASH

    @staticmethod
    def build_photo_strip(on_select, on_double_click, gallery_callback,
                          add_callback, delete_callback,
                          gallery_text=None):
        """Build a photo column with strip + buttons. Returns (column_widget, photo_strip)."""
        app = App.get_running_app()
        column = WrapperBox(orientation="vertical", size_hint_x=0.33)

        title_box = ContentBox(orientation="horizontal", size_hint_y=0.1)
        column.add_widget(title_box)
        title = FieldLabel(text=lang.PHOTOS_TITLE, valign="bottom", halign="left")
        title.color = app.theme.color_field_label
        title.font_size = app.theme.subtitle_size
        title_box.add_widget(title)

        strip = PhotoStrip(
            size_hint_y=0.7,
            on_select=on_select,
            on_double_click=on_double_click,
        )
        column.add_widget(strip)

        buttons_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        column.add_widget(buttons_box)

        gallery_btn = ButtonGreen(
            text=gallery_text or lang.PHOTO_VIEW_GALLERY, size_hint_x=0.34,
        )
        gallery_btn.font_size = app.theme.small_size
        gallery_btn.bind(on_release=lambda *_: gallery_callback())
        buttons_box.add_widget(gallery_btn)

        add_btn = ButtonYellow(text=lang.PHOTO_ADD, size_hint_x=0.33)
        add_btn.font_size = app.theme.small_size
        add_btn.bind(on_release=lambda *_: add_callback())
        buttons_box.add_widget(add_btn)

        delete_btn = ButtonRed(text=lang.PHOTO_DELETE, size_hint_x=0.33)
        delete_btn.font_size = app.theme.small_size
        delete_btn.bind(on_release=lambda *_: delete_callback())
        buttons_box.add_widget(delete_btn)

        return column, strip
