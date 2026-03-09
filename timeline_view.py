from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, Ellipse, InstructionGroup
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp

from kivy.garden.graph import Graph, LinePlot

from constants import EVENT_WATERING, EVENT_FEEDING, EVENT_PLANTING
from buttons import ButtonRed, NutrientButton, GraphButton
from labels import TitleLabel, FieldLabel
from screens import BaseScreen
from boxes import WrapperBox, ContentBox, SpacerBox, RedBox, YellowBox, GreenBox
from storage import load_plant_events, get_plants_for_garden
from are_you_sure import AreYouSure
from datetime import datetime, timedelta
import math
import copy

# Maps data keys to their theme color attribute names
GRAPH_KEY_COLORS = {
    # Plant
    "plant_height": "color_graph_plant_height",
    "num_nodes": "color_graph_nodes",
    "node_spacing": "color_graph_node_spacing",
    "main_stem_number": "color_graph_stem_count",
    # Environment
    "air_temp_c": "color_graph_air_temp",
    "rh_percent": "color_graph_humidity",
    "soil_moisture": "color_graph_soil_moisture",
    "soil_ph": "color_graph_soil_ph",
    "vpd_kpa": "color_graph_vpd",
    "ppfd": "color_graph_ppfd",
    # Water
    "volume_l": "color_graph_water_volume",
    "water_temp_c": "color_graph_water_temp",
    "ph": "color_graph_water_ph",
    "ppm": "color_graph_water_ppm",
    # Food
    "grow_mix": "color_graph_grow_mix",
    "root_mix": "color_graph_root_mix",
    "bloom_mix": "color_graph_bloom_mix",
    "bloom_boost": "color_graph_bloom_boost",
    "soil_boost": "color_graph_soil_boost",
    "vit_boost": "color_graph_vit_boost",
    "CalMag": "color_graph_calmag",
}


