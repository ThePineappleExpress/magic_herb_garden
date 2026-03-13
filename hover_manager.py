"""hover_manager.py — centralized mouse hover dispatch.

Instead of every HoverBehavior widget binding Window.mouse_pos individually,
a single listener tracks which widget is hovered and dispatches on_enter /
on_leave only when the hovered widget changes.
"""

import logging
from kivy.core.window import Window

LOG = logging.getLogger(__name__)

_tracked_widgets: list = []
_current_hovered = None
_popup_active = False


def register(widget):
    """Register a HoverBehavior widget for centralized tracking."""
    if widget not in _tracked_widgets:
        _tracked_widgets.append(widget)


def unregister(widget):
    """Unregister a HoverBehavior widget (e.g., on removal from tree)."""
    global _current_hovered
    try:
        _tracked_widgets.remove(widget)
    except ValueError:
        pass
    if _current_hovered is widget:
        _current_hovered = None


def set_popup_active(active: bool):
    """Call when a popup opens/closes to suppress hover."""
    global _popup_active, _current_hovered
    _popup_active = active
    if active and _current_hovered is not None:
        _current_hovered.hovered = False
        try:
            _current_hovered.on_leave()
        except Exception:
            pass
        _current_hovered = None


def _on_mouse_pos(window, pos):
    global _current_hovered
    if _popup_active:
        return

    # Check for open popups — suppress hover if any popup is showing
    from kivy.uix.popup import Popup
    root = window
    if root:
        for child in root.children:
            if isinstance(child, Popup):
                if _current_hovered is not None:
                    _current_hovered.hovered = False
                    try:
                        _current_hovered.on_leave()
                    except Exception:
                        pass
                    _current_hovered = None
                return

    hit = None
    # Iterate in reverse (top-most first) for z-order correctness
    for w in reversed(_tracked_widgets):
        try:
            if w.get_root_window() and w.collide_point(*w.to_widget(*pos)):
                hit = w
                break
        except Exception:
            continue

    if hit is _current_hovered:
        return

    if _current_hovered is not None:
        _current_hovered.hovered = False
        try:
            _current_hovered.on_leave()
        except Exception:
            pass

    _current_hovered = hit
    if hit is not None:
        hit.hovered = True
        try:
            hit.on_enter()
        except Exception:
            pass


Window.bind(mouse_pos=_on_mouse_pos)
