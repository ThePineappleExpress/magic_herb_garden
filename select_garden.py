"""select_garden.py - Multi-garden selection screen."""

import logging

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.togglebutton import ToggleButton

from boxes import (
    TitleBox, WrapperBox, ContentBox, ItemBox, SpacerBox,
    RedBox, YellowBox, GreenBox, SelectableBoxLayout, SelectableRecycleBoxLayout,
)
from buttons import ButtonGreen, ButtonRed, ButtonYellow
from labels import FieldLabel, TitleLabel
from text_inputs import MedTextInput
from custom_dropdown import CustomDropdown
from screens import BaseScreen
import lang
import storage

LOG = logging.getLogger(__name__)


class GardenListView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "GardenListItem"
        self.data = []
        self._owner = None  # set by SelectGardenScreen

    def on_double_tap(self, index):
        """Called by SelectableBoxLayout on double-tap; enters the garden."""
        if self._owner:
            self._owner._on_select()


class SelectGardenScreen(BaseScreen):

    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_garden_id = None

        screen_wrapper = WrapperBox(orientation="horizontal", size_hint_x=1)

        # -- Left sidebar (same pattern as garden_view) -------------------------
        spacer_left = SpacerBox(size_hint_x=0.2)
        stripes_holder = ContentBox(orientation="horizontal")
        stripes_holder.add_widget(ItemBox(size_hint_x=0.45))
        stripes_holder.add_widget(RedBox())
        stripes_holder.add_widget(YellowBox())
        stripes_holder.add_widget(GreenBox())
        stripes_holder.add_widget(ItemBox(size_hint_x=0.45))
        spacer_left.add_widget(stripes_holder)
        spacer_left.add_widget(SpacerBox(size_hint_x=0.3))
        title = TitleLabel(
            text=lang.SCREEN_TITLE_SELECT_GARDEN.format(color=TitleLabel().hex_color)
        )
        spacer_left.add_widget(title)
        spacer_left.add_widget(SpacerBox(size_hint_x=0.3))
        screen_wrapper.add_widget(spacer_left)

        # -- Right content area -------------------------------------------------
        content_wrapper = ContentBox(orientation="vertical", size_hint=(1, 1))

        # Header
        header = TitleBox(orientation="horizontal", size_hint_y=0.1)
        header.add_widget(SpacerBox(size_hint_x=0.8))
        side_menu = ItemBox(orientation="horizontal", size_hint_x=0.2)
        settings_btn = ButtonYellow(text=lang.OPTIONS, size_hint_x=0.1)
        settings_btn.bind(on_press=self._on_settings)
        side_menu.add_widget(settings_btn)
        header.add_widget(side_menu)
        content_wrapper.add_widget(header)

        content_wrapper.add_widget(SpacerBox(size_hint_y=0.02))

        # ── Sort / Search toolbar ──
        toolbar = ContentBox(orientation="horizontal", size_hint_y=None, height="40dp")

        self._sort_key = "garden_name"
        self._sort_ascending = True
        sort_options = [lang.SORT_NAME, lang.SORT_PLANT_COUNT]
        self._sort_label_to_key = {
            lang.SORT_NAME: "garden_name",
            lang.SORT_PLANT_COUNT: "plant_count",
        }
        sort_label = FieldLabel(text=lang.SORT_BY, size_hint_x=None, width="60dp")
        toolbar.add_widget(sort_label)
        self.sort_dropdown = CustomDropdown(
            options=sort_options, size_hint_x=0.2,
        )
        self.sort_dropdown.selected = lang.SORT_NAME
        self.sort_dropdown.main_button.text = lang.SORT_NAME
        self.sort_dropdown.bind(selected=self._on_sort_changed)
        toolbar.add_widget(self.sort_dropdown)

        self.sort_dir_btn = ToggleButton(
            text=lang.SORT_ASCENDING, size_hint_x=None, width="100dp",
        )
        self.sort_dir_btn.bind(on_press=self._on_sort_dir_toggle)
        toolbar.add_widget(self.sort_dir_btn)

        toolbar.add_widget(SpacerBox(size_hint_x=0.05))

        self.search_input = MedTextInput(
            hint_text=lang.SEARCH_HINT, size_hint_x=0.3,
            multiline=False,
        )
        self.search_input.bind(text=self._on_search_text)
        toolbar.add_widget(self.search_input)

        content_wrapper.add_widget(toolbar)

        content_wrapper.add_widget(SpacerBox(size_hint_y=0.02))

        # Garden list (RecycleView)
        list_area = ItemBox(orientation="horizontal", size_hint_y=1)
        list_area.add_widget(SpacerBox(size_hint_x=0.02))
        self.garden_list = GardenListView(size_hint_x=1)
        self.garden_list._owner = self
        list_area.add_widget(self.garden_list)
        list_area.add_widget(SpacerBox(size_hint_x=0.02))
        content_wrapper.add_widget(list_area)

        content_wrapper.add_widget(SpacerBox(size_hint_y=0.02))

        # Footer buttons
        footer = ContentBox(orientation="horizontal", size_hint_y=0.1)
        footer.add_widget(SpacerBox(size_hint_x=0.6))
        add_btn = ButtonGreen(text=lang.ADD_GARDEN)
        add_btn.bind(on_press=self._on_add_garden)
        footer.add_widget(add_btn)
        select_btn = ButtonYellow(text=lang.ENTER_GARDEN)
        select_btn.bind(on_press=self._on_select)
        footer.add_widget(select_btn)
        delete_btn = ButtonRed(text=lang.DELETE_GARDEN)
        delete_btn.bind(on_press=self._on_delete_pressed)
        footer.add_widget(delete_btn)
        content_wrapper.add_widget(footer)

        screen_wrapper.add_widget(content_wrapper)
        self.add_content(screen_wrapper)

    # -- Lifecycle ---------------------------------------------------------------

    def on_enter(self):
        self._refresh_gardens()

    def _refresh_gardens(self):
        gardens = storage.load_gardens()
        data = []
        for g in gardens:
            data.append({
                "garden_id": g.get("id", ""),
                "garden_name": g.get("name", ""),
                "garden_type": g.get("type", "").capitalize(),
                "plant_count": str(len(g.get("plants", []))),
            })
        self._all_gardens = data
        self._apply_filters()
        self._selected_garden_id = None

    def _apply_filters(self):
        """Apply search and sort to _all_gardens → garden_list.data."""
        items = list(self._all_gardens)

        # Search filter
        query = getattr(self, 'search_input', None)
        search_text = query.text.strip().lower() if query else ""
        if search_text:
            items = [
                g for g in items
                if search_text in (g.get("garden_name") or "").lower()
                or search_text in (g.get("garden_type") or "").lower()
            ]

        # Sort
        key = getattr(self, '_sort_key', 'garden_name')
        ascending = getattr(self, '_sort_ascending', True)

        def sort_val(g):
            v = g.get(key) or ""
            try:
                return (0, float(v))
            except (ValueError, TypeError):
                return (1, v.lower())

        items.sort(key=sort_val, reverse=not ascending)
        self.garden_list.data = items

    def _on_sort_changed(self, instance, value):
        self._sort_key = self._sort_label_to_key.get(value, "garden_name")
        self._apply_filters()

    def _on_sort_dir_toggle(self, instance):
        if instance.state == "down":
            self._sort_ascending = False
            instance.text = lang.SORT_DESCENDING
        else:
            self._sort_ascending = True
            instance.text = lang.SORT_ASCENDING
        self._apply_filters()

    def _on_search_text(self, instance, value):
        self._apply_filters()

    # -- Selection ---------------------------------------------------------------

    def _get_selected_index(self):
        lm = self.garden_list.layout_manager
        if not lm or not lm.selected_nodes:
            return None
        return lm.selected_nodes[0]

    def _get_selected_garden(self):
        idx = self._get_selected_index()
        if idx is None:
            return None
        return self.garden_list.data[idx]

    # -- Actions -----------------------------------------------------------------

    def _on_select(self, *args):
        garden = self._get_selected_garden()
        if not garden:
            return
        app = App.get_running_app()
        app.current_garden_id = garden["garden_id"]
        app.previous_screen = "select_garden"
        garden_screen = app.screen.get_screen("garden_view")
        garden_screen.refresh_plants()
        app.screen.current = "garden_view"

    def _on_add_garden(self, *args):
        app = App.get_running_app()
        app.previous_screen = "select_garden"
        app.screen.current = "add_garden"

    def _on_delete_pressed(self, *args):
        garden = self._get_selected_garden()
        if not garden:
            return
        app = App.get_running_app()
        are_you_sure = app.screen.get_screen("are_you_sure")
        are_you_sure.prompt_text = lang.MSG_CONFIRM_DELETE_GARDEN
        are_you_sure.confirm_callback = lambda *_: self._do_delete(garden["garden_id"])
        app.previous_screen = "select_garden"
        app.screen.current = "are_you_sure"

    def _do_delete(self, garden_id):
        storage.delete_garden(garden_id)
        LOG.info("Deleted garden %s", garden_id)
        app = App.get_running_app()
        app.screen.current = "select_garden"

    def _on_settings(self, *args):
        app = App.get_running_app()
        app.previous_screen = "select_garden"
        app.screen.current = "settings"