class SimpleGraph(BoxLayout):
    def __init__(self, key=None, color=None, owner=None, tab_key=None, multi_keys=None, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=120, **kwargs)
        app = App.get_running_app()
        self.key = key
        self.color = color
        self._owner = owner
        self._tab_key = tab_key
        self.multi_keys = list(multi_keys) if multi_keys else None
        legend_row = WrapperBox(orientation="horizontal", size_hint_y=None, height=28)
        if key == "plant_height":
            legend_title = "Plant Height (cm)"
        elif key == "num_nodes":
            legend_title = "Number of Nodes"
        elif key == "node_spacing":
            legend_title = "Node Spacing (cm)"
        elif key == "main_stem_number":
            legend_title = "Main Stem Number"
        elif key == "air_temp_c":
            legend_title = "Air Temperature (°C)"
        elif key == "rh_percent":
            legend_title = "Relative Humidity (%)"
        elif key == "soil_moisture":
            legend_title = "Soil Moisture Level"
        elif key == "soil_ph":
            legend_title = "Soil pH"
        elif key == "vpd_kpa":
            legend_title = "VPD (kPa)"
        elif key == "ppfd":
            legend_title = "PPFD (µmol/m²/s)"
        elif key == "volume_l":
            legend_title = "Water Volume (L)"
        elif key == "water_temp_c":
            legend_title = "Water Temperature (°C)"
        elif key == "ph":
            legend_title = "Water pH"
        elif key == "ppm":
            legend_title = "Water PPM"
        else:
            legend_title = ""
        legend_label = FieldLabel(text=legend_title, halign="right", padding=app.theme.padding_right)
        legend_label.color = app.theme.color_field_value
        legend_label.font_size = app.theme.body_size
        legend_row.add_widget(legend_label)
        self.add_widget(legend_row)
        content_row = BoxLayout(orientation="horizontal")
        self._y_label_col = BoxLayout(orientation="vertical", size_hint_x=None, width=80)
        content_row.add_widget(self._y_label_col)
        center_col = BoxLayout(orientation="vertical")
        self.graph = Graph(xlabel="", ylabel="", x_ticks_minor=0, x_grid=True, y_grid=True, xmin=0, xmax=10, ymin=0, ymax=1, padding=5, x_ticks_major=1, y_ticks_major=1)
        self.graph.bind(on_touch_down=self._on_graph_touch)
        self.graph.bind(on_touch_move=self._on_graph_touch_move, on_touch_up=self._on_graph_touch_up)
        self._bg_rect = Rectangle(pos=self.graph.pos, size=self.graph.size, color = app.theme.color_transparent)
        self.graph.bind(pos=self._update_bg_rect, size=self._update_bg_rect)
        self.plot = None
        self.plots = {}
        self._plot_visible = {}
        if self.multi_keys:
            for mk in self.multi_keys:
                attr = GRAPH_KEY_COLORS.get(mk, "color_graph_line")
                col = getattr(app.theme, attr, app.theme.color_graph_line)
                lp = LinePlot(color=col)
                lp.line_width = 2
                self.graph.add_plot(lp)
                self.plots[mk] = lp
                self._plot_visible[mk] = True
        else:
            self.plot = LinePlot(color=self.color)
            self.plot.line_width = 2
            self.graph.add_plot(self.plot)
        self._scheduled_x_update = None
        self._pending_x_args = None
        self._grid_lines = []
        self._h_grid_lines = []
        self._grid_color = None
        self._scheduled_grid_update = None
        with self.graph.canvas.before:
            self._grid_color = Color(*app.theme.color_button_bg)
        self._label_rects = []
        self._y_label_rects = []
        self._label_color = None
        with self.graph.canvas.after:
            self._label_color = Color(*app.theme.color_field_value)
        # marker instruction group (recreated each redraw)
        self._marker_group = None
        self.graph.bind(
            xmin=lambda *a: self._schedule_grid_update(), 
            xmax=lambda *a: self._schedule_grid_update(), 
            x_ticks_major=lambda *a: self._schedule_grid_update(), 
            pos=lambda *a: self._schedule_grid_update(), 
            size=lambda *a: self._schedule_grid_update()
        )
        center_col.add_widget(self.graph)
        self._x_label_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=0)
        center_col.add_widget(self._x_label_row)
        content_row.add_widget(center_col)
        self.add_widget(content_row)
        self.full_points = []
        self._xmin = 0
        self._xmax = 10
        self.graph.bind(ymin=lambda *a: self._update_y_labels(), ymax=lambda *a: self._update_y_labels(), y_ticks_major=lambda *a: self._update_y_labels(), size=lambda *a: self._update_y_labels())
        self._current_base_date = None
        self._current_fmt = "%d.%m.%y"

    def _update_bg_rect(self, *a):
        self._bg_rect.pos = self.graph.pos
        self._bg_rect.size = self.graph.size

    def _clear_y_labels(self):
        self._y_label_col.clear_widgets()
        for r in list(self._y_label_rects):
            self.graph.canvas.after.remove(r)
        self._y_label_rects = []

    def _compute_y_ticks(self):
        ymin = float(self.graph.ymin)
        ymax = float(self.graph.ymax)
        tick = float(getattr(self.graph, "y_ticks_major", 0) or 0)
        ticks = []
        if tick > 0 and ymax > ymin:
            v = ymin
            while v <= ymax + 1e-9:
                ticks.append(v)
                v += tick
            if not ticks or abs(ticks[-1] - ymax) > 1e-9:
                ticks.append(ymax)
        else:
            for i in range(5):
                ticks.append(ymin + (ymax - ymin) * i / 4.0)
        return ticks

    def _compute_nice_tick(self, ymin, ymax, intervals=4):
        y_range = float(ymax) - float(ymin)
        if y_range <= 0:
            return 1
        raw = y_range / float(intervals)
        mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
        residual = raw / mag
        if residual <= 1:
            nice = 1
        elif residual <= 2:
            nice = 2
        elif residual <= 5:
            nice = 5
        else:
            nice = 10
        return nice * mag

    def _update_y_labels(self):
        self._clear_y_labels()
        ticks = self._compute_y_ticks()
        if not ticks:
            return
        app = App.get_running_app()
        def _is_intish(x):
            return abs(x - round(x)) < 1e-8
        ymin = float(self.graph.ymin)
        ymax = float(self.graph.ymax)
        needed = len(ticks)
        while len(self._y_label_rects) < needed:
            r = Rectangle(texture=None, pos=(0, 0), size=(0, 0))
            self.graph.canvas.after.add(r)
            self._y_label_rects.append(r)
        while len(self._y_label_rects) > needed:
            r = self._y_label_rects.pop()
            self.graph.canvas.after.remove(r)
        for i, val in enumerate(ticks):
            if _is_intish(val):
                text = str(int(round(val)))
            else:
                text = ("%.2f" % val).rstrip("0").rstrip(".")
            fs = 12
            s = app.theme.body_size
            if isinstance(s, (int, float)):
                fs = s
            elif isinstance(s, str) and s.endswith("sp"):
                fs = float(s[:-2])
            else:
                fs = float(s)
            cl = CoreLabel(text=text, font_size=fs, font_name=app.theme.font_body)
            cl.refresh()
            tex = cl.texture
            frac = (val - ymin) / (ymax - ymin) if ymax > ymin else 0
            ypix = self.graph.y + frac * self.graph.height
            xbase = self._y_label_col.x
            xwidth = self._y_label_col.width
            px = xbase + max(4, xwidth - tex.width - 6)
            py = ypix - tex.height / 2.0
            r = self._y_label_rects[i]
            r.texture = tex
            r.size = (tex.width, tex.height)
            r.pos = (px, py)
        self._schedule_grid_update()

    def _schedule_grid_update(self):
        if self._scheduled_grid_update is not None:
            self._scheduled_grid_update.cancel()
        self._scheduled_grid_update = Clock.schedule_once(self._draw_grid, 0)

    def _draw_grid(self, _dt):
        try:
            xmin = float(self.graph.xmin)
            xmax = float(self.graph.xmax)
            step = float(self.graph.x_ticks_major) if getattr(self.graph, "x_ticks_major", None) else None
            if step is None or step <= 0 or xmax <= xmin:
                for ln in self._grid_lines:
                    ln.points = []
                return
            ticks = []
            start = math.ceil(xmin / step) * step
            v = start
            while v <= xmax + 1e-9:
                ticks.append(v)
                v += step
            needed = len(ticks)
            while len(self._grid_lines) < needed:
                ln = Line(points=[], width=1)
                self.graph.canvas.before.add(ln)
                self._grid_lines.append(ln)
            while len(self._grid_lines) > needed:
                ln = self._grid_lines.pop()
                self.graph.canvas.before.remove(ln)
            for i, t in enumerate(ticks):
                frac = (t - xmin) / (xmax - xmin)
                xpix = self.graph.x + frac * self.graph.width
                y0 = self.graph.y
                y1 = self.graph.y + self.graph.height
                self._grid_lines[i].points = [xpix, y0, xpix, y1]
            y_ticks = self._compute_y_ticks()
            ymin = float(self.graph.ymin)
            ymax = float(self.graph.ymax)
            needed_h = len(y_ticks)
            while len(self._h_grid_lines) < needed_h:
                ln = Line(points=[], width=1)
                self.graph.canvas.before.add(ln)
                self._h_grid_lines.append(ln)
            while len(self._h_grid_lines) > needed_h:
                ln = self._h_grid_lines.pop()
                self.graph.canvas.before.remove(ln)
            for i, yval in enumerate(y_ticks):
                frac = (yval - ymin) / (ymax - ymin) if ymax > ymin else 0
                ypix = self.graph.y + frac * self.graph.height
                x0 = self.graph.x
                x1 = self.graph.x + self.graph.width
                self._h_grid_lines[i].points = [x0, ypix, x1, ypix]
            try:
                base = getattr(self, "_current_base_date", None)
                fmt = getattr(self, "_current_fmt", None) or "%d.%m.%y"
                if base is None:
                    for r in list(self._label_rects):
                        try:
                            self.graph.canvas.after.remove(r)
                        except Exception:
                            pass
                    self._label_rects = []
                else:
                    labels = []
                    app = App.get_running_app()
                    fs = 12
                    try:
                        s = app.theme.body_size
                        if isinstance(s, (int, float)):
                            fs = s
                        elif isinstance(s, str) and s.endswith("sp"):
                            fs = float(s[:-2])
                        else:
                            fs = float(s)
                    except Exception:
                        fs = 12
                    for t in ticks:
                        days = int(round(t))
                        dt = base + timedelta(days=days)
                        txt = f"{dt.day}.{dt.month}.{dt.year % 100:02d}"
                        cl = CoreLabel(text=txt, font_size=fs)
                        cl.refresh()
                        labels.append((txt, cl.texture))

                    needed = len(labels)
                    # create extra Rectangles if needed
                    while len(self._label_rects) < needed:
                        r = Rectangle(texture=None, pos=(0, 0), size=(0, 0))
                        self.graph.canvas.after.add(r)
                        self._label_rects.append(r)
                    # remove surplus rects
                    while len(self._label_rects) > needed:
                        r = self._label_rects.pop()
                        self.graph.canvas.after.remove(r)

                    # draw labels, skipping ones that would overlap
                    last_center = None
                    last_half = 0
                    min_gap = 8
                    for i, (txt, tex) in enumerate(labels):
                        frac = (ticks[i] - xmin) / (xmax - xmin)
                        xpix = self.graph.x + frac * self.graph.width
                        w = tex.width
                        h = tex.height
                        center = xpix
                        half = w / 2.0
                        if last_center is not None and (center - last_center) < (last_half + half + min_gap):
                                # hide this label
                            self._label_rects[i].texture = None
                            self._label_rects[i].size = (0, 0)
                            continue
                        # position label inside the reserved x_label_row area (centered vertically)
                        px = xpix - w / 2.0
                        py = self._x_label_row.y + max(0, (self._x_label_row.height - h) / 2.0)
                        self._label_rects[i].texture = tex
                        self._label_rects[i].size = (w, h)
                        self._label_rects[i].pos = (px, py)
                        last_center = center
                        last_half = half
            except Exception:
                pass
            
            # After drawing labels, draw point markers for plotted points so
            # they move together with graph scrolling/zooming. We'll recreate a
            # fresh InstructionGroup each redraw to avoid leftover instructions
            # that cause ghosting.
            try:
                ymin = float(self.graph.ymin)
                ymax = float(self.graph.ymax)
                xmin = float(self.graph.xmin)
                xmax = float(self.graph.xmax)
                # helper to ensure safe fraction
                def _frac(v, lo, hi):
                    return (v - lo) / (hi - lo) if hi > lo else 0.0

                # compute inner plotting rect accounting for Graph.padding
                pad_val = getattr(self.graph, 'padding', 0)
                if isinstance(pad_val, (list, tuple)):
                    if len(pad_val) == 4:
                        pad_left, pad_top, pad_right, pad_bottom = pad_val
                    elif len(pad_val) == 2:
                        pad_left, pad_top = pad_val
                        pad_right, pad_bottom = pad_left, pad_top
                    else:
                        pad_left = pad_top = pad_right = pad_bottom = float(pad_val[0]) if pad_val else 0
                else:
                    pad_left = pad_top = pad_right = pad_bottom = float(pad_val or 0)

                x_base = float(self.graph.x) + pad_left
                x_width = max(1.0, float(self.graph.width) - (pad_left + pad_right))
                y_base = float(self.graph.y) + pad_bottom
                y_height = max(1.0, float(self.graph.height) - (pad_top + pad_bottom))

                # recreate marker group
                try:
                    if getattr(self, '_marker_group', None) is not None:
                        try:
                            self.graph.canvas.after.remove(self._marker_group)
                        except Exception:
                            pass
                    self._marker_group = InstructionGroup()
                    self.graph.canvas.after.add(self._marker_group)
                except Exception:
                    self._marker_group = None

                # Single-series plot: draw markers for actual plotted or raw series
                if getattr(self, 'plot', None) is not None and not self.multi_keys and getattr(self, '_marker_group', None) is not None:
                    pts = getattr(self.plot, 'points', None)
                    if not pts:
                        pts = (getattr(self, '_last_series_map', {}) or {}).get(self.key, []) or getattr(self, 'full_points', []) or []
                    try:
                        pass
                    except Exception:
                        pass
                    for x, y in pts:
                        # only draw if inside bounds
                        if x < xmin or x > xmax or y < ymin or y > ymax:
                            continue
                        fracx = _frac(x, xmin, xmax)
                        fracy = _frac(y, ymin, ymax)
                        xpix = x_base + fracx * x_width
                        ypix = y_base + fracy * y_height
                        # small visual correction: nudge single-series markers up
                        # so they visually align with the LinePlot stroke
                        try:
                            ypix += dp(2)
                        except Exception:
                            pass
                        d = dp(15)
                        r = d / 2.0
                        try:
                            rawc = getattr(self.plot, 'color', None) or getattr(self, 'color', None) or app.theme.color_field_value
                            cval = list(rawc) if isinstance(rawc, (list, tuple)) else list(rawc)
                            if len(cval) == 3:
                                cval = [cval[0], cval[1], cval[2], 1.0]
                        except Exception:
                            cval = (1, 1, 1, 1)
                        self._marker_group.add(Color(*cval))
                        self._marker_group.add(Ellipse(pos=(xpix - r, ypix - r), size=(d, d)))

                # Multi-series plots
                if self.multi_keys and getattr(self, '_marker_group', None) is not None:
                    for mk in self.multi_keys:
                        lp = self.plots.get(mk)
                        if lp is None:
                            continue
                        # skip drawing markers for plots that are toggled off
                        try:
                            if not self._plot_visible.get(mk, True):
                                continue
                        except Exception:
                            pass
                        # prefer the points currently plotted on the LinePlot (this
                        # reflects toggles and uses raw points when available).
                        pts = getattr(lp, 'points', None) or []
                        if not pts:
                            try:
                                pts = list((getattr(self, '_last_series_map', {}) or {}).get(mk, []) or [])
                            except Exception:
                                pts = []
                        for x, y in pts:
                            if x < xmin or x > xmax or y < ymin or y > ymax:
                                continue
                            fracx = _frac(x, xmin, xmax)
                            fracy = _frac(y, ymin, ymax)
                            xpix = x_base + fracx * x_width
                            ypix = y_base + fracy * y_height
                            d = dp(15)
                            r = d / 2.0
                            try:
                                rawc = getattr(lp, 'color', None) or app.theme.color_field_value
                                cval = list(rawc) if isinstance(rawc, (list, tuple)) else list(rawc)
                                if len(cval) == 3:
                                    cval = [cval[0], cval[1], cval[2], 1.0]
                            except Exception:
                                cval = (1, 1, 1, 1)
                            self._marker_group.add(Color(*cval))
                            self._marker_group.add(Ellipse(pos=(xpix - r, ypix - r), size=(d, d)))
            except Exception:
                pass
            # ensure the shared label color instruction stays set to off-white
            try:
                app = App.get_running_app()
                if getattr(self, '_label_color', None) is not None:
                    self._label_color.rgba = list(app.theme.color_field_value)
            except Exception:
                pass
        except Exception:
            pass

    def _on_graph_touch(self, graph, touch):
        try:
            # ignore touches outside this graph to avoid swallowing other widgets" events
            if not graph.collide_point(*touch.pos):
                return False

            # Kivy mouse wheel may appear as touch.scroll_y or via touch.button
            scroll_y = 0
            if hasattr(touch, "scroll_y"):
                scroll_y = getattr(touch, "scroll_y") or 0
            elif hasattr(touch, "button") and touch.button:
                btn = touch.button.lower()
                if "up" in btn:
                    scroll_y = 1
                elif "down" in btn:
                    scroll_y = -1
            # start drag on left click
            if hasattr(touch, "button") and touch.button and touch.button.lower() == "left":
                try:
                    touch.grab(self)
                except Exception:
                    pass
                self._drag_start_pos = touch.pos
                return True

            if scroll_y == 0:
                return False

            # detect shift modifier
            try:
                raw_mods = getattr(Window, "modifiers", None)
                if raw_mods is None:
                    raw_mods = getattr(Window, "_modifiers", None)
                mods = [m.lower() for m in (raw_mods or [])]
            except Exception:
                mods = []

            if "shift" in mods:
                factor = 0.8 if scroll_y > 0 else 1.25
                self.zoom(factor)
            else:
                frac = -0.1 if scroll_y > 0 else 0.1
                self.scroll(frac)
            # if owner present, sync this graph"s window to other graphs in same tab
            try:
                if getattr(self, "_owner", None):
                    self._owner._sync_graphs_to(self)
            except Exception:
                pass
            return True
        except Exception:
            return False

    def set_series(self, points):
        """points: list of (x, y) numeric. x expected increasing."""
        # If multi_keys configured, `points` is expected to be a mapping key->list[(x,y)]
        # capture whether this graph previously had any points so we can detect
        # an initial population (no user interaction yet)
        prev_has_points = bool(getattr(self, 'full_points', []))
        if self.multi_keys:
            # combine bounds across all provided series
            try:
                self._last_series_map = dict(points or {})
            except Exception:
                self._last_series_map = {}
            all_x = []
            all_y = []
            combined_filled = []
            for mk in self.multi_keys:
                pts_filled = points.get(mk, []) if isinstance(points, dict) else []
                pts_filled = sorted(pts_filled, key=lambda p: p[0]) if pts_filled else []
                raw_map = (points.get('_raw') if isinstance(points, dict) else None) or {}
                pts_raw = raw_map.get(mk, None)
                if pts_raw:
                    pts_raw = sorted(pts_raw, key=lambda p: p[0]) if pts_raw else []
                # extend combined filled list for full_points used in scrolling/zooming
                combined_filled.extend(pts_filled)
                all_x.extend([p[0] for p in pts_filled])
                all_y.extend([p[1] for p in pts_filled])
                lp = self.plots.get(mk)
                if lp is not None:
                    if self._plot_visible.get(mk, True) and (pts_raw or pts_filled):
                        use_pts = pts_raw if pts_raw else pts_filled
                        lp.points = [(x, y) for x, y in use_pts]
                    else:
                        lp.points = []
            # set full_points to the combined filled points across all series (sorted, unique by x)
            try:
                combined_filled_sorted = sorted(combined_filled, key=lambda p: p[0])
                self.full_points = combined_filled_sorted
            except Exception:
                self.full_points = combined_filled
            if not all_x:
                self.graph.xmin = 0
                self.graph.xmax = 1
                self.graph.ymin = 0
                self.graph.ymax = 1
                return
            xmin, xmax = min(all_x), max(all_x)
            # On initial population (graph not yet interacted with), have the
            # graph fill the available width by showing the entire data span.
            # If the graph already had a user/window set, preserve it (do not
            # reset to full span).
            try:
                is_initial = (getattr(self, '_xmin', None) == 0 and getattr(self, '_xmax', None) == 10 and not prev_has_points)
            except Exception:
                is_initial = False
            if is_initial:
                self._xmin = xmin
                self._xmax = xmax
            else:
                # For non-initial visuals, prefer a wider default window anchored to most recent
                DEFAULT_WINDOW = 60
                self._xmax = xmax
                self._xmin = min(xmin, xmax - DEFAULT_WINDOW)
                # ensure a minimum visible width of 1 day to avoid degenerate views
                if self._xmax - self._xmin < 1:
                    self._xmin = self._xmax - 1
            ymin = 0.0
            ymax = max(all_y) if all_y else 1.0
            # Set ymax to next highest 0.5 step
            ymax = 0.5 * math.ceil((ymax + 1e-9) / 0.5)
            if ymin == ymax:
                ymax = max(ymax, ymin + 0.5)
            self.graph.xmin = self._xmin
            self.graph.xmax = self._xmax
            self.graph.ymin = ymin
            self.graph.ymax = ymax
            self.graph.y_ticks_major = 0.5
            try:
                self._update_y_labels()
            except Exception:
                pass
            return

        # legacy single-series handling
        # allow callers to pass a dict with filled data plus '_raw' mapping
        # capture prior state to detect initial population
        prev_has_points = bool(getattr(self, 'full_points', []))
        if isinstance(points, dict) and not self.multi_keys:
            filled = points.get(self.key, [])
            filled = sorted(filled, key=lambda p: p[0]) if filled else []
            raw_map = points.get('_raw', {}) or {}
            raw = raw_map.get(self.key, [])
            raw = sorted(raw, key=lambda p: p[0]) if raw else []
            points_for_bounds = filled
            points_for_plot = raw if raw else filled
        else:
            points_for_bounds = points
            points_for_plot = points
        if not points_for_bounds:
            self.full_points = []
            if self.plot:
                self.plot.points = []
            return
        self.full_points = sorted(points_for_bounds, key=lambda p: p[0])
        xs = [p[0] for p in self.full_points]
        ys = [p[1] for p in self.full_points]
        xmin, xmax = min(xs), max(xs)
        # On initial population (no prior user window), show the full data span so
        # the graph fills the window horizontally. If the user has already
        # modified the view, preserve their window instead (do not reset).
        try:
            is_initial = (getattr(self, '_xmin', None) == 0 and getattr(self, '_xmax', None) == 10 and not prev_has_points)
        except Exception:
            is_initial = False
        if is_initial:
            self._xmin = xmin
            self._xmax = xmax
        else:
            DEFAULT_WINDOW = 60
            self._xmax = xmax
            self._xmin = min(xmin, xmax - DEFAULT_WINDOW)
            if self._xmax - self._xmin < 1:
                self._xmin = self._xmax - 1

        # y bounds
        ymin, ymax = (min(ys), max(ys)) if ys else (0, 1)
        # prefer using the most recent (last) measurement as the reference high
        try:
            last_y = ys[-1]
            if last_y is not None:
                ymax = max(ymax, last_y)
        except Exception:
            pass
        # force baseline at zero for all keys except pH measurements
        key_lower = (self.key or "").lower()
        if key_lower not in ("ph", "soil_ph"):
            # enforce y axis starts at 0 (show values from 0..max)
            ymin = 0.0
        else:
            # For pH graphs, use a fixed, meaningful range to avoid autoscale issues
            ymin = 5.0
            ymax = 7.0
        # avoid zero span
        if ymin == ymax:
            # keep small padding
            if key_lower in ("ph", "soil_ph"):
                ymin -= 0.5
                ymax += 0.5
            else:
                # for non-pH, ensure visible span around value and include zero
                ymax = max(ymax, ymin + 1.0)

        self.graph.xmin = self._xmin
        self.graph.xmax = self._xmax
        self.graph.ymin = ymin
        self.graph.ymax = ymax

        # choose a "nice" major tick for y axis so non-pH graphs show at most 5 values
        # (4 intervals). pH graphs are handled separately below.
        y_range = float(self.graph.ymax) - float(self.graph.ymin)
        intervals = 4
        if y_range <= 0:
            self.graph.y_ticks_major = 1
        else:
            tick = self._compute_nice_tick(float(self.graph.ymin), float(self.graph.ymax))
            self.graph.y_ticks_major = tick
        if key_lower in ("ph", "soil_ph"):
            self.graph.y_ticks_major = 0.5
            self.graph.ymin = 5.0
            self.graph.ymax = 7.0
        if key_lower == "main_stem_number":
            self.graph.y_ticks_major = 1
            self.graph.ymin = math.floor(float(self.graph.ymin))
            self.graph.ymax = math.ceil(float(self.graph.ymax))
        tick = float(getattr(self.graph, "y_ticks_major", 0) or 0)
        if tick > 0:
            top = float(self.graph.ymax)
            aligned_top = math.ceil((top - 1e-9) / tick) * tick
            self.graph.ymax = aligned_top

        # set visible plot points: prefer plotting raw/original points (points_for_plot)
        if self.plot:
            pf = points_for_plot or []
            self.plot.points = [(x, y) for x, y in pf]
            # remember last provided plot-series so marker placement can use
            # the original data-space points (avoids double-scaling issues)
            try:
                self._last_series_map = {self.key: list(pf)}
            except Exception:
                self._last_series_map = {self.key: []}
        self._update_y_labels()

    def scroll(self, frac):
        if not self.full_points:
            return

        total_min = min(p[0] for p in self.full_points)
        total_max = max(p[0] for p in self.full_points)
        win = self._xmax - self._xmin
        delta = win * frac
        new_min = max(total_min, min(total_max - win, self._xmin + delta))
        new_max = new_min + win
        self._xmin, self._xmax = new_min, new_max
        self.graph.xmin = self._xmin
        self.graph.xmax = self._xmax


    def zoom(self, factor):
        """factor <1 zoom in, >1 zoom out; center-preserving."""
        if not self.full_points:
            return

        total_min = min(p[0] for p in self.full_points)
        total_max = max(p[0] for p in self.full_points)
        center = (self._xmin + self._xmax) / 2.0
        half = (self._xmax - self._xmin) / 2.0 * factor
        new_min = max(total_min, center - half)
        new_max = min(total_max, center + half)
        # clamp if inverted
        if new_max - new_min < 1:
            new_min = max(total_min, center - 0.5)
            new_max = new_min + 1
        self._xmin, self._xmax = new_min, new_max
        self.graph.xmin = self._xmin
        self.graph.xmax = self._xmax


    # Drag-to-pan handlers
    def _on_graph_touch_move(self, graph, touch):
        try:
            # only handle if this touch was grabbed by this widget instance
            if getattr(touch, "grab_current", None) is not self:
                return False
            # compute horizontal movement in pixels
            if not hasattr(self, "_drag_start_pos") or self._drag_start_pos is None:
                return False
            dx = touch.pos[0] - self._drag_start_pos[0]
            # convert pixels to day units
            width = float(self.graph.width) or 1.0
            span = float(self._xmax - self._xmin) or 1.0
            days_per_pixel = span / width
            frac = - (dx * days_per_pixel) / span if span != 0 else 0
            # apply scroll by fraction
            self.scroll(frac)
            # update stored start pos to allow smooth dragging
            self._drag_start_pos = touch.pos
            # sync other graphs in same tab
            try:
                if getattr(self, "_owner", None):
                    self._owner._sync_graphs_to(self)
            except Exception:
                pass
            return True
        except Exception:
            return False

    def _on_graph_touch_up(self, graph, touch):
        try:
            if getattr(touch, "grab_current", None) is self:
                try:
                    touch.ungrab(self)
                except Exception:
                    pass
            self._drag_start_pos = None
            # final sync after drag ends
            try:
                if getattr(self, "_owner", None):
                    self._owner._sync_graphs_to(self)
            except Exception:
                pass
            return False
        except Exception:
            return False

    def show_x_labels(self, base_date=None, enabled=True, fmt="%Y-%m-%d"):
        """Populate the bottom x-axis label row with formatted date strings.
        `base_date` is a datetime used to convert day-number x values back to dates.
        """
        try:
            # if disabling, clear immediately
            if not enabled:
                if self._scheduled_x_update is not None:
                    try:
                        self._scheduled_x_update.cancel()
                    except Exception:
                        pass
                    self._scheduled_x_update = None
                # remove any canvas-drawn label rectangles
                try:
                    for r in list(self._label_rects):
                        try:
                            self.graph.canvas.after.remove(r)
                        except Exception:
                            pass
                    self._label_rects = []
                except Exception:
                    pass
                self._x_label_row.clear_widgets()
                self._x_label_row.height = 0
                return
            if base_date is None:
                return

            # enable drawing of canvas labels by setting current base/format and scheduling a redraw
            self._current_base_date = base_date
            self._current_fmt = fmt
            # reserve vertical space for labels under the graph
            try:
                app = App.get_running_app()
                fs = 12
                try:
                    s = app.theme.body_size
                    if isinstance(s, (int, float)):
                        fs = s
                    elif isinstance(s, str) and s.endswith("sp"):
                        fs = float(s[:-2])
                    else:
                        fs = float(s)
                except Exception:
                    fs = 12
                # give a little padding
                self._x_label_row.height = int(max(20, fs + 8))
            except Exception:
                try:
                    self._x_label_row.height = 24
                except Exception:
                    pass
            if self._scheduled_x_update is not None:
                try:
                    self._scheduled_x_update.cancel()
                except Exception:
                    pass
            self._scheduled_x_update = Clock.schedule_once(self._draw_grid, 0)
        except Exception:
            pass


class TimelineScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.plant = None
        self.tab_graphs = {
            "plant": [],
            "environment": [],
            "water": [],
            "food": []
        }
        # store base date per tab for x-label formatting
        self._tab_base_date = {}
        # food tab relative/absolute toggle state and cached full mapping
        self._food_relative = False
        self._last_food_full_map = None
        # cached absolute y-scale for food graphs (so toggling doesn't rescale Y)
        self._last_food_ymin = None
        self._last_food_ymax = None
        self._last_food_y_tick = None
        timeline_view = WrapperBox(orientation="horizontal")
        spacer_left = SpacerBox(size_hint_x=0.2)
        timeline_view.add_widget(spacer_left)
        stripes_holder = WrapperBox(orientation="horizontal")
        stripe_0 = ContentBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_0)
        stripe_1 = RedBox(); stripes_holder.add_widget(stripe_1)
        stripe_2 = YellowBox(); stripes_holder.add_widget(stripe_2)
        stripe_3 = GreenBox(); stripes_holder.add_widget(stripe_3)
        stripe_4 = ContentBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_4)
        spacer_left.add_widget(stripes_holder)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        title = TitleLabel(text=f"Just look at this [color={TitleLabel().hex_color}]BEAUTY[/color]")
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.2)
        spacer_left.add_widget(spacer_vertical)

        content = WrapperBox(orientation="vertical")
        timeline_view.add_widget(content)
        
        self.header = WrapperBox(orientation="horizontal", size_hint_y=0.2)
        content.add_widget(self.header)
        
        title_box = ContentBox(orientation="vertical")
        self.header.add_widget(title_box)
        spacer_box = SpacerBox(size_hint_y=0.2)
        title_box.add_widget(spacer_box)
        
        name_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        self.name_label = FieldLabel(text="", valign="middle", halign="left")
        self.name_label.font_size = app.theme.subtitle_size
        self.name_label.color = app.theme.color_field_value
        name_box.add_widget(self.name_label)
        title_box.add_widget(name_box)

        strain_box = ContentBox(orientation="horizontal", size_hint_y=0.3)
        self.strain_label = FieldLabel(text="", valign="middle", halign="left")
        self.strain_label.font_size = app.theme.logo_size_2
        self.strain_label.color = app.theme.color_field_value

        strain_box.add_widget(self.strain_label)
        title_box.add_widget(strain_box)

        # Tabbed panel
        self.tabbed_panel = TabbedPanel(do_default_tab=False, size_hint_y=0.8, size_hint_x=1.0)

        self._create_tab("Plant", "plant", ["plant_height", "num_nodes", "node_spacing", "main_stem_number"], app.theme.color_tab_plant)
        self._create_tab("Environment", "environment", ["air_temp_c", "rh_percent", "soil_moisture", "soil_ph", "vpd_kpa", "ppfd"], app.theme.color_tab_environment)
        self._create_tab("Water", "water", ["volume_l", "water_temp_c", "ph", "ppm"], app.theme.color_tab_water)
        self._create_tab("Food", "food", ["grow_mix","root_mix","bloom_mix","bloom_boost","soil_boost","vit_boost","CalMag"], app.theme.color_tab_food)

        # compute initial heights so graphs fill the window reasonably
        self._update_graph_heights()

        content.add_widget(self.tabbed_panel)
        footer = SpacerBox(size_hint_y=0.1)
        buttons = ContentBox(size_hint_y=0.66)
        go_back_btn = ButtonRed(text="Back")
        go_back_btn.bind(on_release=app.go_back)
        buttons.add_widget(go_back_btn)
        footer.add_widget(buttons)
        content.add_widget(footer)

        right = SpacerBox(size_hint_x=0.1)
        timeline_view.add_widget(right)

        self.add_widget(timeline_view)
        Window.bind(on_mouse_scroll=self._on_mouse_scroll, on_scroll=self._on_mouse_scroll)
        Window.bind(size=self._on_window_resize)

    def _update_ui(self):
        app = App.get_running_app()
        plant = self.plant or {}


        self.genes = plant.get("genes", "")
        self.name_label.text = " | ".join([plant.get("name", ""), self.genes])

        self.strain_label.text = plant.get("strain", "")
        genes = (self.genes or "").strip().lower()
        if genes == "sativa":
            self.strain_label.color = app.theme.color_strain_sativa
        elif genes == "indica":
            self.strain_label.color = app.theme.color_strain_indica
        elif genes == "hybrid":
            self.strain_label.color = app.theme.color_strain_hybrid
        else:
            self.strain_label.color = app.theme.color_strain_unknown
    def _create_tab(self, title_text, tab_key, keys, color):
        app = App.get_running_app()
        tab = TabbedPanelItem(text=title_text)
        container = ContentBox(orientation="vertical", size_hint_y=1)
        if tab_key == "food":
            g = SimpleGraph(key=None, color=color, owner=self, tab_key=tab_key, multi_keys=keys)
            container.add_widget(g)
            self.tab_graphs[tab_key].append(g)
            btn_row = WrapperBox(orientation="horizontal", size_hint_y=None, height=36)
            for mk in keys:
                title = mk.replace("_", " ").title()
                btn = GraphButton(text=title, state='down')
                # set button color to match the corresponding plot color
                try:
                    lp = g.plots.get(mk)
                    # copy the color values so buttons don't share the same mutable list
                    if lp is not None and getattr(lp, 'color', None) is not None:
                        col = list(lp.color)
                    else:
                        col = list(app.theme.color_label_title)
                except Exception:
                    col = list(app.theme.color_label_title)

                # initial visuals
                btn.background_color = app.theme.color_transparent
                btn.color = app.theme.color_label_title

                # update visuals when toggled
                # capture the color for this iteration in the default arg to avoid
                # late-binding to the loop variable which would make all buttons
                # use the final color (observed as all purple after retoggle).
                def _state_cb(inst, value, _col=col):
                    try:
                        if value == 'down':
                            inst.background_color = list(_col)
                            inst.color = app.theme.color_button_on_color_text
                        else:
                            inst.background_color = list(app.theme.color_transparent)
                            inst.color = app.theme.color_label_title
                    except Exception:
                        pass

                btn.bind(state=_state_cb)

                def _make_cb(mkey):
                    def _cb(inst):
                        visible = inst.state == 'down'
                        g._plot_visible[mkey] = visible
                        lp = g.plots.get(mkey)
                        if lp is None:
                            return
                        if visible:
                            # prefer raw/original points when restoring visibility
                            last = (getattr(g, "_last_series_map", {}) or {})
                            raw_map = last.get('_raw', {}) or {}
                            pts_raw = raw_map.get(mkey, [])
                            pts = pts_raw if pts_raw else last.get(mkey, [])
                            if pts:
                                lp.points = [(x, y) for x, y in sorted(pts, key=lambda p: p[0])]
                        else:
                            lp.points = []
                    return _cb

                btn.bind(on_release=_make_cb(mk))
                # apply initial state visuals
                _state_cb(btn, btn.state)
                btn_row.add_widget(btn)
            container.add_widget(btn_row)

            # Add Relative/Absolute toggle on the right side
            rel_btn = GraphButton(text='Absolute', state='normal')
            rel_btn.background_color = app.theme.color_transparent
            rel_btn.color = app.theme.color_label_title
            def _rel_state_cb(inst, value):
                try:
                    if value == 'down':
                        inst.text = 'ml Per liter'
                        self._food_relative = True
                    else:
                        inst.text = 'ml'
                        self._food_relative = False
                    last = getattr(self, '_last_food_full_map', None)
                    if last is None:
                        return
                    if self._food_relative:
                        transformed = self._apply_food_relative(copy.deepcopy(last))
                    else:
                        transformed = copy.deepcopy(last)
                    try:
                        self._apply_and_preserve_x(g, transformed)
                    except Exception:
                        g.set_series(transformed)

                    # maintain absolute y-scale across toggles when available
                    try:
                        if not self._food_relative and getattr(g, 'graph', None) is not None:
                            # we're in absolute mode: record current y-scale
                            self._last_food_ymin = float(g.graph.ymin)
                            self._last_food_ymax = float(g.graph.ymax)
                            self._last_food_y_tick = float(getattr(g.graph, 'y_ticks_major', 0) or 0)
                        elif self._food_relative and self._last_food_ymin is not None and self._last_food_ymax is not None:
                            # apply stored absolute y-scale to relative view
                            g.graph.ymin = float(self._last_food_ymin)
                            g.graph.ymax = float(self._last_food_ymax)
                            if self._last_food_y_tick is not None:
                                g.graph.y_ticks_major = float(self._last_food_y_tick)
                            g._update_y_labels()
                    except Exception:
                        pass
                except Exception:
                    pass
            rel_btn.bind(state=_rel_state_cb)
            btn_row.add_widget(rel_btn)
        else:
            for k in keys:
                g = SimpleGraph(k, color, owner=self, tab_key=tab_key)
                container.add_widget(g)
                self.tab_graphs[tab_key].append(g)
        tab.add_widget(container)
        self.tabbed_panel.add_widget(tab)

    def _on_window_resize(self, window, size):
        self._update_graph_heights()

    def _update_graph_heights(self):
        for graphs in self.tab_graphs.values():
            self._update_graph_heights_for_list(graphs)

    def _update_graph_heights_for_list(self, graphs):
        if not graphs:
            return
        reserved = Window.height / 3
        avail = max(200, Window.height - reserved)
        per = max(100, int(avail / len(graphs)))
        for g in graphs:
            g.size_hint_y = None
            g.height = per

    def _sync_graphs_to(self, source_graph):
        for tab_key, graphs in self.tab_graphs.items():
            if source_graph in graphs:
                for g in graphs:
                    g._xmin = source_graph._xmin
                    g._xmax = source_graph._xmax
                    g.graph.xmin = g._xmin
                    g.graph.xmax = g._xmax
                base = self._tab_base_date.get(tab_key)
                if base is not None and graphs:
                    bottom = graphs[-1]
                    bottom.show_x_labels(base, enabled=True)
                return

    def load_plant(self, plant):
        self.plant = plant
        plant_id = plant.get("id")
        data = load_plant_events(plant_id)
        events = data.get("events", []) if data else []
        series_map, base_date = self._prepare_series(events)
        mapping = {
            "plant": ["plant_height", "num_nodes", "node_spacing", "main_stem_number"],
            "environment": ["air_temp_c", "rh_percent", "soil_moisture", "soil_ph", "vpd_kpa", "ppfd"],
            "water": ["volume_l", "water_temp_c", "ph", "ppm"],
            "food": ["grow_mix","root_mix","bloom_mix","bloom_boost","soil_boost","vit_boost","CalMag"]
        }
        for tab_key, keys in mapping.items():
            graph_widgets = self.tab_graphs.get(tab_key, [])
            if tab_key == "food":
                if graph_widgets:
                    g = graph_widgets[0]
                    # include volume_l in the full mapping (needed for per-L computations)
                    full = {k: series_map.get(k, []) for k in keys}
                    full['volume_l'] = series_map.get('volume_l', [])
                    raw_map = {k: series_map.get('_raw', {}).get(k, []) for k in keys}
                    raw_map['volume_l'] = series_map.get('_raw', {}).get('volume_l', [])
                    full['_raw'] = raw_map
                    # cache full mapping for toggle handling
                    self._last_food_full_map = copy.deepcopy(full)
                    # If this graph hasn't been initialized by the user (default tiny window),
                    # apply the series normally so it uses the wider default window logic.
                    try:
                        uninitialized = (getattr(g, '_xmin', None) == 0 and getattr(g, '_xmax', None) == 10 and not getattr(g, 'full_points', None))
                    except Exception:
                        uninitialized = False

                    if getattr(self, '_food_relative', False):
                        # toggling to relative: preserve x-window if the user has changed it
                        self._apply_and_preserve_x(g, self._apply_food_relative(copy.deepcopy(full)))
                        # ensure we use the absolute y-scale if we have it
                        if self._last_food_ymin is not None and self._last_food_ymax is not None:
                            try:
                                g.graph.ymin = float(self._last_food_ymin)
                                g.graph.ymax = float(self._last_food_ymax)
                                if self._last_food_y_tick is not None:
                                    g.graph.y_ticks_major = float(self._last_food_y_tick)
                                g._update_y_labels()
                            except Exception:
                                pass
                    else:
                        if uninitialized:
                            # first-time apply: let set_series compute the default wider window
                            g.set_series(copy.deepcopy(full))
                        else:
                            self._apply_and_preserve_x(g, copy.deepcopy(full))
                        # record absolute y-scale from the freshly-applied absolute data
                        try:
                            self._last_food_ymin = float(g.graph.ymin)
                            self._last_food_ymax = float(g.graph.ymax)
                            self._last_food_y_tick = float(getattr(g.graph, 'y_ticks_major', 0) or 0)
                        except Exception:
                            self._last_food_ymin = None
                            self._last_food_ymax = None
                            self._last_food_y_tick = None
            else:
                for i, k in enumerate(keys):
                    if i < len(graph_widgets):
                        pts_map = {k: series_map.get(k, [])}
                        pts_map['_raw'] = {k: series_map.get('_raw', {}).get(k, [])}
                        graph_widgets[i].set_series(pts_map)
            self._tab_base_date[tab_key] = base_date
            graph_widgets = self.tab_graphs.get(tab_key, [])
            if graph_widgets and base_date is not None:
                bottom = graph_widgets[-1]
                bottom.show_x_labels(base_date, enabled=True)
            self._update_ui()
        # After applying all series, schedule a post-layout refresh to ensure graphs
        # pick up the parent widths and redraw correctly (fixes graphs not filling
        # the available horizontal space on initial load/toggle).
        def _post_apply_refresh(_dt):
            for graphs in self.tab_graphs.values():
                for g in graphs:
                    try:
                        # re-apply computed window to graph (in case layout changed)
                        g.graph.xmin = g._xmin
                        g.graph.xmax = g._xmax
                        g._schedule_grid_update()
                    except Exception:
                        pass
        try:
            Clock.schedule_once(_post_apply_refresh, 0)
        except Exception:
            pass

    def set_plant(self, plant):
        if plant is None:
            return
        if isinstance(plant, dict):
            self.load_plant(plant)
            return
        from kivy.app import App as _App
        app = _App.get_running_app()
        garden_id = getattr(app, 'current_garden_id', None)
        plants = get_plants_for_garden(garden_id) if garden_id else []
        for p in plants:
            if str(p.get("id")) == str(plant):
                self.load_plant(p)
                return

    def update_timeline(self, plant_id):
        from kivy.app import App as _App
        app = _App.get_running_app()
        garden_id = getattr(app, 'current_garden_id', None)
        plants = get_plants_for_garden(garden_id) if garden_id else []
        for p in plants:
            if str(p.get("id")) == str(plant_id):
                self.load_plant(p)
                return

    def _prepare_series(self, events):
        dates = []
        parsed = []
        for e in events:
            ts = e.get("ts")
            if not ts:
                continue
            dt = datetime.strptime(ts, "%Y-%m-%d")
            parsed.append((dt, e))
            dates.append(dt)
        if not dates:
            return {}, {}
        base = min(dates)
        def daynum(dt):
            return (dt - base).days
        mapping = {}
        raw_mapping = {}
        sm_map = {"dust":0, "dry":1, "moist":2, "wet":3, "soaked":4}
        for dt, e in parsed:
            x = daynum(dt)
            plant_vals = e.get("plant", {})
            env_vals = e.get("environment", {})
            feeding = e.get("feeding", {})
            candidates = {}
            # include plant and environment nested values always
            candidates.update(plant_vals)
            candidates.update(env_vals)
            # include water-related top-level fields only for watering/planting events
            ev_type = (e.get("type") or "").lower()
            if ev_type in (EVENT_WATERING, EVENT_PLANTING, EVENT_FEEDING):
                for k in ("volume_l", "water_temp_c", "ph", "ppm"):
                    if k in e:
                        candidates[k] = e.get(k)
            # include feeding nested values only for feeding events
            if ev_type == EVENT_FEEDING:
                candidates.update(feeding if isinstance(feeding, dict) else {})
            for k, v in candidates.items():
                if v is None:
                    continue
                if k == "soil_moisture":
                    if isinstance(v, str):
                        y = sm_map.get(v.lower(), None)
                        if y is None:
                            continue
                    else:
                        y = float(v)
                else:
                    try:
                        y = float(v)
                    except Exception:
                        continue
                mapping.setdefault(k, []).append((x, y))
                raw_mapping.setdefault(k, []).append((x, y))
        # Normalize series for watering/feeding so missing days show explicit 0s.
        try:
            all_days = set()
            for dt in dates:
                all_days.add(daynum(dt))
            if all_days:
                min_day = min(all_days)
                max_day = max(all_days)
            else:
                min_day = 0
                max_day = 0
            # keys representing water volumes and feeding amounts that should be zero-filled
            zero_fill_keys = set([
                "volume_l",
                # feeding keys
                "grow_mix", "root_mix", "bloom_mix", "bloom_boost", "soil_boost", "vit_boost", "CalMag",
            ])
            for k in zero_fill_keys:
                # build day->value mapping for existing points
                pts = mapping.get(k, [])
                day_map = {int(x): y for x, y in pts}
                filled = []
                for d in range(min_day, max_day + 1):
                    y = day_map.get(d, 0.0)
                    filled.append((d, float(y)))
                mapping[k] = filled
        except Exception:
            pass
        # attach raw (original) series so callers can plot only real points
        try:
            mapping['_raw'] = raw_mapping
        except Exception:
            mapping['_raw'] = {}
        return mapping, base

    def _apply_food_relative(self, full):
        """Return a transformed copy of `full` where food nutrient values are divided by volume_l per day.
        `full` is expected to contain nutrient series lists and a 'volume_l' filled series and a '_raw' dict.

        Behavior:
        - Prefer raw nutrient points when available (so we don't divide zero-filled series when a nutrient
          wasn't applied that day).
        - For each day, divide nutrient amount by the day's volume_l. If the day's volume is missing or zero,
          fall back to the nutrient's absolute amount (do not replace with 0.0).
        """
        try:
            food_keys = ["grow_mix","root_mix","bloom_mix","bloom_boost","soil_boost","vit_boost","CalMag"]
            # filled volume per day (day -> volume)
            vol_filled = {int(x): float(y) for x, y in (full.get('volume_l') or [])}
            raw_map = (full.get('_raw') or {}) or {}
            raw_vol_map = {int(x): float(y) for x, y in (raw_map.get('volume_l') or [])}
            new_full = {}
            # keep volume series as-is
            new_full['volume_l'] = list(full.get('volume_l') or [])

            # Build a day->value mapping for nutrient raw points (prefer raw when present)
            for k in food_keys:
                # build day->value mapping from filled series then overlay raw points
                day_map = {int(x): float(y) for x, y in (full.get(k) or [])}
                for x, y in (raw_map.get(k) or []):
                    day_map[int(x)] = float(y)

                new_pts = []
                # iterate through days for which we have a volume (preserves filled day sequence)
                days = sorted(vol_filled.keys()) if vol_filled else sorted(day_map.keys())
                for d in days:
                    val = day_map.get(d, 0.0)
                    try:
                        vol = vol_filled.get(int(d), None)
                        if vol and float(vol) != 0.0:
                            new_y = float(val) / float(vol)
                        else:
                            # fallback to absolute amount when volume missing/zero
                            new_y = float(val)
                    except Exception:
                        new_y = float(val or 0.0)
                    new_pts.append((d, new_y))
                new_full[k] = new_pts

            # transform raw series (preserve original sparse points but convert where possible)
            new_raw = {}
            for k in food_keys:
                pts = list((raw_map.get(k) or []))
                new_pts = []
                for x, y in pts:
                    try:
                        d = int(x)
                        vol = raw_vol_map.get(d, None)
                        if vol is None:
                            vol = vol_filled.get(d, None)
                        if vol and float(vol) != 0.0:
                            new_y = float(y) / float(vol)
                        else:
                            new_y = float(y)
                    except Exception:
                        new_y = float(y or 0.0)
                    new_pts.append((x, new_y))
                new_raw[k] = new_pts
            new_full['_raw'] = new_raw
            return new_full
        except Exception:
            return full

    def _apply_and_preserve_x(self, g, mapping):
        """Set `mapping` on graph `g` while preserving the current x-window (center and width) when possible."""
        try:
            prev_min = getattr(g, '_xmin', None)
            prev_max = getattr(g, '_xmax', None)
            # if graph appears uninitialized (default 0..10 and no points) then
            # treat this as an initial population and let set_series fill entire span
            try:
                uninitialized = (prev_min == 0 and prev_max == 10 and not getattr(g, 'full_points', None))
            except Exception:
                uninitialized = False
            if uninitialized:
                g.set_series(mapping)
                return
            # compute old window width
            win = None
            if prev_min is not None and prev_max is not None:
                win = float(prev_max) - float(prev_min)
            # apply new series
            g.set_series(mapping)
            # if there's no previous window info, keep default result
            if win is None:
                return
            # compute total available span from mapping
            all_x = []
            for k, pts in mapping.items():
                if k == '_raw':
                    continue
                try:
                    all_x.extend([p[0] for p in pts if pts])
                except Exception:
                    pass
            if not all_x:
                return
            tmin = min(all_x)
            tmax = max(all_x)
            # if available span is smaller than desired window, just use full span
            if (tmax - tmin) <= win:
                new_min = float(tmin)
                new_max = float(tmax)
            else:
                # preserve center where possible
                center = (prev_min + prev_max) / 2.0
                new_min = max(tmin, min(center - win / 2.0, tmax - win))
                new_max = new_min + win
            g._xmin, g._xmax = new_min, new_max
            g.graph.xmin = new_min
            g.graph.xmax = new_max
        except Exception:
            try:
                g.set_series(mapping)
            except Exception:
                pass

    def _on_mouse_scroll(self, window, *args):
        x = y = scroll_x = scroll_y = 0
        if len(args) >= 4:
            x, y, scroll_x, scroll_y = args[0], args[1], args[2], args[3]
        elif len(args) == 1:
            ev = args[0]
            scroll_x = getattr(ev, "scroll_x", 0) or getattr(ev, "sx", 0) or 0
            scroll_y = getattr(ev, "scroll_y", 0) or getattr(ev, "sy", 0) or 0
        raw_mods = getattr(Window, "modifiers", None)
        if raw_mods is None:
            raw_mods = getattr(Window, "_modifiers", None)
        mods = [m.lower() for m in (raw_mods or [])]
        active_text = (self.tabbed_panel.current_tab.text or "").lower()
        key = "plant" if "plant" in active_text else ("environment" if "environment" in active_text else ("water" if "water" in active_text else ("food" if "food" in active_text else None)))
        graphs = self.tab_graphs.get(key, [])
        if not graphs:
            return False
        if "shift" in mods:
            factor = 0.8 if scroll_y > 0 else 1.25
            for g in graphs:
                g.zoom(factor)
        else:
            frac = -0.1 if scroll_y > 0 else 0.1
            for g in graphs:
                g.scroll(frac)
        return True

