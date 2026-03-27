"""hover_manager.py - centralized mouse hover dispatch.

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


def unregister_tree(root_widget):
    """Unregister *root_widget* and every tracked descendant.

    Call this when a container is removed from the widget tree so that
    deeply-nested registered widgets (e.g. PhotoThumbnails inside an
    orphaned PhotoStrip) do not leak in ``_tracked_widgets``.
    """
    if not _tracked_widgets:
        return
    to_remove = []
    for w in _tracked_widgets:
        try:
            node = w
            seen = set()
            while node is not None:
                if id(node) in seen:
                    break  # cycle guard
                if node is root_widget:
                    to_remove.append(w)
                    break
                seen.add(id(node))
                node = node.parent
        except (ReferenceError, AttributeError):
            # Widget partially destroyed - mark for removal anyway
            to_remove.append(w)
    for w in to_remove:
        unregister(w)


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


def _is_visible_in_scrollview(widget):
    """Return False if *widget* is clipped outside a parent ScrollView."""
    try:
        from kivy.uix.scrollview import ScrollView
        wcx, wcy = widget.to_window(widget.center_x, widget.center_y)
        parent = widget.parent
        seen = set()
        while parent is not None:
            pid = id(parent)
            if pid in seen:
                break  # cycle guard
            seen.add(pid)
            if isinstance(parent, ScrollView):
                local = parent.to_widget(wcx, wcy)
                if not parent.collide_point(*local):
                    return False
            parent = parent.parent
        return True
    except Exception:
        return False


def _on_mouse_pos(window, pos):
    global _current_hovered
    if _popup_active:
        return

    # Check for open popups - suppress hover if any popup is showing
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
                # Ensure the widget is not scrolled out of view
                if not _is_visible_in_scrollview(w):
                    continue
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
