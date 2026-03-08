"""select_garden.py - Multi-garden selection screen."""

import logging

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

from boxes import ContentBox, ItemBox, SpacerBox, WrapperBox, SelectableEventBox
from buttons import ButtonGreen, ButtonRed, ButtonYellow
from labels import FieldLabel, TitleLabel
from screens import BaseScreen
from ui_builders import create_initial_layout
import lang
import storage

LOG = logging.getLogger(__name__)


class GardenCard(SelectableEventBox):
    """A selectable row representing a garden in the list."""
    pass


class SelectGardenScreen(BaseScreen):

    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_garden_id = None

        app = App.get_running_app()
        title_text = lang.SCREEN_TITLE_SELECT_GARDEN.format(color=TitleLabel().hex_color)
        screen_wrapper, layout = create_initial_layout(
            self, app, title_text=title_text, left_size=0.1,
            show_day_box=False, show_info_header=False,
        )

        layout.add_widget(WrapperBox(size_hint_y=0.3))

        # -- Legend row ---------------------------------------------------------
        legend = ContentBox(orientation="horizontal", size_hint_y=None, height=30)
        legend.add_widget(FieldLabel(text=lang.LEGEND_GARDEN_NAME, size_hint_x=0.4, bold=True))
        legend.add_widget(FieldLabel(text=lang.LEGEND_GARDEN_TYPE, size_hint_x=0.2, bold=True))
        legend.add_widget(FieldLabel(text=lang.LEGEND_PLANT_COUNT, size_hint_x=0.2, bold=True))
        legend.add_widget(SpacerBox(size_hint_x=0.2))
        layout.add_widget(legend)

        layout.add_widget(SpacerBox(size_hint_y=0.01))

        # -- Garden list (scrollable) ------------------------------------------
        scroll_area = BoxLayout(orientation="horizontal", size_hint_y=3.0)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self._garden_container = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=4, padding=(4, 4),
        )
        self._garden_container.bind(
            minimum_height=self._garden_container.setter("height")
        )
        scroll.add_widget(self._garden_container)
        scroll_area.add_widget(scroll)
        layout.add_widget(scroll_area)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Buttons ------------------------------------------------------------
        btn_row = WrapperBox(orientation="horizontal")

        add_holder = ItemBox(orientation="horizontal")
        add_btn = ButtonGreen(text=lang.ADD_GARDEN.replace("\n", " "))
        add_btn.bind(on_press=self._on_add_garden)
        add_holder.add_widget(add_btn)
        btn_row.add_widget(add_holder)

        enter_holder = ItemBox(orientation="horizontal")
        enter_btn = ButtonYellow(text=lang.SELECT_GARDEN)
        enter_btn.bind(on_press=self._on_select)
        enter_holder.add_widget(enter_btn)
        btn_row.add_widget(enter_holder)

        delete_holder = ItemBox(orientation="horizontal")
        delete_btn = ButtonRed(text=lang.DELETE_GARDEN.replace("\n", " "))
        delete_btn.bind(on_press=self._on_delete)
        delete_holder.add_widget(delete_btn)
        btn_row.add_widget(delete_holder)

        settings_holder = ItemBox(orientation="horizontal")
        settings_btn = ButtonYellow(text="Settings")
        settings_btn.bind(on_press=self._on_settings)
        settings_holder.add_widget(settings_btn)
        btn_row.add_widget(settings_holder)

        layout.add_widget(btn_row)
        layout.add_widget(WrapperBox(size_hint_y=0.3))

        screen_wrapper.add_widget(layout)
        screen_wrapper.add_widget(SpacerBox(size_hint_x=0.1))

    def on_enter(self):
        self._rebuild_list()

    def _rebuild_list(self):
        self._garden_container.clear_widgets()
        self._selected_garden_id = None

        gardens = storage.load_gardens()
        for garden in gardens:
            gid = garden.get("id", "")
            name = garden.get("name", gid)
            gtype = garden.get("type", "")
            plant_count = len(garden.get("plants", []))

            row = GardenCard(
                orientation="horizontal",
                size_hint_y=None,
                height=48,
                spacing=8,
            )
            row.add_widget(FieldLabel(text=name, size_hint_x=0.4))
            row.add_widget(FieldLabel(text=gtype.capitalize(), size_hint_x=0.2))
            row.add_widget(FieldLabel(text=str(plant_count), size_hint_x=0.2))
            row.add_widget(SpacerBox(size_hint_x=0.2))

            # Bind selection
            row.bind(on_press=lambda inst, _gid=gid: self._on_card_pressed(_gid))
            self._garden_container.add_widget(row)

    def _on_card_pressed(self, garden_id):
        self._selected_garden_id = garden_id
        # Update visual selection
        for child in self._garden_container.children:
            if isinstance(child, GardenCard):
                child.selected = False
        # Find and select the pressed card
        for child in self._garden_container.children:
            if isinstance(child, GardenCard):
                labels = [c for c in child.children if hasattr(c, "text")]
                # The garden_id is captured in the closure, match by checking order
                child.selected = True
                break

    def _on_select(self, *args):
        if not self._selected_garden_id:
            return
        app = App.get_running_app()
        app.current_garden_id = self._selected_garden_id
        app.previous_screen = "select_garden"

        target = getattr(app, "post_garden_select_screen", "garden_view")
        app.screen.current = target

    def _on_add_garden(self, *args):
        app = App.get_running_app()
        app.previous_screen = "select_garden"
        app.screen.current = "add_garden"

    def _on_delete(self, *args):
        if not self._selected_garden_id:
            return
        app = App.get_running_app()
        are_you_sure = app.screen.get_screen("are_you_sure")
        are_you_sure.prompt_text = lang.MSG_CONFIRM_DELETE_GARDEN
        are_you_sure.confirm_callback = lambda *_: self._do_delete()
        app.previous_screen = "select_garden"
        app.screen.current = "are_you_sure"

    def _do_delete(self):
        if self._selected_garden_id:
            storage.delete_garden(self._selected_garden_id)
            LOG.info("Deleted garden %s", self._selected_garden_id)
            self._selected_garden_id = None
        app = App.get_running_app()
        app.screen.current = "select_garden"

    def _on_settings(self, *args):
        app = App.get_running_app()
        app.previous_screen = "select_garden"
        app.screen.current = "settings"
