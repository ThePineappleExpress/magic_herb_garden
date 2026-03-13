"""photo_widgets.py - Reusable UI components for photo attachments.

Provides PhotoThumbnail, PhotoStrip, and PhotoViewPopup.
"""

import logging
from io import BytesIO

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.clock import Clock

from buttons import ButtonRed, ButtonGreen, ButtonYellow, ButtonTransparent, HoverBehavior
import hover_manager

LOG = logging.getLogger(__name__)

THUMB_SIZE = 100
THUMB_HOVER_SIZE = 150


def bytes_to_texture(image_bytes):
    """Convert raw JPEG/PNG bytes into a Kivy Texture."""
    if not image_bytes:
        return None
    try:
        buf = BytesIO(image_bytes)
        img = CoreImage(buf, ext="jpg")
        return img.texture
    except Exception:
        LOG.exception("Failed to convert bytes to texture")
        return None


class PhotoThumbnail(HoverBehavior, BoxLayout):
    """100x100 thumbnail widget with hover overlay and selection.

    - Click: select (highlight border)
    - Double-click: open PhotoViewPopup
    - Hover: overlay enlarges to 150x150 (no layout shift)
    """

    selected = BooleanProperty(False)
    photo_id = StringProperty("")
    plant_id = StringProperty("")

    def __init__(self, photo_id="", plant_id="", texture=None,
                 on_select=None, on_double_click=None, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (THUMB_SIZE, THUMB_SIZE))
        super().__init__(**kwargs)
        self.photo_id = photo_id
        self.plant_id = plant_id
        self._on_select = on_select
        self._on_double_click = on_double_click
        self._hover_widget = None

        self._image = Image(
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True,
        )
        if texture:
            self._image.texture = texture
        self.add_widget(self._image)

        with self.canvas.before:
            self._border_color = Color(0, 0, 0, 0)
            self._border_rect = Line(rectangle=(0, 0, 0, 0), width=2)
        self.bind(pos=self._update_border, size=self._update_border)
        self.bind(selected=self._on_selected_change)

    def set_texture(self, texture):
        self._image.texture = texture

    def _update_border(self, *_):
        if self.selected:
            self._border_color.rgba = [0.773, 0.847, 0.427, 1]
        else:
            self._border_color.rgba = [0, 0, 0, 0]
        x, y = self.pos
        w, h = self.size
        self._border_rect.rectangle = (x, y, w, h)

    def _on_selected_change(self, *_):
        self._update_border()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        if touch.is_double_tap:
            if self._on_double_click:
                self._on_double_click(self.photo_id, self.plant_id)
            return True
        if self._on_select:
            self._on_select(self.photo_id)
        return True

    def on_enter(self):
        """Show enlarged overlay on hover."""
        if self._hover_widget:
            return
        texture = self._image.texture
        if not texture:
            return
        # Don't show hover if thumbnail is clipped by a ScrollView
        from kivy.uix.scrollview import ScrollView
        wcx, wcy = self.to_window(self.center_x, self.center_y)
        parent = self.parent
        while parent is not None:
            if isinstance(parent, ScrollView):
                if not parent.collide_point(*parent.to_widget(wcx, wcy)):
                    return
                break
            parent = parent.parent
        hover = Image(
            texture=texture,
            size_hint=(None, None),
            size=(THUMB_HOVER_SIZE, THUMB_HOVER_SIZE),
            allow_stretch=True,
            keep_ratio=True,
        )
        hover.pos = (wcx - THUMB_HOVER_SIZE / 2, wcy - THUMB_HOVER_SIZE / 2)
        root = self.get_root_window()
        if root:
            root.add_widget(hover)
            self._hover_widget = hover

    def on_leave(self):
        """Remove hover overlay."""
        if self._hover_widget:
            root = self.get_root_window()
            if root:
                try:
                    root.remove_widget(self._hover_widget)
                except Exception:
                    pass
            self._hover_widget = None

    def on_parent(self, instance, parent):
        if parent is None:
            self.on_leave()
            hover_manager.unregister(self)
        else:
            hover_manager.register(self)


