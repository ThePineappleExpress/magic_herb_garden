"""select_garden.py - Multi-garden selection screen."""

import sys
import logging
from datetime import date

from kivy.app import App
from kivy.uix.recycleview import RecycleView

from buttons import ButtonGreen, ButtonRed, ButtonYellow
from helpers import go_to_add_garden, go_to_garden, go_to_settings, go_to_are_you_sure
from list_screen import BaseListScreen
from data import GardenRepository, IndexRepository
import lang

LOG = logging.getLogger(__name__)


class GardenListView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "GardenListItem"
        self.data = []
        self._owner = None
        self.bind(height=self._check_scroll_needed)

    def _check_scroll_needed(self, *args):
        layout = self.children[0] if self.children else None
        if layout and hasattr(layout, 'minimum_height'):
            self.do_scroll_y = layout.minimum_height > self.height
        else:
            self.do_scroll_y = True

    def on_data(self, *args):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._check_scroll_needed(), 0)

    def on_double_tap(self, index):
        if self._owner:
            self._owner._on_select()


class SelectGardenScreen(BaseListScreen):

    _title_text = lang.SCREEN_TITLE_SELECT_GARDEN
    _sort_options = [
        lang.SORT_NAME, lang.SORT_PLANT_COUNT, lang.SORT_TYPE,
        lang.SORT_LAST_PLANTED, lang.SORT_LAST_EVENT, lang.SORT_NEXT_EVENT,
    ]
    _sort_label_to_key = {
        lang.SORT_NAME: "garden_name",
        lang.SORT_PLANT_COUNT: "plant_count",
        lang.SORT_TYPE: "garden_type",
        lang.SORT_LAST_PLANTED: "last_planted",
        lang.SORT_LAST_EVENT: "last_event_ts",
        lang.SORT_NEXT_EVENT: "last_event_ts",
    }
    _default_sort_key = "last_event_ts"
    _default_ascending = False
    _searchable_fields = ["garden_name", "garden_type"]
    _legend_columns = [
        (lang.LEGEND_GARDEN_NAME, 0.5, "left"),
        (lang.LEGEND_GARDEN_TYPE, 0.2, "center"),
        (lang.LEGEND_PLANT_COUNT, 0.2, "center"),
    ]
    _list_widget_class = GardenListView

    def __init__(self, **kwargs):
        self._header_buttons = [
            (lang.OPTIONS, ButtonYellow, self._on_settings, 0.1),
            (lang.EXIT_APP, ButtonRed, self._on_exit_app, 0.1),
        ]
        self._footer_buttons = [
            (lang.ADD_GARDEN, ButtonGreen, go_to_add_garden, None, 0.6),
            (lang.ENTER_GARDEN, ButtonYellow, self._on_select, None, None),
            (lang.DELETE_GARDEN, ButtonRed, self._on_delete_pressed, None, None),
        ]
        super().__init__(**kwargs)
        self._selected_garden_id = None

    # -- Lifecycle ---------------------------------------------------------------

    def on_enter(self):
        super().on_enter()
        self._refresh_gardens()

    def _refresh_gardens(self):
        gardens = GardenRepository.list_all()
        today = date.today()
        index = IndexRepository.get_all()
        data = []
        for g in gardens:
            plants = g.get("plants", [])
            active_count = sum(
                1 for p in plants
                if isinstance(p, dict) and not self._is_harvested(p, today)
            )
            last_planted = ""
            last_event_ts = ""
            for p in plants:
                if not isinstance(p, dict):
                    continue
                dp = p.get("date_planted", "") or ""
                if dp > last_planted:
                    last_planted = dp
                pid = str(p.get("id", ""))
                idx_entry = index.get(pid, {})
                ts = idx_entry.get("last_event_ts", "") or ""
                effective_ts = max(ts, dp) if dp else ts
                if effective_ts > last_event_ts:
                    last_event_ts = effective_ts
            data.append({
                "garden_id": g.get("id", ""),
                "garden_name": g.get("name", ""),
                "garden_type": g.get("type", "").capitalize(),
                "plant_count": str(len(plants)),
                "active_plant_count": active_count,
                "last_planted": last_planted,
                "last_event_ts": last_event_ts,
            })
        self._all_items = data
        self._apply_filters()
        self._selected_garden_id = None

    def _is_active(self, item):
        return item.get("active_plant_count", 0) > 0

    @staticmethod
    def _is_harvested(plant, today):
        """Check if a plant is harvested by stage or by estimated date."""
        if plant.get("stage") == "harvested":
            return True
        dt_str = plant.get("date_planted")
        if not dt_str:
            return False
        base_f = plant.get("days_to_flower")
        try:
            base_f = int(base_f) if base_f is not None else 0
        except (ValueError, TypeError):
            base_f = 0
        if not base_f:
            return False
        penalty = int(plant.get("penalty", 0) or 0)
        est_h = (base_f + 14 + penalty) * 2
        try:
            y, m, d = map(int, dt_str.split("-"))
            planted = date(y, m, d)
            days_since = (today - planted).days
            return days_since > est_h
        except Exception:
            return False

    # -- Actions -----------------------------------------------------------------

    def _on_select(self, *args):
        garden = self.get_selected_item()
        if not garden:
            return
        app = App.get_running_app()
        app.current_garden_id = garden["garden_id"]
        go_to_garden(None)

    def _on_delete_pressed(self, *args):
        garden = self.get_selected_item()
        if not garden:
            return
        go_to_are_you_sure(lang.MSG_CONFIRM_DELETE_GARDEN,
                           lambda *_: self._do_delete(garden["garden_id"]))

    def _do_delete(self, garden_id):
        GardenRepository.delete(garden_id)
        LOG.info("Deleted garden %s", garden_id)
        app = App.get_running_app()
        app.screen.current = "select_garden"

    def _on_settings(self, *args):
        go_to_settings()

    def _on_exit_app(self, *args):
        go_to_are_you_sure(lang.MSG_CONFIRM_EXIT, lambda *_: sys.exit(0))
