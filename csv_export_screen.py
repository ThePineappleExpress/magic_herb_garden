"""csv_export_screen.py - Export selected gardens to a single flat CSV file."""

import logging
from datetime import date
from pathlib import Path

import pandas as pd

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from boxes import ContentBox, ItemBox, SpacerBox, WrapperBox
from buttons import ButtonGreen, ButtonRed, ButtonYellow
from labels import FieldLabel, TitleLabel
from screens import BaseScreen
from ui_builders import create_initial_layout
from data import GardenRepository, EventRepository
import lang

LOG = logging.getLogger(__name__)

CSV_EXT = ".csv"

# ---------------------------------------------------------------------------
# Flat CSV column definitions
# ---------------------------------------------------------------------------
# Column order rationale:
#   1. Human-readable identifiers first  (garden name, strain, dates, event info)
#   2. Measurements grouped by topic     (watering → nutrients → plant obs → env)
#   3. Garden setup / context            (light, location)
#   4. Opaque UUIDs last                 (useful for joins but noisy to read)
# ---------------------------------------------------------------------------
CSV_COLUMNS = [
    # -- Core identifiers (human-readable) ------------------------------------
    "garden_name",
    "plant_strain",
    "plant_seedbank",
    "plant_date_planted",
    "plant_stage",
    "event_ts",
    "event_type",
    "event_notes",
    # -- Watering metrics -----------------------------------------------------
    "volume_l",
    "water_temp_c",
    "ph",
    "ppm",
    # -- Feeding / nutrients --------------------------------------------------
    "feeding_veg",
    "feeding_root",
    "feeding_soil",
    "feeding_vit",
    "feeding_flower",
    "feeding_tops",
    "feeding_calmag",
    "feeding_myco_trico",
    # -- Plant observations ---------------------------------------------------
    "plant_height",
    "num_nodes",
    "node_spacing",
    "main_stem_number",
    "leaf_color",
    "leaf_morphology",
    # -- Environment ----------------------------------------------------------
    "air_temp_c",
    "rh_percent",
    "vpd_kpa",
    "ppfd",
    "soil_moisture",
    "soil_ph",
    "light_schedule",
    # -- Garden setup / context -----------------------------------------------
    "garden_type",
    "garden_light_type",
    "garden_light_wattage",
    "garden_light_schedule_on",
    "garden_light_schedule_off",
    "garden_location",
    "plant_location",
    "plant_status",
    # -- IDs (useful for programmatic joins, noisy for humans) ----------------
    "garden_id",
    "plant_id",
    "event_id",
]


def _garden_base_row(garden: dict) -> dict:
    """Extract garden-level fields into a flat dict."""
    schedule = garden.get("light_schedule") or []
    return {
        "garden_id": garden.get("id", ""),
        "garden_name": garden.get("name", ""),
        "garden_type": garden.get("type", ""),
        "garden_light_type": garden.get("light_type", ""),
        "garden_light_wattage": garden.get("light_wattage", ""),
        "garden_light_schedule_on": schedule[0] if len(schedule) > 0 else "",
        "garden_light_schedule_off": schedule[1] if len(schedule) > 1 else "",
        "garden_location": garden.get("location", ""),
    }


def _plant_base_row(plant: dict) -> dict:
    """Extract plant-level fields into a flat dict."""
    return {
        "plant_id": plant.get("id", ""),
        "plant_strain": plant.get("strain", ""),
        "plant_seedbank": plant.get("seedbank", ""),
        "plant_date_planted": plant.get("date_planted", ""),
        "plant_location": plant.get("location", ""),
        "plant_status": plant.get("status", ""),
    }


