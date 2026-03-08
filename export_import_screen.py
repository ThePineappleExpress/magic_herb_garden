"""export_import_screen.py - .weed file export and import screen."""

import logging
from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton

from boxes import ContentBox, ItemBox, SpacerBox, WrapperBox
from buttons import ButtonGreen, ButtonRed, ButtonYellow, PasswordEyeToggle
from data import GardenRepository, PlantRepository
from labels import FieldLabel, TitleLabel
from screens import BaseScreen
from text_inputs import MedTextInput
from ui_builders import create_initial_layout
from weed_format import (
    WEED_EXT,
    WeedCorrupted,
    WeedPasswordRequired,
    WeedWrongPassword,
    read_weed,
    write_weed,
)
import lang
import storage

LOG = logging.getLogger(__name__)


class ExportImportScreen(BaseScreen):

    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()

        title_text = lang.EXPORT_IMPORT_TITLE.format(color=TitleLabel().hex_color)
        screen_wrapper, layout = create_initial_layout(self, app, title_text=title_text, left_size=0.1, show_day_box=False, show_info_header=False)

        layout.add_widget(WrapperBox(size_hint_y=0.5))

        # -- Export type toggle --------------------------------------------------
        type_row = ContentBox(orientation="horizontal")
        type_row.add_widget(FieldLabel(text=lang.EXPORT_TYPE_LABEL, size_hint_x=0.3))
        type_box = ItemBox(orientation="horizontal")
        self.btn_safe = ToggleButton(text=lang.EXPORT_SAFE, group="weed_export_type", allow_no_selection=False, state="down")
        self.btn_open = ToggleButton(text=lang.EXPORT_OPEN, group="weed_export_type", allow_no_selection=False,)
        self.btn_safe.bind(state=lambda *_: self._update_pw_visibility())
        self.btn_open.bind(state=lambda *_: self._update_pw_visibility())
        type_box.add_widget(self.btn_safe)
        type_box.add_widget(self.btn_open)
        type_row.add_widget(type_box)
        layout.add_widget(type_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Garden checkbox scroll area ----------------------------------------
        scroll_container = BoxLayout(orientation="horizontal", size_hint_y=3.0)
        scroll_container.add_widget(SpacerBox(size_hint_x=0.3))
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self._checkbox_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=4, padding=(4, 4))
        self._checkbox_container.bind(minimum_height=self._checkbox_container.setter("height"))
        scroll.add_widget(self._checkbox_container)
        scroll_container.add_widget(scroll)
        layout.add_widget(scroll_container)

        self._garden_checkboxes = [] # [(garden_id, CheckBox), ...]

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Garden selection label + Select-all / Deselect-all buttons ---------
        sel_row = ContentBox(orientation="horizontal")
        sel_row.add_widget(FieldLabel(text=lang.EXPORT_SELECT_GARDENS, size_hint_x=0.3))
        btns_box = ItemBox(orientation="horizontal")
        btn_select_all = ButtonYellow(text=lang.EXPORT_SELECT_ALL, size_hint_x=0.35)
        btn_select_all.bind(on_press=self._select_all_gardens)
        btn_deselect_all = ButtonYellow(text=lang.EXPORT_DESELECT_ALL, size_hint_x=0.35)
        btn_deselect_all.bind(on_press=self._deselect_all_gardens)
        btns_box.add_widget(btn_select_all)
        btns_box.add_widget(btn_deselect_all)
        sel_row.add_widget(btns_box)
        layout.add_widget(sel_row)

        layout.add_widget(SpacerBox(size_hint_y=0.01))

        # -- Export password -----------------------------------------------------
        self._pw_row = ContentBox(orientation="horizontal")
        self._pw_row.add_widget(FieldLabel(text=lang.EXPORT_PASSWORD, size_hint_x=0.3))
        pw_input_row = ItemBox(orientation="horizontal")
        self.export_pw_input = MedTextInput(
            hint_text=lang.EXPORT_PASSWORD, password=True
        )
        pw_input_row.add_widget(self.export_pw_input)
        self._export_pw_eye = PasswordEyeToggle(text_input=self.export_pw_input)
        pw_input_row.add_widget(self._export_pw_eye)
        self._pw_row.add_widget(pw_input_row)
        layout.add_widget(self._pw_row)

        layout.add_widget(SpacerBox(size_hint_y=0.01))

        # -- Export password confirm ----------------------------------------------
        self._confirm_pw_row = ContentBox(orientation="horizontal")
        self._confirm_pw_row.add_widget(
            FieldLabel(text=lang.EXPORT_PASSWORD_CONFIRM, size_hint_x=0.3)
        )
        confirm_input_row = ItemBox(orientation="horizontal")
        self.export_pw_confirm_input = MedTextInput(
            hint_text=lang.EXPORT_PASSWORD_CONFIRM, password=True
        )
        confirm_input_row.add_widget(self.export_pw_confirm_input)
        self._export_confirm_eye = PasswordEyeToggle(
            text_input=self.export_pw_confirm_input
        )
        confirm_input_row.add_widget(self._export_confirm_eye)
        self._confirm_pw_row.add_widget(confirm_input_row)
        layout.add_widget(self._confirm_pw_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Buttons wrapper -----------------------------------------------------

        button_row = WrapperBox(orientation="horizontal")
                

        # -- Export button -------------------------------------------------------
        export_btn_holder = ItemBox(orientation="horizontal")
        export_btn = ButtonGreen(text=lang.BUTTON_EXPORT)
        export_btn.bind(on_press=self._on_export_pressed)
        export_btn_holder.add_widget(export_btn)
        button_row.add_widget(export_btn_holder)

        # -- Import button --------------------------------------------------------
        import_btn_holder = ItemBox(orientation="horizontal")
        import_btn = ButtonYellow(text=lang.BUTTON_IMPORT)
        import_btn.bind(on_press=self._on_import_pressed)
        import_btn_holder.add_widget(import_btn)
        button_row.add_widget(import_btn_holder)

        # -- Cancel button --------------------------------------------------------
        cancel_btn_holder = ItemBox(orientation="horizontal")
        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        cancel_btn.bind(on_press=self._on_cancel)
        cancel_btn_holder.add_widget(cancel_btn)
        button_row.add_widget(cancel_btn_holder)

        layout.add_widget(button_row)

        layout.add_widget(WrapperBox(size_hint_y=0.5))

        screen_wrapper.add_widget(layout)
        screen_wrapper.add_widget(SpacerBox(size_hint_x=0.1))

        self._update_pw_visibility()

    # -- on_enter ---------------------------------------------------------------

    def on_enter(self):
        # Capture entry origin, but don't overwrite it when returning from our
        # own sub-screens (are_you_sure) which set previous_screen to
        # "export_import". This keeps cancel working after a round-trip.
        app = App.get_running_app()
        _own_family = {"export_import", "are_you_sure"}
        if app.previous_screen not in _own_family:
            self._origin_screen = app.previous_screen or "settings"

        self._rebuild_checkboxes()
        self.export_pw_input.text = ""
        self.export_pw_confirm_input.text = ""
        self._export_pw_eye.reset()
        self._export_confirm_eye.reset()
        self.btn_safe.state = "down"
        self.btn_open.state = "normal"
        self._update_pw_visibility()

    # -- Garden checkboxes ------------------------------------------------------

    def _rebuild_checkboxes(self):
        """Reload garden list from storage and rebuild the checkbox rows."""
        self._checkbox_container.clear_widgets()
        self._garden_checkboxes.clear()
        gardens = storage.load_gardens()
        for garden in gardens:
            gid = garden.get("id", "")
            name = garden.get("name", gid)
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=8)
            cb = CheckBox(active=True, size_hint_x=None, width=40)
            lbl = FieldLabel(text=name)
            row.add_widget(cb)
            row.add_widget(lbl)
            self._checkbox_container.add_widget(row)
            self._garden_checkboxes.append((gid, cb))

    def _select_all_gardens(self, *args):
        for _, cb in self._garden_checkboxes:
            cb.active = True

    def _deselect_all_gardens(self, *args):
        for _, cb in self._garden_checkboxes:
            cb.active = False

    def _get_selected_garden_ids(self):
        return [gid for gid, cb in self._garden_checkboxes if cb.active]

    # -- Password row visibility -------------------------------------------------

    def _update_pw_visibility(self, *args):
        encrypted = self.btn_safe.state == "down"
        for row in (self._pw_row, self._confirm_pw_row):
            row.opacity = 1.0 if encrypted else 0.0
            row.disabled = not encrypted

    # -- Export flow -------------------------------------------------------------

    def _on_export_pressed(self, instance):
        selected_ids = self._get_selected_garden_ids()
        if not selected_ids:
            self._show_info_popup(lang.EXPORT_NO_GARDENS_SELECTED)
            return

        encrypted = self.btn_safe.state == "down"
        export_password = None
        if encrypted:
            pw = self.export_pw_input.text.strip()
            pw_confirm = self.export_pw_confirm_input.text.strip()
            if not pw:
                from effects import shake_and_flash
                shake_and_flash(self.export_pw_input)
                return
            if len(pw) < 8:
                from effects import shake_and_flash
                shake_and_flash(self.export_pw_input)
                return
            if pw != pw_confirm:
                from effects import shake_and_flash
                shake_and_flash(self.export_pw_input)
                shake_and_flash(self.export_pw_confirm_input)
                return
            export_password = pw

        self._open_export_save_popup(selected_ids, export_password)

    def _open_export_save_popup(self, selected_ids, export_password):
        """Show a directory chooser + filename field popup before writing."""
        default_name = "export_" + date.today().strftime("%Y-%m-%d") + WEED_EXT
        chooser = FileChooserListView(
            path=str(Path.home()),
            dirselect=True,
            filters=["!.*"],
        )
        popup_layout = BoxLayout(orientation="vertical", spacing=5, padding=10)
        popup_layout.add_widget(chooser)

        fn_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=8
        )
        fn_label = FieldLabel(
            text=lang.EXPORT_FILENAME_LABEL, size_hint_x=None, width=160
        )
        fn_input = MedTextInput(text=default_name)
        fn_row.add_widget(fn_label)
        fn_row.add_widget(fn_input)
        popup_layout.add_widget(fn_row)

        btn_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=10
        )
        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        export_btn = ButtonGreen(text=lang.BUTTON_EXPORT)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(export_btn)
        popup_layout.add_widget(btn_row)

        popup = Popup(
            title=lang.EXPORT_CHOOSE_LOCATION,
            content=popup_layout,
            size_hint=(0.75, 0.75),
        )
        cancel_btn.bind(on_press=popup.dismiss)
        export_btn.bind(
            on_press=lambda *_: self._do_export(
                chooser, fn_input, popup, selected_ids, export_password
            )
        )
        popup.open()

    def _do_export(self, chooser, fn_input, popup, selected_ids, export_password):
        """Collect data, write the .weed file, close popup, and report result."""
        filename = fn_input.text.strip()
        if not filename:
            return
        if not filename.endswith(WEED_EXT):
            filename += WEED_EXT

        if chooser.selection:
            directory = chooser.selection[0]
        else:
            directory = chooser.path
        dest = Path(directory) / filename

        try:
            gardens_data = self._gather_export_data(selected_ids)
        except Exception:
            LOG.exception("Failed to gather export data")
            popup.dismiss()
            self._show_info_popup(f"{lang.EXPORT_ERROR} (gather failed)")
            return

        try:
            write_weed(dest, gardens_data, export_password=export_password)
        except Exception:
            LOG.exception("write_weed failed for %s", dest)
            popup.dismiss()
            self._show_info_popup(f"{lang.EXPORT_ERROR} {dest}")
            return

        popup.dismiss()
        self._show_info_popup(f"{lang.EXPORT_SUCCESS}\n{dest}")
        LOG.info("Exported %d garden(s) to %s", len(selected_ids), dest)

    def _gather_export_data(self, garden_ids):
        """Return [{garden: {...}, events: {plant_id: {...}}}, ...] for export."""
        result = []
        for gid in garden_ids:
            garden = storage.load_garden(gid)
            if not garden:
                LOG.warning("Garden %s not found during export - skipping", gid)
                continue
            events_map = {}
            for plant in garden.get("plants", []):
                pid = plant.get("id")
                if pid:
                    ev = storage.load_plant_events(pid)
                    if ev:
                        events_map[pid] = ev
            result.append({"garden": garden, "events": events_map})
        return result

    # -- Import flow -------------------------------------------------------------

    def _on_import_pressed(self, instance):
        self._open_import_chooser_popup()

    def _open_import_chooser_popup(self):
        """Show a file chooser popup filtered to *.weed files."""
        chooser = FileChooserListView(
            path=str(Path.home()),
            dirselect=False,
            filters=["*.weed", "!.*"],
        )
        popup_layout = BoxLayout(orientation="vertical", spacing=5, padding=10)
        popup_layout.add_widget(chooser)

        btn_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=10
        )
        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        import_btn = ButtonGreen(text=lang.BUTTON_IMPORT)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(import_btn)
        popup_layout.add_widget(btn_row)

        popup = Popup(
            title=lang.IMPORT_CHOOSE_FILE,
            content=popup_layout,
            size_hint=(0.75, 0.75),
        )
        cancel_btn.bind(on_press=popup.dismiss)
        import_btn.bind(
            on_press=lambda *_: self._on_import_file_selected(chooser, popup)
        )
        popup.open()

    def _on_import_file_selected(self, chooser, popup):
        if not chooser.selection:
            return
        file_path = chooser.selection[0]
        popup.dismiss()
        self._try_import(file_path, export_password=None)

    def _try_import(self, file_path, export_password=None):
        """Attempt to read the .weed file and proceed through the import flow."""
        try:
            data = read_weed(file_path, export_password=export_password)
        except WeedPasswordRequired:
            self._open_import_password_popup(file_path)
            return
        except WeedWrongPassword:
            self._show_info_popup(lang.IMPORT_ERROR_WRONG_PW)
            return
        except WeedCorrupted:
            self._show_info_popup(lang.IMPORT_ERROR_CORRUPT)
            return
        except Exception:
            LOG.exception("Unexpected error reading %s", file_path)
            self._show_info_popup(lang.IMPORT_ERROR_CORRUPT)
            return

        # Check for conflicting garden IDs
        existing_ids = {g.get("id") for g in storage.load_gardens() if g.get("id")}
        import_ids = [g.get("id") for g in data.get("gardens", []) if g.get("id")]
        conflicts = [gid for gid in import_ids if gid in existing_ids]

        if conflicts:
            n = len(conflicts)
            app = App.get_running_app()
            are_you_sure = app.screen.get_screen("are_you_sure")
            are_you_sure.prompt_text = lang.IMPORT_CONFLICT_WARNING.format(n=n)
            are_you_sure.confirm_callback = lambda *_: self._do_import(data)
            app.previous_screen = "export_import"
            app.screen.current = "are_you_sure"
        else:
            self._do_import(data)

    def _open_import_password_popup(self, file_path):
        """Prompt for the export password when the .weed file is encrypted."""
        popup_layout = BoxLayout(orientation="vertical", spacing=8, padding=10)
        popup_layout.add_widget(
            FieldLabel(text=lang.IMPORT_PASSWORD_PROMPT, size_hint_y=None, height=60)
        )
        pw_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=4
        )
        pw_input = MedTextInput(hint_text=lang.EXPORT_PASSWORD, password=True)
        eye = PasswordEyeToggle(text_input=pw_input)
        pw_row.add_widget(pw_input)
        pw_row.add_widget(eye)
        popup_layout.add_widget(pw_row)

        btn_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=10
        )
        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        ok_btn = ButtonGreen(text=lang.YES)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(ok_btn)
        popup_layout.add_widget(btn_row)

        popup = Popup(
            title=lang.IMPORT_PASSWORD_PROMPT,
            content=popup_layout,
            size_hint=(0.5, 0.4),
        )
        cancel_btn.bind(on_press=popup.dismiss)

        def _on_ok(*args):
            pw = pw_input.text.strip()
            popup.dismiss()
            self._try_import(file_path, export_password=pw)

        ok_btn.bind(on_press=_on_ok)
        popup.open()

    def _do_import(self, data):
        """Write imported gardens and event files; invalidate repository caches."""
        gardens = data.get("gardens", [])
        events_by_plant = data.get("events", {})
        imported_gardens = 0
        imported_events = 0

        for garden in gardens:
            gid = garden.get("id")
            if not gid:
                continue
            if storage.save_garden(garden):
                imported_gardens += 1
            for plant in garden.get("plants", []):
                pid = plant.get("id")
                if pid:
                    ev = events_by_plant.get(pid)
                    if ev and storage.save_plant_events(pid, ev):
                        imported_events += 1

        # Invalidate in-memory repository caches so next read sees fresh data
        PlantRepository._plants_cache.clear()
        GardenRepository._gardens_cache = None

        # Navigate back to the export/import screen before showing the popup so
        # we don't leave the user on are_you_sure with a stale confirm_callback.
        app = App.get_running_app()
        if app.screen.current != "export_import":
            app.previous_screen = "export_import"
            app.screen.current = "export_import"

        self._rebuild_checkboxes()

        msg = lang.IMPORT_SUCCESS.format(
            gardens=imported_gardens, events=imported_events
        )
        self._show_info_popup(msg)
        LOG.info(
            "Imported %d gardens and %d event files", imported_gardens, imported_events
        )

    # -- Info popup --------------------------------------------------------------

    def _show_info_popup(self, message):
        popup_layout = BoxLayout(orientation="vertical", spacing=8, padding=12)
        lbl = FieldLabel(text=str(message), halign="left", valign="top")
        popup_layout.add_widget(lbl)
        btn_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=48, spacing=10
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

    # -- Navigation --------------------------------------------------------------

    def _on_cancel(self, instance):
        app = App.get_running_app()
        app.screen.current = getattr(self, "_origin_screen", "settings")