class PhotoStrip(BoxLayout):
    """Vertically scrollable grid of PhotoThumbnail widgets.

    Shows thumbnails for a list of photo metadata dicts.
    Provides selection tracking and double-click callbacks.
    """

    selected_photo_id = StringProperty("")

    def __init__(self, on_select=None, on_double_click=None, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        super().__init__(**kwargs)
        self._on_select_cb = on_select
        self._on_double_click_cb = on_double_click
        self._thumbnails = {}

        self._scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        self._grid = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=5,
            padding=5,
            row_default_height=THUMB_SIZE,
        )
        self._grid.bind(minimum_height=self._grid.setter("height"))
        self._scroll.add_widget(self._grid)
        self.add_widget(self._scroll)
        self.bind(width=self._update_cols)

    def _update_cols(self, *_):
        available = max(self.width - 10, THUMB_SIZE)
        cols = max(1, int(available // (THUMB_SIZE + 5)))
        self._grid.cols = cols

    def set_photos(self, photo_metas, load_thumb_fn=None):
        """Populate grid with photo metadata dicts.

        Each dict must have 'id' and 'plant_id' keys.
        load_thumb_fn(plant_id, photo_id) -> bytes for lazy loading.
        """
        self._grid.clear_widgets()
        self._thumbnails.clear()
        self.selected_photo_id = ""

        for meta in photo_metas:
            pid = meta.get("id", "")
            plant_id = meta.get("plant_id", "")
            thumb = PhotoThumbnail(
                photo_id=pid,
                plant_id=plant_id,
                on_select=self._on_thumb_select,
                on_double_click=self._on_thumb_double_click,
            )
            self._thumbnails[pid] = thumb
            self._grid.add_widget(thumb)

            if load_thumb_fn:
                self._lazy_load_thumb(plant_id, pid, thumb, load_thumb_fn)

    def _lazy_load_thumb(self, plant_id, photo_id, thumb_widget, load_fn):
        """Load thumbnail bytes and set texture."""
        def _do_load(dt):
            raw = load_fn(plant_id, photo_id)
            if raw:
                texture = bytes_to_texture(raw)
                if texture:
                    thumb_widget.set_texture(texture)
        Clock.schedule_once(_do_load, 0)

    def _on_thumb_select(self, photo_id):
        # Deselect previous
        if self.selected_photo_id and self.selected_photo_id in self._thumbnails:
            self._thumbnails[self.selected_photo_id].selected = False
        # Select new
        self.selected_photo_id = photo_id
        if photo_id in self._thumbnails:
            self._thumbnails[photo_id].selected = True
        if self._on_select_cb:
            self._on_select_cb(photo_id)

    def _on_thumb_double_click(self, photo_id, plant_id):
        if self._on_double_click_cb:
            self._on_double_click_cb(photo_id, plant_id)

    def add_thumbnail(self, photo_id, plant_id, texture=None):
        """Add a single thumbnail to the grid."""
        thumb = PhotoThumbnail(
            photo_id=photo_id,
            plant_id=plant_id,
            texture=texture,
            on_select=self._on_thumb_select,
            on_double_click=self._on_thumb_double_click,
        )
        self._thumbnails[photo_id] = thumb
        self._grid.add_widget(thumb)

    def remove_thumbnail(self, photo_id):
        """Remove a thumbnail from the grid."""
        thumb = self._thumbnails.pop(photo_id, None)
        if thumb:
            self._grid.remove_widget(thumb)
        if self.selected_photo_id == photo_id:
            self.selected_photo_id = ""


class PhotoViewPopup(Popup):
    """Full-window image viewer with zoom, pan, and gallery navigation.

    Zoom: Ctrl+scroll
    Pan vertical: scroll wheel
    Pan horizontal: Shift+scroll
    Pan: click-and-drag
    Navigate: Left/Right arrow keys or side arrow buttons
    Close: X button or Escape
    """

    def __init__(self, image_bytes=None, texture=None,
                 photo_list=None, current_index=0, **kwargs):
        """Create the popup.

        Args:
            image_bytes: Raw image bytes for initial photo.
            texture: Kivy texture for initial photo.
            photo_list: List of (photo_id, plant_id) tuples for navigation.
            current_index: Index into photo_list for the currently shown photo.
        """
        kwargs.setdefault("size_hint", (1, 1))
        kwargs.setdefault("title", "")
        kwargs.setdefault("separator_height", 0)
        kwargs.setdefault("auto_dismiss", False)
        kwargs.setdefault("background", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0.8))
        super().__init__(**kwargs)

        self._photo_list = photo_list or []
        self._current_index = current_index
        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._last_touch_pos = None

        self._content_box = FloatLayout()

        # Photo image — size/pos managed manually via _apply_transform
        self._photo_image = Image(
            size_hint=(None, None),
            allow_stretch=True,
            keep_ratio=True,
        )
        if texture:
            self._photo_image.texture = texture
        elif image_bytes:
            tex = bytes_to_texture(image_bytes)
            if tex:
                self._photo_image.texture = tex
        self._content_box.add_widget(self._photo_image)

        # Overlay — always rendered above the image
        self._overlay = FloatLayout(size_hint=(1, 1))

        self._left_arrow = ButtonTransparent(
            text="<",
            size_hint=(None, None),
            size=(50, 80),
            pos_hint={"x": 0, "center_y": 0.5},
            font_size=32,
            opacity=0.7,
        )
        self._left_arrow.bind(on_release=lambda *_: self._navigate(-1))
        self._overlay.add_widget(self._left_arrow)

        self._right_arrow = ButtonTransparent(
            text=">",
            size_hint=(None, None),
            size=(50, 80),
            pos_hint={"right": 1, "center_y": 0.5},
            font_size=32,
            opacity=0.7,
        )
        self._right_arrow.bind(on_release=lambda *_: self._navigate(1))
        self._overlay.add_widget(self._right_arrow)

        self._close_btn = ButtonRed(
            text="X",
            size_hint=(None, None),
            size=(40, 40),
            pos_hint={"right": 1, "top": 1},
        )
        self._close_btn.bind(on_release=lambda *_: self.dismiss())
        self._overlay.add_widget(self._close_btn)

        self._content_box.add_widget(self._overlay)
        self.content = self._content_box

        self._content_box.bind(size=self._apply_transform, pos=self._apply_transform)
        self._update_arrows()
        Clock.schedule_once(self._apply_transform, 0)
        Window.bind(on_key_down=self._on_key_down)

    # ------------------------------------------------------------------
    def _apply_transform(self, *_):
        """Recompute image size and position from current zoom and pan."""
        img = self._photo_image
        tex = img.texture
        if not tex:
            return
        cw, ch = self._content_box.size
        cx, cy = self._content_box.pos
        if cw <= 0 or ch <= 0:
            return
        tw, th = tex.size
        base_scale = min(cw / tw, ch / th)
        scale = base_scale * self._zoom
        img.size = (tw * scale, th * scale)
        img.center_x = cx + cw / 2 + self._pan_x
        img.center_y = cy + ch / 2 + self._pan_y

    # ------------------------------------------------------------------
    def _update_arrows(self):
        """Show/hide arrow buttons based on adjacent photos."""
        has_list = len(self._photo_list) > 1
        show_left = has_list and self._current_index > 0
        show_right = has_list and self._current_index < len(self._photo_list) - 1
        self._left_arrow.opacity = 0.7 if show_left else 0
        self._left_arrow.disabled = not show_left
        self._right_arrow.opacity = 0.7 if show_right else 0
        self._right_arrow.disabled = not show_right

    def _navigate(self, direction):
        """Navigate to adjacent photo. direction: -1 (prev) or +1 (next)."""
        if not self._photo_list:
            return
        new_index = self._current_index + direction
        if new_index < 0 or new_index >= len(self._photo_list):
            return
        self._current_index = new_index
        photo_id, plant_id = self._photo_list[new_index]
        try:
            from data import PhotoRepository
            raw = PhotoRepository.load_photo_bytes(plant_id, photo_id)
            if raw:
                self.set_image(image_bytes=raw)
        except Exception:
            LOG.exception("Failed to load photo %s for navigation", photo_id)
        self._update_arrows()

    # ------------------------------------------------------------------
    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 27:  # Escape
            self.dismiss()
            return True
        if key == 276:  # Left arrow
            self._navigate(-1)
            return True
        if key == 275:  # Right arrow
            self._navigate(1)
            return True
        return False

    # ------------------------------------------------------------------
    def on_touch_down(self, touch):
        # Block all touches so nothing underneath responds
        if not self.collide_point(*touch.pos):
            return True

        # Overlay buttons always get first priority
        if self._close_btn.collide_point(*touch.pos):
            return self._close_btn.dispatch('on_touch_down', touch)
        if not self._left_arrow.disabled and self._left_arrow.collide_point(*touch.pos):
            return self._left_arrow.dispatch('on_touch_down', touch)
        if not self._right_arrow.disabled and self._right_arrow.collide_point(*touch.pos):
            return self._right_arrow.dispatch('on_touch_down', touch)

        if 'button' in touch.profile:
            mods = Window._modifiers if hasattr(Window, '_modifiers') else []
            # Shift+scroll = horizontal pan
            if 'shift' in mods:
                if touch.button == 'scrollup':
                    self._pan_x += 30
                    self._apply_transform()
                    return True
                elif touch.button == 'scrolldown':
                    self._pan_x -= 30
                    self._apply_transform()
                    return True
            # Ctrl+scroll = zoom
            if 'ctrl' in mods:
                if touch.button == 'scrollup':
                    self._zoom = min(self._zoom * 1.1, 10.0)
                    self._apply_transform()
                    return True
                elif touch.button == 'scrolldown':
                    self._zoom = max(self._zoom / 1.1, 0.5)
                    self._apply_transform()
                    return True
            # Plain scroll = vertical pan
            if touch.button == 'scrollup':
                self._pan_y += 30
                self._apply_transform()
                return True
            elif touch.button == 'scrolldown':
                self._pan_y -= 30
                self._apply_transform()
                return True

        # Left click → start drag-to-pan
        touch.grab(self)
        self._last_touch_pos = (touch.x, touch.y)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            dx = touch.x - self._last_touch_pos[0]
            dy = touch.y - self._last_touch_pos[1]
            self._pan_x += dx
            self._pan_y += dy
            self._last_touch_pos = (touch.x, touch.y)
            self._apply_transform()
            return True
        return True  # block everything

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return True  # block everything

    # ------------------------------------------------------------------
    def dismiss(self, *args, **kwargs):
        Window.unbind(on_key_down=self._on_key_down)
        super().dismiss(*args, **kwargs)

    def set_image(self, image_bytes=None, texture=None):
        """Update the displayed image."""
        if texture:
            self._photo_image.texture = texture
        elif image_bytes:
            tex = bytes_to_texture(image_bytes)
            if tex:
                self._photo_image.texture = tex
        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._apply_transform()


class PhotoPickerPopup(Popup):
    """File chooser popup with a live image preview panel on the right.

    The preview auto-updates when the user selects a file in the chooser.
    Call ``open()`` to show, and bind ``on_file_selected`` to receive the
    chosen ``Path`` when the user confirms.
    """

    def __init__(self, on_file_selected=None, **kwargs):
        import lang
        from pathlib import Path as _Path

        kwargs.setdefault("title", lang.PHOTO_ADD)
        kwargs.setdefault("size_hint", (0.8, 0.8))
        super().__init__(**kwargs)

        self._on_file_selected = on_file_selected

        root = BoxLayout(orientation="vertical")

        # --- top row: file chooser (left) + preview (right) ---------------
        browser_row = BoxLayout(orientation="horizontal")
        root.add_widget(browser_row)

        from kivy.uix.filechooser import FileChooserListView
        self._chooser = FileChooserListView(
            filters=["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"],
            path=str(_Path.home()),
            size_hint_x=0.55,
        )
        browser_row.add_widget(self._chooser)

        # Preview panel
        preview_box = BoxLayout(
            orientation="vertical",
            size_hint_x=0.45,
            padding=10,
        )
        self._preview_image = Image(
            allow_stretch=True,
            keep_ratio=True,
        )
        preview_box.add_widget(self._preview_image)
        browser_row.add_widget(preview_box)

        # Update preview when selection changes
        self._chooser.bind(selection=self._on_selection_change)

        # --- button row ---------------------------------------------------
        btn_row = BoxLayout(size_hint_y=None, height=50)
        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        cancel_btn.bind(on_release=lambda *_: self.dismiss())
        btn_row.add_widget(cancel_btn)

        select_btn = ButtonGreen(text=lang.PHOTO_ADD)
        select_btn.bind(on_release=lambda *_: self._confirm())
        btn_row.add_widget(select_btn)
        root.add_widget(btn_row)

        self.content = root

    def _on_selection_change(self, chooser, selection):
        """Load a preview of the currently highlighted file."""
        if not selection:
            self._preview_image.texture = None
            return
        from pathlib import Path as _Path
        p = _Path(selection[0])
        if not p.is_file():
            self._preview_image.texture = None
            return
        try:
            raw = p.read_bytes()
            tex = bytes_to_texture(raw)
            self._preview_image.texture = tex
        except Exception:
            self._preview_image.texture = None

    def _confirm(self):
        """Invoke callback with the selected Path and dismiss."""
        selection = self._chooser.selection
        if not selection:
            return
        from pathlib import Path as _Path
        filepath = _Path(selection[0])
        if not filepath.is_file():
            return
        if self._on_file_selected:
            self._on_file_selected(filepath)
        self.dismiss()
