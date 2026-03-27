import sys
from datetime import date
from kivy.properties import StringProperty, ObjectProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.svg import Svg
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale
from kivy.uix.recycleview import RecycleView

from data import PlantRepository, IndexRepository
import lang
from helpers import (on_plant_seed, get_difference_days, go_to_add_event,
                      go_to_timeline, go_to_plant_details, go_to_settings,
                      go_to_select_garden, go_to_are_you_sure)
from buttons import ButtonGreen, ButtonRed, ButtonYellow
from list_screen import BaseListScreen


class LeafIcon(Widget):
    source = StringProperty("")
    _svg = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(source=self._on_source, pos=self._redraw, size=self._redraw)

    def _on_source(self, *args):
        self._svg = Svg(self.source) if self.source else None
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        if not self._svg:
            return
        svg = self._svg
        if self.height <= 0 or self.width <= 0 or svg.width <= 0 or svg.height <= 0:
            return
        scale = (self.height / svg.height) / 1.5
        scaled_w = svg.width * scale
        scaled_h = svg.height * scale
        x = self.x + (self.width - scaled_w) * 0.5
        y = self.y + (self.height - scaled_h) * 0.6
        self.canvas.add(PushMatrix())
        self.canvas.add(Translate(x, y))
        self.canvas.add(Scale(scale, scale, 1))
        self.canvas.add(svg)
        self.canvas.add(PopMatrix())


class PlantListView(RecycleView):
    genes = StringProperty("")
    genes_icon = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "PlantListItem"
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
        if self._owner and 0 <= index < len(self.data):
            self._owner.on_details_button()

    def on_genes(self, instance, value):
        if value == "Sativa":
            self.genes_icon = "S"
        elif value == "Indica":
            self.genes_icon = "I"
        elif value == "Hybrid":
            self.genes_icon = "H"
        else:
            self.genes_icon = "?"


