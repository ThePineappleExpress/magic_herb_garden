"""settings_screen.py - Application settings screen.

Language, theme, shader, password, database path, export/import navigation.
"""

import logging

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.spinner import Spinner

from boxes import ContentBox, ItemBox, SpacerBox, WrapperBox
from buttons import ButtonGreen, ButtonRed, ButtonYellow, PasswordEyeToggle
from effects import shake_and_flash
from helpers import derive_encryption_key, hash_password, verify_password
from labels import FieldLabel, TitleLabel
from screens import BaseScreen
from text_inputs import MedTextInput
from ui_builders import create_initial_layout
import lang
import storage

LOG = logging.getLogger(__name__)


class SettingsScreen(BaseScreen):

    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = App.get_running_app()
        title_text = lang.SCREEN_SETTINGS_TITLE.format(color=TitleLabel().hex_color)
        screen_wrapper, layout = create_initial_layout(
            self, app, title_text=title_text, left_size=0.1,
            show_day_box=False, show_info_header=False,
        )

        layout.add_widget(WrapperBox(size_hint_y=0.3))

        # -- Language -----------------------------------------------------------
        lang_row = ContentBox(orientation="horizontal")
        lang_row.add_widget(FieldLabel(text=lang.SETTINGS_LANGUAGE, size_hint_x=0.3))
        lang_input = ItemBox(orientation="horizontal")
        self.lang_spinner = Spinner(
            text="English",
            values=[],
            size_hint_x=0.5,
        )
        self.lang_spinner.bind(text=self._on_language_changed)
        lang_input.add_widget(self.lang_spinner)
        lang_input.add_widget(FieldLabel(text=lang.SETTINGS_LANGUAGE_RESTART, size_hint_x=0.5))
        lang_row.add_widget(lang_input)
        layout.add_widget(lang_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Theme --------------------------------------------------------------
        theme_row = ContentBox(orientation="horizontal")
        theme_row.add_widget(FieldLabel(text=lang.SETTINGS_THEME, size_hint_x=0.3))
        theme_input = ItemBox(orientation="horizontal")
        self.theme_spinner = Spinner(text="dark", values=[], size_hint_x=0.5)
        self.theme_spinner.bind(text=self._on_theme_changed)
        theme_input.add_widget(self.theme_spinner)
        theme_row.add_widget(theme_input)
        layout.add_widget(theme_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Shader toggle ------------------------------------------------------
        shader_row = ContentBox(orientation="horizontal")
        shader_row.add_widget(FieldLabel(text=lang.SETTINGS_SHADER_TOGGLE, size_hint_x=0.3))
        shader_input = ItemBox(orientation="horizontal")
        self.shader_spinner = Spinner(
            text=lang.SETTINGS_SHADER_ON,
            values=[lang.SETTINGS_SHADER_ON, lang.SETTINGS_SHADER_OFF],
            size_hint_x=0.3,
        )
        shader_input.add_widget(self.shader_spinner)

        self.shader_style_spinner = Spinner(text="smoke", values=[], size_hint_x=0.3)
        shader_input.add_widget(self.shader_style_spinner)

        reload_btn = ButtonYellow(text=lang.SETTINGS_SHADER_RELOAD, size_hint_x=0.2)
        reload_btn.bind(on_press=self._on_shader_reload)
        shader_input.add_widget(reload_btn)
        shader_row.add_widget(shader_input)
        layout.add_widget(shader_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Current password ---------------------------------------------------
        cur_pw_row = ContentBox(orientation="horizontal")
        cur_pw_row.add_widget(FieldLabel(text=lang.SETTINGS_CURRENT_PASSWORD, size_hint_x=0.3))
        cur_pw_input = ItemBox(orientation="horizontal")
        self.cur_pw = MedTextInput(hint_text=lang.HINT_CURRENT_PASSWORD, password=True)
        cur_pw_input.add_widget(self.cur_pw)
        self._cur_eye = PasswordEyeToggle(text_input=self.cur_pw)
        cur_pw_input.add_widget(self._cur_eye)
        self.remove_pw_btn = ButtonRed(text=lang.SETTINGS_REMOVE_PASSWORD, size_hint_x=0.25)
        self.remove_pw_btn.bind(on_press=self._on_remove_password)
        cur_pw_input.add_widget(self.remove_pw_btn)
        cur_pw_row.add_widget(cur_pw_input)
        layout.add_widget(cur_pw_row)

        layout.add_widget(SpacerBox(size_hint_y=0.01))

        # -- New password -------------------------------------------------------
        new_pw_row = ContentBox(orientation="horizontal")
        new_pw_row.add_widget(FieldLabel(text=lang.SETTINGS_PASSWORD, size_hint_x=0.3))
        new_pw_input = ItemBox(orientation="horizontal")
        self.new_pw = MedTextInput(hint_text=lang.HINT_ENTER_PASSWORD, password=True)
        new_pw_input.add_widget(self.new_pw)
        self._new_eye = PasswordEyeToggle(text_input=self.new_pw)
        new_pw_input.add_widget(self._new_eye)
        new_pw_row.add_widget(new_pw_input)
        layout.add_widget(new_pw_row)

        layout.add_widget(SpacerBox(size_hint_y=0.01))

        # -- Confirm password ---------------------------------------------------
        conf_pw_row = ContentBox(orientation="horizontal")
        conf_pw_row.add_widget(FieldLabel(text=lang.SETTINGS_PASSWORD_CONFIRM, size_hint_x=0.3))
        conf_pw_input = ItemBox(orientation="horizontal")
        self.confirm_pw = MedTextInput(hint_text=lang.HINT_CONFIRM_PASSWORD, password=True)
        conf_pw_input.add_widget(self.confirm_pw)
        self._conf_eye = PasswordEyeToggle(text_input=self.confirm_pw)
        conf_pw_input.add_widget(self._conf_eye)
        conf_pw_row.add_widget(conf_pw_input)
        layout.add_widget(conf_pw_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # -- Database path ------------------------------------------------------
        db_row = ContentBox(orientation="horizontal")
        db_row.add_widget(FieldLabel(text=lang.SETTINGS_DB_PATH, size_hint_x=0.3))
        db_input = ItemBox(orientation="horizontal")
        self.db_path_input = MedTextInput(hint_text=lang.HINT_DB_PATH)
        db_input.add_widget(self.db_path_input)
        db_select_btn = ButtonYellow(text=lang.SETTINGS_SELECT_FOLDER, size_hint_x=0.15)
        db_input.add_widget(db_select_btn)
        db_row.add_widget(db_input)
        layout.add_widget(db_row)

        layout.add_widget(SpacerBox(size_hint_y=0.04))

        # -- Action buttons -----------------------------------------------------
        btn_row = WrapperBox(orientation="horizontal")

        save_holder = ItemBox(orientation="horizontal")
        save_btn = ButtonGreen(text=lang.BUTTON_SAVE)
        save_btn.bind(on_press=self._on_save)
        save_holder.add_widget(save_btn)
        btn_row.add_widget(save_holder)

        export_holder = ItemBox(orientation="horizontal")
        export_btn = ButtonYellow(text=lang.SETTINGS_EXPORT_IMPORT)
        export_btn.bind(on_press=self._on_export_import)
        export_holder.add_widget(export_btn)
        btn_row.add_widget(export_holder)

        csv_holder = ItemBox(orientation="horizontal")
        csv_btn = ButtonYellow(text=lang.SETTINGS_EXPORT_CSV)
        csv_btn.bind(on_press=self._on_csv_export)
        csv_holder.add_widget(csv_btn)
        btn_row.add_widget(csv_holder)

        back_holder = ItemBox(orientation="horizontal")
        back_btn = ButtonRed(text=lang.BACK)
        back_btn.bind(on_press=self._on_back)
        back_holder.add_widget(back_btn)
        btn_row.add_widget(back_holder)

        layout.add_widget(btn_row)
        layout.add_widget(WrapperBox(size_hint_y=0.3))

        screen_wrapper.add_widget(layout)
        screen_wrapper.add_widget(SpacerBox(size_hint_x=0.1))

    # -- Lifecycle --------------------------------------------------------------

    def on_enter(self):
        settings = storage.load_settings()

        # Populate language spinner
        try:
            from bin.lang import get_available_languages
            self.lang_spinner.values = get_available_languages()
        except Exception:
            self.lang_spinner.values = ["English"]
        current_lang = settings.get("language", "english").capitalize()
        if current_lang in self.lang_spinner.values:
            self.lang_spinner.text = current_lang

        # Populate theme spinner
        try:
            from bin.themes import get_available_themes
            self.theme_spinner.values = get_available_themes()
        except Exception:
            self.theme_spinner.values = ["dark"]
        current_theme = settings.get("theme", "dark")
        if current_theme in self.theme_spinner.values:
            self.theme_spinner.text = current_theme

        # Populate shader spinner
        try:
            from bin.shaders import get_available_shaders
            self.shader_style_spinner.values = get_available_shaders()
        except Exception:
            self.shader_style_spinner.values = ["smoke"]
        current_shader = settings.get("shader", "smoke")
        if current_shader in self.shader_style_spinner.values:
            self.shader_style_spinner.text = current_shader

        shader_on = settings.get("shader_enabled", True)
        self.shader_spinner.text = lang.SETTINGS_SHADER_ON if shader_on else lang.SETTINGS_SHADER_OFF

        # Password fields
        has_pw = bool(settings.get("password"))
        self.cur_pw.text = ""
        self.new_pw.text = ""
        self.confirm_pw.text = ""
        self.cur_pw.hint_text = lang.HINT_CURRENT_PASSWORD if has_pw else lang.HINT_NO_PASSWORD_SET
        self.cur_pw.disabled = not has_pw
        self.remove_pw_btn.disabled = not has_pw
        self._cur_eye.reset()
        self._new_eye.reset()
        self._conf_eye.reset()

        # DB path
        self.db_path_input.text = settings.get("db_path", "")

    # -- Callbacks --------------------------------------------------------------

    def _on_language_changed(self, spinner, text):
        pass  # Applied on save

    def _on_theme_changed(self, spinner, text):
        pass  # Applied on save

    def _on_shader_reload(self, *args):
        app = App.get_running_app()
        settings = storage.load_settings()
        settings["shader"] = self.shader_style_spinner.text
        settings["shader_enabled"] = self.shader_spinner.text == lang.SETTINGS_SHADER_ON
        storage.save_settings(settings)

    def _on_save(self, *args):
        settings = storage.load_settings()

        # Language
        settings["language"] = self.lang_spinner.text.lower()

        # Theme
        settings["theme"] = self.theme_spinner.text

        # Shader
        settings["shader"] = self.shader_style_spinner.text
        settings["shader_enabled"] = self.shader_spinner.text == lang.SETTINGS_SHADER_ON

        # Password change
        new_pw = self.new_pw.text.strip()
        confirm_pw = self.confirm_pw.text.strip()
        has_existing_pw = bool(settings.get("password"))

        if new_pw:
            # Verify current password if one exists
            if has_existing_pw:
                if not verify_password(self.cur_pw.text.strip(), settings.get("password", {})):
                    shake_and_flash(self.cur_pw)
                    return

            if new_pw != confirm_pw:
                shake_and_flash(self.new_pw)
                shake_and_flash(self.confirm_pw)
                return

            if len(new_pw) < 8:
                shake_and_flash(self.new_pw)
                return

            # Confirm via are_you_sure
            app = App.get_running_app()
            are_you_sure = app.screen.get_screen("are_you_sure")
            are_you_sure.prompt_text = lang.WARN_SET_PASSWORD
            are_you_sure.confirm_callback = lambda *_: self._do_set_password(settings, new_pw)
            app.previous_screen = "settings"
            app.screen.current = "are_you_sure"
            return

        # DB path change
        new_db_path = self.db_path_input.text.strip()
        old_db_path = settings.get("db_path", "")
        if new_db_path and new_db_path != old_db_path:
            settings["db_path"] = new_db_path

        storage.save_settings(settings)
        self._on_back()

    def _do_set_password(self, settings, password):
        from crypto import CryptoContext
        from migrate import encrypt_all_data

        old_pw_data = settings.get("password")
        pw_data = hash_password(password)
        settings["password"] = pw_data
        storage.save_settings(settings)

        key = derive_encryption_key(password, pw_data)

        if old_pw_data:
            # Re-encrypt with new key
            from migrate import reencrypt_all_data
            old_key = CryptoContext.get_key()
            if old_key:
                reencrypt_all_data(old_key, key)
        else:
            # First-time encryption
            encrypt_all_data(key)

        CryptoContext.set_key(key)
        LOG.info("Password set/changed successfully")

        app = App.get_running_app()
        app.screen.current = "settings"

    def _on_remove_password(self, *args):
        settings = storage.load_settings()
        stored = settings.get("password", {})
        if not stored:
            return

        cur_pw = self.cur_pw.text.strip()
        if not cur_pw or not verify_password(cur_pw, stored):
            shake_and_flash(self.cur_pw)
            return

        app = App.get_running_app()
        are_you_sure = app.screen.get_screen("are_you_sure")
        are_you_sure.prompt_text = lang.WARN_REMOVE_PASSWORD
        are_you_sure.confirm_callback = lambda *_: self._do_remove_password(settings)
        app.previous_screen = "settings"
        app.screen.current = "are_you_sure"

    def _do_remove_password(self, settings):
        from crypto import CryptoContext
        from migrate import decrypt_all_data

        key = CryptoContext.get_key()
        if key:
            decrypt_all_data(key)

        settings.pop("password", None)
        settings.pop("pw_fail_count", None)
        settings.pop("pw_locked_until", None)
        storage.save_settings(settings)
        CryptoContext.clear()
        LOG.info("Password removed, database decrypted")

        app = App.get_running_app()
        app.screen.current = "settings"

    def _on_export_import(self, *args):
        app = App.get_running_app()
        app.previous_screen = "settings"
        app.screen.current = "export_import"

    def _on_csv_export(self, *args):
        app = App.get_running_app()
        app.previous_screen = "settings"
        app.screen.current = "csv_export"

    def _on_back(self, *args):
        app = App.get_running_app()
        if app.previous_screen:
            app.screen.current = app.previous_screen
        else:
            app.screen.current = "garden_view"