def _event_row(event: dict) -> dict:
    """Flatten a single event dict into CSV columns."""
    feeding = event.get("feeding") or {}
    plant_obs = event.get("plant") or {}
    env = event.get("environment") or {}

    return {
        "event_id": event.get("id", ""),
        "event_ts": event.get("ts", ""),
        "event_type": event.get("type", ""),
        "event_notes": event.get("notes", ""),
        # watering / feeding metrics
        "volume_l": event.get("volume_l", ""),
        "water_temp_c": event.get("water_temp_c", ""),
        "ph": event.get("ph", ""),
        "ppm": event.get("ppm", ""),
        # nutrients
        "feeding_grow_mix": feeding.get("grow_mix", ""),
        "feeding_root_mix": feeding.get("root_mix", ""),
        "feeding_bloom_mix": feeding.get("bloom_mix", ""),
        "feeding_bloom_boost": feeding.get("bloom_boost", ""),
        "feeding_soil_boost": feeding.get("soil_boost", ""),
        "feeding_vit_boost": feeding.get("vit_boost", ""),
        "feeding_calmag": feeding.get("CalMag", ""),
        "feeding_myco_trico": feeding.get("myco_trico", ""),
        # plant observations
        "plant_height": plant_obs.get("plant_height", ""),
        "num_nodes": plant_obs.get("num_nodes", ""),
        "node_spacing": plant_obs.get("node_spacing", ""),
        "main_stem_number": plant_obs.get("main_stem_number", ""),
        "leaf_color": plant_obs.get("leaf_color", ""),
        "leaf_morphology": plant_obs.get("leaf_morphology", ""),
        "plant_stage": plant_obs.get("stage", ""),
        # environment
        "air_temp_c": env.get("air_temp_c", ""),
        "rh_percent": env.get("rh_percent", ""),
        "vpd_kpa": env.get("vpd_kpa", ""),
        "ppfd": env.get("ppfd", ""),
        "soil_moisture": env.get("soil_moisture", ""),
        "soil_ph": env.get("soil_ph", ""),
        "light_schedule": env.get("light_schedule", ""),
    }


def write_gardens_csv(dest: Path, gardens_data: list) -> None:
    """Write *gardens_data* (list of {garden, events} dicts) to a CSV file at *dest*.

    Each row corresponds to a single event.  Plants with no logged events
    still get one row (blank event columns) so every plant is represented.
    Rows are sorted by garden name → plant date planted → event timestamp so
    that all events for a plant cluster together chronologically.
    """
    rows: list[dict] = []

    for entry in gardens_data:
        garden = entry.get("garden", {})
        events_map = entry.get("events", {})
        garden_row = _garden_base_row(garden)

        for plant in garden.get("plants", []):
            plant_row = _plant_base_row(plant)
            pid = plant.get("id")
            ev_data = events_map.get(pid) if pid else None
            events = ev_data.get("events", []) if ev_data else []

            if events:
                for event in events:
                    rows.append({**garden_row, **plant_row, **_event_row(event)})
            else:
                rows.append({**garden_row, **plant_row})

    # Sort: garden name → plant date planted (ISO string sort is correct) → event ts
    rows.sort(key=lambda r: (
        r.get("garden_name", ""),
        r.get("plant_date_planted", ""),
        r.get("event_ts", ""),
    ))

    df = pd.DataFrame(rows, columns=CSV_COLUMNS)
    df.to_csv(dest, index=False, encoding="utf-8")


# ---------------------------------------------------------------------------
# Screen
# ---------------------------------------------------------------------------

