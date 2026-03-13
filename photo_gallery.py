"""photo_gallery.py - Per-plant photo gallery screen.

Layout mirrors TimelineScreen: left sidebar with stripes + title,
right content area with scrollable thumbnail grid and action buttons.
"""

import logging
from uuid import uuid4
from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from screens import BaseScreen
from labels import TitleLabel, FieldLabel
from boxes import WrapperBox, ContentBox, SpacerBox, RedBox, YellowBox, GreenBox
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from photo_widgets import PhotoStrip, PhotoViewPopup, PhotoPickerPopup, bytes_to_texture
from data import PhotoRepository
from are_you_sure import AreYouSure
import lang

LOG = logging.getLogger(__name__)


class PhotoGalleryScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plant = None
        self._selected_photo_id = ""
        self._origin_screen = None  # screen that opened the gallery
        app = App.get_running_app()

        gallery_view = WrapperBox(orientation="horizontal")

        # -- Left sidebar --
        spacer_left = SpacerBox(size_hint_x=0.2)
        gallery_view.add_widget(spacer_left)
        stripes_holder = WrapperBox(orientation="horizontal")
        stripe_0 = ContentBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_0)
        stripe_1 = RedBox(); stripes_holder.add_widget(stripe_1)
        stripe_2 = YellowBox(); stripes_holder.add_widget(stripe_2)
        stripe_3 = GreenBox(); stripes_holder.add_widget(stripe_3)
        stripe_4 = ContentBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_4)
        spacer_left.add_widget(stripes_holder)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        title = TitleLabel(text=lang.PHOTO_GALLERY_TITLE.format(color=TitleLabel().hex_color))
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.2)
        spacer_left.add_widget(spacer_vertical)

        # -- Right content area --
        content = WrapperBox(orientation="vertical")
        gallery_view.add_widget(content)

        # Header
        self.header = WrapperBox(orientation="horizontal", size_hint_y=0.15)
        content.add_widget(self.header)

        title_box = ContentBox(orientation="vertical")
        self.header.add_widget(title_box)
        spacer_box = SpacerBox(size_hint_y=0.2)
        title_box.add_widget(spacer_box)

        name_box = ContentBox(orientation="horizontal", size_hint_y=0.3)
        self.name_label = FieldLabel(text="", valign="middle", halign="left")
        self.name_label.font_size = app.theme.subtitle_size
        self.name_label.color = app.theme.color_field_value
        name_box.add_widget(self.name_label)
        title_box.add_widget(name_box)

        strain_box = ContentBox(orientation="horizontal", size_hint_y=0.5)
        self.strain_label = FieldLabel(text="", valign="middle", halign="left")
        self.strain_label.font_size = app.theme.logo_size_2
        self.strain_label.color = app.theme.color_field_value
        strain_box.add_widget(self.strain_label)
        title_box.add_widget(strain_box)

        # Photo grid (scrollable, spans full width)
        self._photo_strip = PhotoStrip(
            size_hint_y=0.7,
            on_select=self._on_photo_select,
            on_double_click=self._on_photo_double_click,
        )
        content.add_widget(self._photo_strip)

        # Buttons
        footer = SpacerBox(size_hint_y=0.15)
        buttons = ContentBox(size_hint_y=0.66, spacing=10)

        view_btn = ButtonGreen(text=lang.PHOTO_VIEW)
        view_btn.bind(on_release=lambda *_: self._view_selected())
        buttons.add_widget(view_btn)

        add_btn = ButtonYellow(text=lang.PHOTO_ADD)
        add_btn.bind(on_release=lambda *_: self._open_file_picker())
        buttons.add_widget(add_btn)

        delete_btn = ButtonRed(text=lang.PHOTO_DELETE)
        delete_btn.bind(on_release=lambda *_: self._delete_selected())
        buttons.add_widget(delete_btn)

        back_btn = ButtonRed(text=lang.BACK)
        back_btn.bind(on_release=lambda *_: self._go_back())
        buttons.add_widget(back_btn)

        footer.add_widget(buttons)
        content.add_widget(footer)

        right = SpacerBox(size_hint_x=0.1)
        gallery_view.add_widget(right)

        self.add_widget(gallery_view)

    def on_enter(self):
        super().on_enter()
        Window.bind(on_key_down=self._on_key_down)

    def on_leave(self):
        super().on_leave()
        Window.unbind(on_key_down=self._on_key_down)

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 127 or key == 46:  # Delete key
            self._delete_selected()
            return True
        if key == 13:  # Enter
            self._view_selected()
            return True
        return False

    def set_plant(self, plant):
        self.plant = plant or {}
        # Capture the originating screen at navigation time
        app = App.get_running_app()
        self._origin_screen = app.previous_screen
        self._update_ui()

    def _update_ui(self):
        app = App.get_running_app()
        plant = self.plant or {}
        self.name_label.text = " | ".join([plant.get("seedbank", ""), plant.get("genes", "")])
        self.strain_label.text = plant.get("strain", "")
        genes = (plant.get("genes", "") or "").strip().lower()
        if genes == "sativa":
            self.strain_label.color = app.theme.color_strain_sativa
        elif genes == "indica":
            self.strain_label.color = app.theme.color_strain_indica
        elif genes == "hybrid":
            self.strain_label.color = app.theme.color_strain_hybrid
        else:
            self.strain_label.color = app.theme.color_strain_unknown

        plant_id = str(plant.get("id") or plant.get("plant_id") or "")
        if not plant_id:
            return
        PhotoRepository.invalidate()
        photo_metas = PhotoRepository.list_for_plant(plant_id)
        self._photo_strip.set_photos(
            photo_metas,
            load_thumb_fn=PhotoRepository.load_thumb_bytes,
        )

    def _go_back(self):
        """Navigate back to the screen that opened the gallery."""
        app = App.get_running_app()
        target = self._origin_screen or app.previous_screen
        if target:
            app.screen.current = target

    def _on_photo_select(self, photo_id):
        self._selected_photo_id = photo_id

    def _get_photo_list(self):
        """Build full photo list for the current plant (all photos)."""
        plant = getattr(self, 'plant', None) or {}
        plant_id = str(plant.get("id", ""))
        if not plant_id:
            return []
        metas = PhotoRepository.list_for_plant(plant_id)
        return [(m["id"], m["plant_id"]) for m in metas]

    def _on_photo_double_click(self, photo_id, plant_id):
        raw = PhotoRepository.load_photo_bytes(plant_id, photo_id)
        if raw:
            photo_list = self._get_photo_list()
            current_index = 0
            for i, (pid, _) in enumerate(photo_list):
                if pid == photo_id:
                    current_index = i
                    break
            popup = PhotoViewPopup(
                image_bytes=raw,
                photo_list=photo_list,
                current_index=current_index,
            )
            popup.open()

    def _view_selected(self):
        if not self._selected_photo_id:
            return
        meta = PhotoRepository.get_meta(self._selected_photo_id)
        if not meta:
            return
        plant_id = meta.get("plant_id", "")
        raw = PhotoRepository.load_photo_bytes(plant_id, self._selected_photo_id)
        if raw:
            photo_list = self._get_photo_list()
            current_index = 0
            for i, (pid, _) in enumerate(photo_list):
                if pid == self._selected_photo_id:
                    current_index = i
                    break
            popup = PhotoViewPopup(
                image_bytes=raw,
                photo_list=photo_list,
                current_index=current_index,
            )
            popup.open()

    def _delete_selected(self):
        if not self._selected_photo_id:
            return
        app = App.get_running_app()
        photo_id = self._selected_photo_id

        def _do_delete():
            meta = PhotoRepository.get_meta(photo_id)
            if not meta:
                return
            plant_id = meta.get("plant_id", "")
            PhotoRepository.detach(plant_id, photo_id)
            self._photo_strip.remove_thumbnail(photo_id)
            self._selected_photo_id = ""
            app.screen.current = "photo_gallery"

        app.previous_screen = "photo_gallery"
        are_you_sure = app.screen.get_screen("are_you_sure")
        are_you_sure.prompt_text = lang.MSG_CONFIRM_DELETE_PHOTO
        are_you_sure.confirm_callback = _do_delete
        app.screen.current = "are_you_sure"

    def _open_file_picker(self):
        app = App.get_running_app()
        plant = self.plant or {}
        plant_id = str(plant.get("id", ""))
        if not plant_id:
            return

        def _on_file_selected(filepath):
            try:
                image_bytes = filepath.read_bytes()
            except Exception:
                return

            photo_id = str(uuid4())
            garden_id = str(app.current_garden_id or "")
            # Attach to the latest event for this plant
            from data import EventRepository
            from storage import load_plant_events
            data = load_plant_events(plant_id)
            events = data.get("events", []) if data else []
            event_id = events[-1].get("id", "") if events else ""

            ok = PhotoRepository.attach(
                plant_id, event_id, garden_id,
                photo_id, image_bytes, filepath.name,
            )
            if ok and event_id and events:
                photos = events[-1].setdefault("photos", [])
                photos.append(photo_id)
                EventRepository.save(plant_id, data)
                # Add thumbnail to strip
                thumb_bytes = PhotoRepository.load_thumb_bytes(plant_id, photo_id)
                if thumb_bytes:
                    texture = bytes_to_texture(thumb_bytes)
                    self._photo_strip.add_thumbnail(photo_id, plant_id, texture)

        PhotoPickerPopup(on_file_selected=_on_file_selected).open()