class GardenViewScreen(BaseListScreen):

    _title_text = lang.SCREEN_TITLE_GARDEN
    _sort_options = [
        lang.SORT_NAME, lang.SORT_BREEDER, lang.SORT_DATE_PLANTED,
        lang.SORT_LAST_EVENT, lang.SORT_NEXT_EVENT,
        lang.SORT_DAYS_TO_HARVEST, lang.SORT_DAYS_TO_WATER, lang.SORT_MEDIUM,
    ]
    _sort_label_to_key = {
        lang.SORT_NAME: "strain",
        lang.SORT_BREEDER: "seedbank",
        lang.SORT_DATE_PLANTED: "date_planted",
        lang.SORT_LAST_EVENT: "last_event_ts",
        lang.SORT_NEXT_EVENT: "last_event_ts",
        lang.SORT_DAYS_TO_HARVEST: "harvest_status",
        lang.SORT_DAYS_TO_WATER: "last_watering",
        lang.SORT_MEDIUM: "medium",
    }
    _default_sort_key = "last_event_ts"
    _default_ascending = False
    _searchable_fields = ["strain", "seedbank", "notes", "medium", "genes"]
    _legend_columns = [
        (lang.LEGEND_GENES, 0.1, "center"),
        (lang.LEGEND_PLANT, 0.5, "left"),
        (lang.LEGEND_MEDIUM, 0.10, "center"),
        (lang.LEGEND_LAST_WATER, 0.11, "center"),
        (lang.LEGEND_NEXT_WATER, 0.13, "center"),
        (lang.LEGEND_FLOWER, 0.14, "center"),
        (lang.LEGEND_HARVEST, 0.14, "center"),
    ]
    _list_widget_class = PlantListView

    def __init__(self, **kwargs):
        self._header_buttons = [
            (lang.VIEW_GARDENS, ButtonYellow, self.on_garden_exit, 0.1),
            (lang.OPTIONS, ButtonYellow, self.on_options, 0.1),
            (lang.EXIT_APP, ButtonRed, self.on_exit_app, 0.1),
        ]
        self._footer_buttons = [
            (lang.ADD_PLANT, ButtonGreen, on_plant_seed, None, 0.8),
            (lang.VIEW_SELECTED_PLANT, ButtonYellow, self.on_details_button, None, None),
            (lang.DELETE_SELECTED_PLANT, ButtonRed, self.on_delete_pressed, None, None),
        ]
        super().__init__(**kwargs)
        self.refresh_plants()

    # -- Navigation callbacks --------------------------------------------------

    def on_delete_pressed(self, instance):
        go_to_are_you_sure(lang.MSG_CONFIRM_DELETE_PLANT,
                           lambda *_: self.on_delete_selected())

    def on_options(self, instance):
        go_to_settings()

    def on_garden_exit(self, instance):
        go_to_select_garden()

    def on_exit_app(self, instance):
        go_to_are_you_sure(lang.MSG_CONFIRM_EXIT, lambda *_: sys.exit(0))

    # -- Data ------------------------------------------------------------------

    def refresh_plants(self):
        app = App.get_running_app()
        garden_id = getattr(app, 'current_garden_id', None)
        plants = PlantRepository.list_for_garden(garden_id) if garden_id else []
        today = date.today()
        index = IndexRepository.get_all()

        data = []
        for p in plants:
            if not isinstance(p, dict):
                continue
            plant_id = p.get("id")
            name = p.get("seedbank") or p.get("name", "")
            strain = p.get("strain", "")
            notes = p.get("notes", "")
            genes = p.get("genes", "")
            date_planted = p.get("date_planted", "")

            idx_entry = index.get(str(plant_id), {}) if plant_id else {}
            last_event_ts = idx_entry.get("last_event_ts") or ""
            if date_planted and date_planted > last_event_ts:
                last_event_ts = date_planted
            last_event_ts = last_event_ts or None

            last_watering = get_difference_days(today, last_event_ts) if last_event_ts else None
            if last_watering is None:
                last_watering = lang.DASH
            else:
                last_watering = str(last_watering)
            next_watering = lang.DASH
            flower_status = lang.DASH
            harvest_status = lang.DASH

            dt_str = p.get("date_planted")
            base_f = p.get("days_to_flower")
            try:
                base_f = int(base_f) if base_f is not None else 0
            except (ValueError, TypeError):
                base_f = 0
            penalty = int(p.get("penalty", 0) or 0)
            est_f = base_f + 14 + penalty
            est_h = est_f * 2
            if dt_str and est_h:
                try:
                    y, m, d = map(int, dt_str.split("-"))
                    planted = date(y, m, d)
                    days_since = (today - planted).days
                    days_left = est_h - days_since
                    if days_left >= 0:
                        harvest_status = f"{days_left}"
                    else:
                        harvest_status = lang.STATUS_HARVESTED
                except Exception:
                    harvest_status = f"{est_h}"

            if dt_str and est_f:
                try:
                    y, m, d = map(int, dt_str.split("-"))
                    planted = date(y, m, d)
                    days_since = (today - planted).days
                    days_left = est_f - days_since
                    if days_left > 0:
                        flower_status = f"{days_left}"
                    elif days_left <= 0 and harvest_status != lang.STATUS_HARVESTED:
                        flower_status = lang.STATUS_FLOWERING
                    elif days_left <= 0 and harvest_status == lang.STATUS_HARVESTED:
                        flower_status = lang.STATUS_HARVESTED
                except Exception:
                    flower_status = f"{est_f}"
            medium = p.get("medium")
            stage = p.get("stage", "")

            if stage == "harvested":
                harvest_status = lang.STATUS_HARVESTED
                flower_status = lang.STATUS_HARVESTED
            elif stage == "flowering":
                if flower_status not in (lang.STATUS_FLOWERING, lang.STATUS_HARVESTED):
                    flower_status = lang.STATUS_FLOWERING

            data.append({
                "id": plant_id,
                "genes": genes,
                "seedbank": name,
                "strain": strain,
                "notes": notes,
                "medium": medium,
                "last_watering": last_watering,
                "next_watering": next_watering,
                "flower_status": flower_status,
                "harvest_status": harvest_status,
                "date_planted": date_planted,
                "last_event_ts": last_event_ts or "",
            })

        self._all_items = data
        self._apply_filters()

    def _is_active(self, item):
        return item.get("harvest_status") != lang.STATUS_HARVESTED

    # -- Selection & actions ---------------------------------------------------

    # Convenience aliases that match the old API used by button bindings
    def get_selected_plant(self):
        return self.get_selected_item()

    def on_view_selected(self, instance):
        plant = self.get_selected_plant()
        if plant is None:
            print("No plant selected")
            return
        print("Selected plant:", plant)

    def on_delete_selected(self, *args):
        idx = self.get_selected_index()
        if idx is None:
            print("No plant selected to delete")
            return

        selected = self.list_widget.data[idx]
        plant_id = selected.get("id")

        app = App.get_running_app()
        garden_id = getattr(app, 'current_garden_id', None)

        if plant_id and garden_id:
            PlantRepository.remove(garden_id, plant_id)

        self.list_widget.data.pop(idx)

        lm = self.list_widget.layout_manager
        if lm and idx in lm.selected_nodes:
            lm.deselect_node(idx)

        app.screen.current = "garden_view"

    def on_details_button(self, *args):
        plant = self.get_selected_plant()
        if not plant:
            return
        go_to_plant_details(None, plant)