class CsvExportScreen(BaseScreen):

    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._origin_screen = "settings"

        app = App.get_running_app()
        title_text = lang.CSV_EXPORT_TITLE.format(color=TitleLabel().hex_color)
        screen_wrapper, layout = create_initial_layout(
            self, app, title_text=title_text, left_size=0.1,
            show_day_box=False, show_info_header=False,
        )

        layout.add_widget(WrapperBox(size_hint_y=0.5))

        # -- Garden checkbox scroll area ----------------------------------------
        scroll_container = BoxLayout(orientation="horizontal", size_hint_y=3.0)
        scroll_container.add_widget(SpacerBox(size_hint_x=0.3))
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self._checkbox_container = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=4, padding=(4, 4),
        )
        self._checkbox_container.bind(
            minimum_height=self._checkbox_container.setter("height")
        )
        scroll.add_widget(self._checkbox_container)
        scroll_container.add_widget(scroll)
        layout.add_widget(scroll_container)

        self._garden_checkboxes: list = []  # [(garden_id, CheckBox), …]

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Select-all / Deselect-all ------------------------------------------
        sel_row = ContentBox(orientation="horizontal")
        sel_row.add_widget(FieldLabel(text=lang.EXPORT_SELECT_GARDENS, size_hint_x=0.3))
        btns_box = ItemBox(orientation="horizontal")
        btn_select_all = ButtonYellow(text=lang.EXPORT_SELECT_ALL, size_hint_x=0.35)
        btn_select_all.bind(on_press=self._select_all)
        btn_deselect_all = ButtonYellow(text=lang.EXPORT_DESELECT_ALL, size_hint_x=0.35)
        btn_deselect_all.bind(on_press=self._deselect_all)
        btns_box.add_widget(btn_select_all)
        btns_box.add_widget(btn_deselect_all)
        sel_row.add_widget(btns_box)
        layout.add_widget(sel_row)

        layout.add_widget(SpacerBox(size_hint_y=0.04))

        # -- Action buttons -----------------------------------------------------
        button_row = WrapperBox(orientation="horizontal")

        export_btn_holder = ItemBox(orientation="horizontal")
        export_btn = ButtonGreen(text=lang.SETTINGS_EXPORT_CSV)
        export_btn.bind(on_press=self._on_export_pressed)
        export_btn_holder.add_widget(export_btn)
        button_row.add_widget(export_btn_holder)

        cancel_btn_holder = ItemBox(orientation="horizontal")
        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        cancel_btn.bind(on_press=self._on_cancel)
        cancel_btn_holder.add_widget(cancel_btn)
        button_row.add_widget(cancel_btn_holder)

        layout.add_widget(button_row)
        layout.add_widget(WrapperBox(size_hint_y=0.5))

        screen_wrapper.add_widget(layout)
        screen_wrapper.add_widget(SpacerBox(size_hint_x=0.1))

    # -- Lifecycle --------------------------------------------------------------

    def on_enter(self):
        super().on_enter()
        app = App.get_running_app()
        if app.previous_screen not in {"csv_export"}:
            self._origin_screen = app.previous_screen or "settings"
        self._rebuild_checkboxes()

    # -- Garden checkboxes ------------------------------------------------------

    def _rebuild_checkboxes(self):
        self._checkbox_container.clear_widgets()
        self._garden_checkboxes.clear()
        for garden in GardenRepository.list_all():
            gid = garden.get("id", "")
            name = garden.get("name", gid)
            row = BoxLayout(
                orientation="horizontal", size_hint_y=None, height=40, spacing=8,
            )
            cb = CheckBox(active=True, size_hint_x=None, width=40)
            lbl = FieldLabel(text=name)
            row.add_widget(cb)
            row.add_widget(lbl)
            self._checkbox_container.add_widget(row)
            self._garden_checkboxes.append((gid, cb))

    def _select_all(self, *_):
        for _, cb in self._garden_checkboxes:
            cb.active = True

    def _deselect_all(self, *_):
        for _, cb in self._garden_checkboxes:
            cb.active = False

    def _get_selected_ids(self) -> list:
        return [gid for gid, cb in self._garden_checkboxes if cb.active]

    # -- Export flow ------------------------------------------------------------

    def _on_export_pressed(self, instance):
        selected_ids = self._get_selected_ids()
        if not selected_ids:
            self._show_info_popup(lang.CSV_EXPORT_NO_GARDENS)
            return
        self._open_save_popup(selected_ids)

    def _open_save_popup(self, selected_ids: list):
        """Show a directory-chooser + filename popup before writing."""
        default_name = "export_" + date.today().strftime("%Y-%m-%d") + CSV_EXT

        from text_inputs import MedTextInput

        chooser = FileChooserListView(
            path=str(Path.home()),
            dirselect=True,
            filters=["!.*"],
        )
        popup_layout = BoxLayout(orientation="vertical", spacing=5, padding=10)
        popup_layout.add_widget(chooser)

        fn_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=8,
        )
        fn_label = FieldLabel(
            text=lang.CSV_EXPORT_FILENAME_LABEL, size_hint_x=None, width=160,
        )
        fn_input = MedTextInput(text=default_name)
        fn_row.add_widget(fn_label)
        fn_row.add_widget(fn_input)
        popup_layout.add_widget(fn_row)

        btn_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=10,
        )
        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        export_btn = ButtonGreen(text=lang.SETTINGS_EXPORT_CSV)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(export_btn)
        popup_layout.add_widget(btn_row)

        popup = Popup(
            title=lang.CSV_EXPORT_CHOOSE_LOCATION,
            content=popup_layout,
            size_hint=(0.75, 0.75),
        )
        cancel_btn.bind(on_press=popup.dismiss)
        export_btn.bind(
            on_press=lambda *_: self._do_export(chooser, fn_input, popup, selected_ids)
        )
        popup.open()

    def _do_export(self, chooser, fn_input, popup, selected_ids: list):
        filename = fn_input.text.strip()
        if not filename:
            return
        if not filename.endswith(CSV_EXT):
            filename += CSV_EXT

        directory = chooser.selection[0] if chooser.selection else chooser.path
        dest = Path(directory) / filename

        try:
            gardens_data = self._gather_data(selected_ids)
        except Exception:
            LOG.exception("Failed to gather export data")
            popup.dismiss()
            self._show_info_popup(f"{lang.CSV_EXPORT_ERROR} (gather failed)")
            return

        try:
            write_gardens_csv(dest, gardens_data)
        except Exception:
            LOG.exception("write_gardens_csv failed for %s", dest)
            popup.dismiss()
            self._show_info_popup(f"{lang.CSV_EXPORT_ERROR} {dest}")
            return

        popup.dismiss()
        self._show_info_popup(f"{lang.CSV_EXPORT_SUCCESS}\n{dest}")
        LOG.info("CSV exported %d garden(s) to %s", len(selected_ids), dest)

    def _gather_data(self, garden_ids: list) -> list:
        """Return [{garden: {...}, events: {plant_id: {...}}}, …] for CSV writing."""
        result = []
        for gid in garden_ids:
            garden = GardenRepository.get(gid)
            if not garden:
                LOG.warning("Garden %s not found during CSV export - skipping", gid)
                continue
            events_map = {}
            for plant in garden.get("plants", []):
                pid = plant.get("id")
                if pid:
                    ev = EventRepository.get(pid)
                    if ev:
                        events_map[pid] = ev
            result.append({"garden": garden, "events": events_map})
        return result

    # -- Info popup -------------------------------------------------------------

    def _show_info_popup(self, message: str):
        popup_layout = BoxLayout(orientation="vertical", spacing=8, padding=12)
        lbl = FieldLabel(text=str(message), halign="left", valign="top")
        popup_layout.add_widget(lbl)
        btn_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=10,
        )
        btn_row.add_widget(WrapperBox())
        ok_btn = ButtonGreen(text=lang.YES)
        ok_btn.size_hint_x = 0.3
        btn_row.add_widget(ok_btn)
        popup_layout.add_widget(btn_row)
        popup = Popup(
            title="",
            content=popup_layout,
            size_hint=(0.5, 0.35),
        )
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()

    # -- Navigation -------------------------------------------------------------

    def _on_cancel(self, instance):
        app = App.get_running_app()
        app.screen.current = getattr(self, "_origin_screen", "settings")
