"""password_check.py - Password gate screen with exponential backoff.

Shown on startup when a password is set. Derives the encryption key on
successful unlock and stores it in CryptoContext.
"""

import logging
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty

from boxes import ContentBox, ItemBox, SpacerBox, WrapperBox
from buttons import ButtonGreen, ButtonRed, PasswordEyeToggle
from crypto import CryptoContext
from effects import shake_and_flash
from helpers import derive_encryption_key, verify_password
from labels import FieldLabel, TitleLabel
from screens import BaseScreen
from text_inputs import MedTextInput
from ui_builders import create_initial_layout
import lang
import storage

LOG = logging.getLogger(__name__)


class PasswordCheckScreen(BaseScreen):

    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._fail_count = 0
        self._locked_until = 0

        app = App.get_running_app()
        title_text = f"Enter your [color={TitleLabel().hex_color}]PASSWORD[/color]"
        screen_wrapper, layout = create_initial_layout(
            self, app, title_text=title_text, left_size=0.2,
            show_day_box=False, show_info_header=False,
        )

        layout.add_widget(WrapperBox(size_hint_y=1))

        # Password input row
        pw_row = ContentBox(orientation="horizontal")
        pw_row.add_widget(FieldLabel(text=lang.SETTINGS_PASSWORD, size_hint_x=0.3))
        input_row = ItemBox(orientation="horizontal")
        self.pw_input = MedTextInput(
            hint_text=lang.HINT_ENTER_PASSWORD, password=True,
        )
        input_row.add_widget(self.pw_input)
        self._eye = PasswordEyeToggle(text_input=self.pw_input)
        input_row.add_widget(self._eye)
        pw_row.add_widget(input_row)
        layout.add_widget(pw_row)

        layout.add_widget(SpacerBox(size_hint_y=0.1))

        # Status label (for backoff messages)
        self.status_label = FieldLabel(text="", size_hint_y=None, height=40)
        layout.add_widget(self.status_label)

        layout.add_widget(SpacerBox(size_hint_y=0.1))

        # Buttons
        btn_row = WrapperBox(orientation="horizontal")
        btn_row.add_widget(WrapperBox())
        unlock_btn = ButtonGreen(text=lang.BUTTON_CONFIRM)
        unlock_btn.bind(on_press=self._on_unlock)
        btn_row.add_widget(unlock_btn)
        layout.add_widget(btn_row)

        layout.add_widget(WrapperBox(size_hint_y=1))

        screen_wrapper.add_widget(layout)
        screen_wrapper.add_widget(SpacerBox(size_hint_x=0.1))

    def on_enter(self):
        self.pw_input.text = ""
        self._eye.reset()
        self.status_label.text = ""
        # Load persisted fail count from settings
        settings = storage.load_settings()
        self._fail_count = settings.get("pw_fail_count", 0)
        self._locked_until = settings.get("pw_locked_until", 0)

    def _on_unlock(self, *args):
        now = time.time()
        if now < self._locked_until:
            remaining = int(self._locked_until - now) + 1
            self.status_label.text = f"Too many attempts. Wait {remaining}s."
            shake_and_flash(self.pw_input)
            return

        pw = self.pw_input.text.strip()
        if not pw:
            shake_and_flash(self.pw_input)
            return

        settings = storage.load_settings()
        stored = settings.get("password", {})

        if not verify_password(pw, stored):
            self._fail_count += 1
            backoff = 2 ** (self._fail_count - 1)
            self._locked_until = time.time() + backoff
            # Persist fail state
            settings["pw_fail_count"] = self._fail_count
            settings["pw_locked_until"] = self._locked_until
            storage.save_settings(settings)

            self.status_label.text = f"Wrong password. Wait {backoff}s before retrying."
            shake_and_flash(self.pw_input)
            LOG.warning("Failed password attempt #%d", self._fail_count)
            return

        # Success - derive encryption key and unlock
        key = derive_encryption_key(pw, stored)
        CryptoContext.set_key(key)

        # Reset fail counter
        self._fail_count = 0
        settings["pw_fail_count"] = 0
        settings.pop("pw_locked_until", None)
        storage.save_settings(settings)

        LOG.info("Password unlock successful")

        app = App.get_running_app()
        target = getattr(app, "post_unlock_screen", None)
        if target:
            app.screen.current = target
        else:
            # Default: go to garden selection or garden view
            gardens = storage.load_gardens()
            if len(gardens) == 1:
                app.current_garden_id = gardens[0].get("id")
                app.screen.current = "garden_view"
            elif len(gardens) > 1:
                app.screen.current = "select_garden"
            else:
                app.screen.current = "add_garden"
