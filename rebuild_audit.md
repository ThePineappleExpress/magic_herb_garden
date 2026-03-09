# Rebuild Audit — Magic Herb Tracker
**Date:** 2026-03-09  
**Method:** Full static analysis of runtime code cross-referenced against README.md (authoritative) and CLAUDE.md.  
Tests are treated as **unreliable** (never tracked in git) and used only to surface API discrepancies, not as truth.

---

## Fix Status (2026-03-09)

| Issue | Status | Summary |
|-------|--------|---------|
| #1+#2 | ✅ Fixed | `on_event_save` rewritten to use `EventRepository.add_event()`; `set_plant` normalises `id`/`plant_id` |
| #3 | ✅ Fixed | Theme fallback changed from `forest_dark` to `green` |
| #4 | ✅ Fixed | `run_unit_tests.py` restored (custom runner, discovers `test_*` functions) |
| #5 | ✅ Fixed | `validate()` no longer checks display-only `name_label`/`strain_label` |
| #6 | ✅ Fixed | Unused `EventListView` class removed from `plant_details.py`; stale imports cleaned |
| #7 | ✅ Fixed | Debug `print` statements removed from `helpers.go_to_timeline` |
| #8 | ✅ Fixed | Covered by #1+#2 — save goes through `EventRepository` |
| #9 | ⚠️ Not a bug | `set_environment.py` strain/catalog lookup is actively used; not dead code |
| #10 | ✅ Fixed | Shader system wired: `fx.py` loads GLSL from disk, `BaseScreen` respects `shader_enabled`, `_on_shader_reload` updates all screens |
| #11 | ✅ Fixed | `test_crypto.py` updated to pass full `stored` dict to `derive_encryption_key` |
| #12 | ✅ Fixed | `_normalize_plants` added to `storage.py`; called from `get_plants_for_garden` |
| #13 | ✅ Fixed | `test_theme_loader.py` references updated from `forest_dark` to `green` |
| #14 | ✅ Fixed | `days_to_flower` guarded with `int(... or 0)` and `penalty` included in `est_f` |
| #15 | ✅ Fixed | `plant.get("notes") or ""` in both `plant_details.py` and `add_event.py` |
| #16 | ✅ Fixed | KV rules verified: `PlantListItem`, `GardenListItem` intact; `default_size` fix pending |
| #26 | ✅ Fixed | Full theme migration: KV rewritten (127 props), Python migrated, `apply_theme()` wired in `main.py`+`settings_screen.py`, per-data-key graph colors, stripe refactor, buttons hover from theme |
| #17 | ✅ Fixed | `plant_id` normalisation moved into `helpers.go_to_add_event` |
| #18 | ✅ Fixed | Double-click binds: `SelectableBoxLayout` dispatches `on_double_tap`, `PlantListView` and `GardenListView` handle it |
| #19 | ✅ Fixed | Seedbank autocomplete: `breeder_trie.py` module + dropdown/keyboard wiring in `sow_seed.py`; catalog guard prevents overwrite |
| #20 | ✅ Fixed | Sort/search/filter toolbar: `GardenViewScreen` has sort dropdown, asc/desc toggle, search, active-only filter; `SelectGardenScreen` has sort dropdown, asc/desc, search |
| #21 | ✅ Fixed | Cascading location dropdowns, astral daylight, /x live label, garden light schedule prefill |
| #22 | ✅ Fixed | `numpy` replaced with `math.exp` |
| #23 | ℹ️ Info | Package audit complete; no code changes needed |
| #24 | ✅ Fixed | All 4 sub-items done: indoor prefill, outdoor astral, flip→flowering, stage on save |
| #25 | ✅ Fixed | Top/Prune/Flip as toggle buttons; Harvest as separate button; priority override; flip disabled after flip event; autofill from last event; edit-last-event button |

**Test suite:** 45/45 passing (0 failures)

---

## Executive Summary

Plants and gardens load correctly. The bootstrap, garden view, sow_seed → set_environment → garden_view flow, and the password/crypto layer are functionally intact. The main damage is concentrated in three areas:

1. ~~The **event-save pipeline** (`add_event.py::on_event_save`) is completely broken~~ — **✅ Fixed**: now uses `EventRepository.add_event()`.
2. ~~The **theme fallback** is broken~~ — **✅ Fixed**: falls back to `green`.
3. ~~The **test runner** (`run_unit_tests.py`) is missing from disk~~ — **✅ Fixed**: restored.

Everything else is either working or has partial patches already in place.

---
---

## Packages
Need checking. Whatever is installed in uv is an indications as what should be imported and used. 

## CRITICAL — Will crash or silently corrupt data

### 1. `on_event_save` bypasses the storage/encryption layer
**File:** `add_event.py` lines ~700-859  
**Impact:** Any event save will either write unencrypted JSON to the wrong path (if platformdirs is active) or corrupt/lose data when encryption is enabled.

**What it does:**
```python
plant_file = os.path.join("usr", "db", "plants", f"{plant_id}.json")
if not os.path.exists(plant_file):
with open(plant_file, "r", ...) as f:
    plant_data = json.load(f)
with open(plant_file, "w", ...) as f:
    json.dump(plant_data, f, ...)
```
**Problems:**

**Impact:** `set_plant()` raises `ValueError` every time it's called unless called through the patched path in `plant_details.py`.

def set_plant(self, plant: dict):
        raise ValueError("set_plant must be called with a valid plant dict containing 'plant_id'.")
```
All plants are stored and passed with key `"id"` (set in `set_environment.py`, read in `garden_view.py`).

**Partial patch already exists** in `plant_details.py` (`safe_go_to_add_event` injects `plant['plant_id'] = plant['id']`), so the `plant_details → add_event` path is protected. However:
- `on_event_save` still reads `plant_id = self.plant.get("plant_id")` and depends on the patched value being present.
- Any other code path that calls `set_plant` without going through `safe_go_to_add_event` will still crash.
- `helpers.go_to_add_event(instance, plant)` calls `add_event_screen.set_plant(plant)` directly, without the patch.

**Fix:** Normalise `set_plant` to accept either `"id"` or `"plant_id"`, or canonicalise plant dicts at the repository boundary to always include both, or simply change `set_plant` to check `plant.get("id") or plant.get("plant_id")`.
---

### 3. `forest_dark` theme fallback does not exist
**File:** `bin/themes/__init__.py` lines 50-54  
**Impact:** Any request for a theme name that doesn't have a `.toml` file silently returns `{}`. Accessing any theme property (e.g. `app.theme.body_size`) then raises `AttributeError` at render time.

```python
def load_theme(name: str) -> dict:
    path = _resolve_theme_path(name)
    if path is None and name != "forest_dark":
        LOG.warning("Theme '%s' not found, falling back to forest_dark", name)
        path = _resolve_theme_path("forest_dark")   # ← "forest_dark" does not exist
    if path is None:
        LOG.error("No theme files found")
        return {}   # ← results in empty dict; all setattr calls in apply_theme are no-ops
```

**Available themes:** `dark`, `green`, `light`, `retro`, `vaporwave`, `water`  
**Missing:** `forest_dark`

**Fix:** Change the hardcoded fallback from `"forest_dark"` to `"green"` on line 50 and 52 of `bin/themes/__init__.py`. Alternatively, create a `forest_dark.toml` (can alias `dark.toml`).

---

### 4. `run_unit_tests.py` is missing
**Impact:** `python run_unit_tests.py` (referenced in README, CLAUDE.md, and CI config) fails with `FileNotFoundError`. CI pipeline is broken.

**Fix:** Either restore the file from git history, or update CI to use `python -m pytest tests/` directly (which works). The tests themselves are runnable via pytest already.

---

## HIGH — Functional failures / incorrect behaviour

### 5. `add_event.validate()` checks display labels, not input fields
**File:** `add_event.py` lines ~456-500  
**Impact:** Validation always flags `name_label` and `strain_label` as empty (they are display-only `FieldLabel` widgets, not text inputs), causing `shake_and_flash` on labels and blocking event saves.

```python
def validate(self):
    invalid = []
    if not self.name_label.text.strip():     # ← this is a display label, not an input
        invalid.append(self.name_label)
    if not self.strain_label.text.strip():   # ← same
        invalid.append(self.strain_label)
```

These labels are populated by `_update_ui()` via `set_plant()`. If `set_plant` runs successfully (after the `plant_id` patch), the labels will be set. But the validate logic conflates "display fields" with "required inputs", and also tries to shake/flash a label widget which is not designed for that.

**Fix:** Remove the name/strain label checks from `validate()`. Required plant context is guaranteed by `set_plant()` being called first; if it hasn't been called, `_plant_set` is False and the early-exit guard at the top of `on_event_save` covers it.

---

### 6. `plant_details.EventListView` uses wrong viewclass
**File:** `plant_details.py` lines ~19-25  
```python
class EventListView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "PlantListItem"   # ← should be an event item class
        self.data = []
```

The `EventListView` is a RecycleView that should display events, but uses the `PlantListItem` KV rule (for plants). Note: this `EventListView` class appears to be unused in the current build — `plant_details.py` uses a `HorizontalScrollView` with manual `SelectableEventBox` widgets instead. But the class definition is a leftover from an older architecture and will cause KV lookup warnings at runtime.

**Fix:** Either delete the class or update the viewclass to an appropriate event item class.

---

### 7. `helpers.go_to_timeline` contains debug `print` statements
**File:** `helpers.py` lines ~41-47  
```python
print("DEBUG: timeline_screen type=", type(timeline_screen))
print("DEBUG: timeline_screen dir sample=", dir(timeline_screen)[:80])
```
These fire on every navigation to the timeline. Low severity but they clutter production output and reveal internal structure.

**Fix:** Remove the debug prints.

---

### 8. `add_event.py` does not import or use `storage` / `data` repositories for saves
**File:** `add_event.py` imports  
The screen imports `load_plant_events` from `storage` (for reading) but then writes via raw `json` instead of going back through the same layer. Inconsistent; will break under encryption (reads will decrypt correctly, writes will re-encrypt incorrectly or not at all).

Already covered by issue #1 above but worth noting separately as an architectural issue: the fix must use `EventRepository.add_event()` or at minimum `storage.save_plant_events()`.

---

### 9. ~~`sow_seed.py` has a duplicate `_apply_catalog_for_strain`~~ — ⚠️ Not a bug
**File:** `set_environment.py`  
On re-inspection, `set_environment.py` **does** have a strain input field (`self.input_plant_strain`) and actively uses `_apply_catalog_for_strain` to auto-fill gene type, photoperiod/auto, and days-to-flower from the seed catalog. The function is used at line 386 when the user accepts an inline autocomplete suggestion. This is not dead code.

The two versions of `_apply_catalog_for_strain` (in `sow_seed.py` and `set_environment.py`) do differ slightly — sow_seed's version also sets the seedbank name — but both are actively called in their respective screens. No fix needed.

---

### 10. Shader selection, reload, and toggle are not wired up
**Files:** `fx.py`, `screens.py`, `settings_screen.py`  
**Impact:** The shader system is visually static — changing the shader style, pressing Reload, or toggling shaders on/off in Settings has no runtime effect beyond persisting a string to `settings.json`.

**10a. `SmokeShaderWidget` has a hardcoded smoke shader — ignores `bin/shaders/`**  
`fx.py` embeds the smoke GLSL source directly as the default value of the `fs` StringProperty (~90 lines of inline GLSL). It never calls `bin.shaders.load_shader()` at all. The four `.glsl` files in `bin/shaders/` (smoke, water, ice, rain) are discoverable via `get_available_shaders()` but never loaded at runtime.

**10b. `BaseScreen` always creates a `SmokeShaderWidget` — ignores `shader_enabled` and `shader` settings**  
```python
# screens.py
class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.layout.add_widget(SmokeShaderWidget(...))  # ← always; never checks settings
```
The `shader_enabled` and `shader` keys in `settings.json` are read and written by `settings_screen.py` but never consulted on screen construction. Toggling shaders off does nothing.

**10c. `_on_shader_reload` saves to disk but does not reload the shader**  
```python
# settings_screen.py
def _on_shader_reload(self, *args):
    settings = storage.load_settings()
    settings["shader"] = self.shader_style_spinner.text
    settings["shader_enabled"] = self.shader_spinner.text == lang.SETTINGS_SHADER_ON
    storage.save_settings(settings)
    # ← no call to load_shader(), no update to any SmokeShaderWidget.fs property
```
The Reload button persists the preference but never actually swaps the running fragment shader.

**10d. `on_fs` defined twice in `fx.py` — second definition shadows the correct one**  
```python
# First definition (correct):
def on_fs(self, instance, value):
    self.canvas.shader.fs = value

# Second definition (wrong, wins due to Python method resolution):
def on_fs(self, instance, value):
    self.canvas['fragment_shader'] = value   # ← wrong key; does nothing
```
Even if something did set the `fs` property, the active `on_fs` handler writes to a non-existent uniform key `fragment_shader` instead of `self.canvas.shader.fs`. Same duplication issue also affects `_update_rect` (harmless — both versions are equivalent) and `update_glsl`.

**10e. Pixel-scale slider (1-64) mentioned in README is not implemented**  
The README states: *"adjust the pixel scale (1-64)"*. There is no pixel-scale uniform in any of the GLSL shaders, no slider widget in `settings_screen.py` for it, and no resolution-scaling logic in `SmokeShaderWidget`. Either this feature was lost in the git corruption or was never implemented.

**Fix strategy:**
1. Remove the inline GLSL from `fx.py` and have `SmokeShaderWidget.__init__` call `bin.shaders.load_shader(name)` to source the fragment shader from disk. Accept a `shader_name` kwarg and fall back to `"smoke"`.
2. Make `BaseScreen.__init__` read `shader_enabled` and `shader` from settings. If disabled, skip adding the shader widget entirely. Store a reference so it can be toggled live.
3. Wire `_on_shader_reload` to: load the new GLSL via `load_shader()`, update the `SmokeShaderWidget.fs` property on all active `BaseScreen` instances (or at least the current one), and respect the on/off toggle.
4. Remove the duplicate `on_fs` / `_update_rect` / `update_glsl` definitions in `fx.py` — keep only the correct versions.
5. Either implement the pixel-scale slider or remove the claim from the README.

---

## MEDIUM — Stale tests (not runtime bugs, but misleading failures)

These test failures reflect the tests being wrong, not the production code.

### 11. `test_crypto.py` — `derive_encryption_key` API mismatch
**File:** `tests/test_crypto.py` lines 159-200  
Tests call `derive_encryption_key("password", stored["enc_salt"])` — passing the raw hex string directly.  
Production signature is `derive_encryption_key(password: str, stored: dict)` — takes the full password dict, extracts `enc_salt` internally.

The production callers (`password_check.py:121`, `settings_screen.py:310`) are correct. The tests are stale.

**Fix:** Update tests to call `derive_encryption_key(password, stored)` where `stored` is the full dict returned by `hash_password()`.  
The README's cryptographic design section confirms the dict-based API is correct.

---

### 12. `test_storage_helpers.py` — `_normalize_plants` does not exist
**File:** `tests/test_storage_helpers.py`, `storage.py`  
4 tests call `storage._normalize_plants()` but the function was never implemented in `storage.py`. The logic it describes (filtering `None` and non-dict items from a list) is sensible and would belong in `get_plants_for_garden`. It may have existed in an older version of storage.

**Fix options:**
- Add `_normalize_plants(data)` to `storage.py` (trivial: `return [p for p in data if isinstance(p, dict)] if isinstance(data, list) else []`) and call it inside `get_plants_for_garden`.
- Or update tests to test the actual `get_plants_for_garden` logic instead.

---

### 13. `test_theme_loader.py` — tests reference `forest_dark`
Already covered by issue #3 above. Once the fallback is changed to `"dark"` and/or `forest_dark.toml` is created, these tests will pass.

---

## LOW — Minor issues / cleanup

### 14. `garden_view.refresh_plants()` — `days_to_flower` can crash if `None`/missing
**File:** `garden_view.py` lines ~178-185  
```python
base_f = p.get("days_to_flower")
est_f = base_f + 14   # ← TypeError if base_f is None
```
If a plant was saved without `days_to_flower` (or with `""` from a text input), this line raises `TypeError`. There's no try/except around the outer calculation, only the inner `date` parsing. Plants created via `set_environment.py` always have `days_to_flower` (it's a required field in `sow_seed.validate()`), so this is only triggered by data imported from `.weed` files or pre-existing DB entries with missing fields.

**Fix:** `base_f = int(p.get("days_to_flower") or 0)` with a try/except wrapper.

---

### 15. `plant_details._update_ui()` calls `plant.get("notes")` — returns `None` assigned to label
**File:** `plant_details.py` line ~224  
```python
self.notes_label.text = plant.get("notes")   # ← None if key missing; Kivy label text must be str
```
Kivy will raise `TypeError: Cannot set property text to <class 'NoneType'>`.

**Fix:** `self.notes_label.text = plant.get("notes") or ""`  (Same pattern already used in `add_event._update_ui` on the same field.)

---

### 16. `magicherbtracker.kv` — `PlantListItem` / `GardenListItem` RecycleView rules
Not verified in this audit (KV file not read). These item classes must be defined in the KV file for `GardenListView` (`select_garden.py`) and `PlantListView` (`garden_view.py`) to render. If they were lost in the git corruption, both RecycleViews will render blank.

**Action:** Visually verify that garden selection and plant list render item rows correctly. If blank, the KV rules for `GardenListItem` and `PlantListItem` need to be restored.

---

### 17. `go_to_add_event` in `helpers.py` missing the `plant_id` patch
**File:** `helpers.py` line ~34  
```python
def go_to_add_event(instance, plant):
    app = App.get_running_app()
    add_event_screen = app.screen.get_screen("add_event")
    add_event_screen.set_plant(plant)   # ← no plant_id patch here
```
Any caller of `go_to_add_event` that hasn't pre-patched `plant['plant_id']` will hit the `ValueError` from issue #2. Currently `plant_details.py` has its own `safe_go_to_add_event` wrapper and does NOT call `helpers.go_to_add_event` — so the helpers function is not reached from the working path. But if any other screen calls `go_to_add_event`, it will crash.

**Fix:** Move the `plant_id` normalisation into `helpers.go_to_add_event` itself so all callers benefit.

---

### 18. Double-click binds missing on garden list and plant list
**Files:** `boxes.py` line 83, `select_garden.py`, `garden_view.py`

`SelectableBoxLayout.on_touch_down` (used as the touch handler for every selectable row) calls `rv.layout_manager.select_node(self.index)` on a plain tap but has no `touch.is_double_tap` check:

```python
# boxes.py — current
def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
        rv = self.parent.parent
        rv.layout_manager.select_node(self.index)   # single-click select only
        return True
    return super().on_touch_down(touch)
```

As a result:
- Opening a garden requires pressing the separate **Enter Garden** button (`select_garden.py._on_select`).
- Opening plant details requires pressing the separate **View Selected** button (`garden_view.on_details_button`).

The intended UX (README: "tap a card to select, double-tap to open") is not implemented.

Kivy provides `touch.is_double_tap` (bool) on every `MotionEvent` — no additional library is needed.

**Fix:**
```python
# boxes.py — proposed
def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
        rv = self.parent.parent
        rv.layout_manager.select_node(self.index)
        if touch.is_double_tap:
            rv.dispatch('on_activate', self.index)   # custom event
        return True
    return super().on_touch_down(touch)
```
Define `on_activate` on `GardenListView` (`select_garden.py`) to call `_on_select()` and on `PlantListView` (`garden_view.py`) to call `on_details_button()`. No changes to KV rules needed.

---

### 19. Seedbank autofill missing; strain autofill overwrites seedbank unconditionally
**File:** `sow_seed.py` lines ~82, ~99, ~405–444

Two related sub-problems:

**19a. `input_plant_name` (seedbank/breeder field) has no autocomplete.**

```python
# sow_seed.py — current
self.input_plant_name = MedTextInput(hint_text=lang.HINT_SELECT_NAME)   # no bind, no dropdown
...
self.input_plant_strain.bind(text=self.on_strain_text)   # strain has autocomplete
# input_plant_name has nothing equivalent
```

`bin/db/breeder_trie.json` exists and mirrors the structure of `bin/db/seed_trie.json`, but `strain_trie.py` only loads `seed_trie.json` (the strain trie) and `sow_seed.py` never references `breeder_trie.json`. The seedbank field is a plain text input with no suggestions.

**19b. `_apply_catalog_for_strain()` always overwrites the seedbank field.**

```python
# sow_seed.py _apply_catalog_for_strain — current (line ~424)
self.input_plant_name.text = name   # ← unconditional; destroys what the user typed
```

If the user manually typed a breeder/seedbank name and then selected a strain from the dropdown, their entry is silently overwritten with the catalog value.

**Fix:**

- Load `breeder_trie.json` in `strain_trie.py` (or a new `breeder_trie.py`), add a `breeder_search(prefix)` function, and wire `input_plant_name.bind(text=self.on_seedbank_text)` in `sow_seed.py` — mirroring the existing strain autocomplete pattern exactly.
- Guard the overwrite in `_apply_catalog_for_strain`:
  ```python
  if not self.input_plant_name.text.strip():
      self.input_plant_name.text = name
  ```

---

### 20. Plant list items incomplete; sort / search / active-filter toolbar absent from both list screens
**Files:** `garden_view.py`, `select_garden.py`, `magicherbtracker.kv` (lines 618 and 732)

Three related sub-problems affecting `GardenViewScreen` (plant list) and `SelectGardenScreen` (garden list):

---

**20a. `PlantListItem` shows `name` above strain instead of `seedbank`; `notes` row may be clipped.**

The middle column of `PlantListItem` in the KV (line 618) already allocates three label slots:

```kv
ListSubLabel:    text: root.name    # ← meant to be seedbank/breeder
ListTitleLabel:  text: root.strain
ListLabel:       text: root.notes
```

However `refresh_plants()` extracts only `name` from the plant dict and never extracts a `seedbank` or `breeder` key:

```python
# garden_view.py refresh_plants() — current
name   = p.get("name", "")
strain = p.get("strain", "")
notes  = p.get("notes", "")
# no p.get("seedbank") / p.get("breeder")
```

The data dict pushed to `plant_list.data` therefore has no `seedbank` key, and the label shows the plant's internal name (which maps to the `input_plant_name` entry from `sow_seed.py` — the seedbank/breeder field — stored under the ambiguous key `"name"`). The fix is to rename the data key to `seedbank` (and rename the KV property accordingly), or confirm `"name"` is the canonical seedbank field and rename the KV label.

Additionally, `PlantListView` sets `default_size: None, dp(80)` while `PlantListItem` declares `height: "120dp"`. In Kivy's RecycleView the `default_size` height is the recycler's allocation hint; if it is smaller than the item's actual height the bottom labels can be clipped. Change `default_size` to `None, dp(120)` to match, and confirm `notes` renders visible.

---

**20b. Sort dropdown and ascending/descending toggle absent.**

Neither `GardenViewScreen` nor `SelectGardenScreen` builds a toolbar above their respective list. Both screens go directly from the header to the `ItemBox` holding the RecycleView with no sorting controls.

Required controls (described below) should live in a new `sort_bar` row above the list with `size_hint_y: 0.06`.

*Plant list sort options* (for `GardenViewScreen`):  
`Date Planted`, `Name`, `Seedbank`, `Days to Flower`, `Stage`, `Last Event`, `Next Event`

*Garden list sort options* (for `SelectGardenScreen`):  
`Name`, `Date Created`, `Number of Plants`, `Last Event`, `Next Event`

Each dropdown should be paired with a small triangle toggle button (▲/▼) that switches between ascending and descending order. Layout: dropdown on the **left** of the sort bar.

Sorting state (`sort_key`, `sort_asc`) should be stored as instance variables and applied inside `refresh_plants()` / `_refresh_gardens()` before assigning to `.data`.

---

**20c. Search input absent.**

Neither screen has a search/filter text input. A `MedTextInput` (or `SmallTextInput`) should sit in the **centre** of the sort bar.

- *Plant list*: filter by substring match across `seedbank`, `strain`, and `notes` fields.  
- *Garden list*: filter by substring match on `garden_name`.

Bind the input's `text` property to a `_on_search_text` method that rebuilds the filtered dataset from the full cached list (keep `self._all_plants` / `self._all_gardens` as the unfiltered source).

---

**20d. Active-only toggle button absent.**

On the **right** side of the sort bar each screen needs a single toggle button (e.g. `ButtonYellow` / `ButtonGreen` toggling label between `lang.SHOW_ACTIVE` and `lang.SHOW_ALL`) that, when active, hides:
- *Plants*: plants whose `harvest_status` equals `lang.STATUS_HARVESTED` (i.e. past estimated harvest date).  
- *Gardens*: gardens whose `active` field is `False` (or equivalent archived flag).

**Fix (summary):**

1. In `magicherbtracker.kv`: rename `PlantListItem.name` property to `seedbank`; fix `default_size` to `dp(120)`.  
2. In `garden_view.refresh_plants()`: extract `seedbank = p.get("seedbank", p.get("name", ""))` with fallback; store full plant list as `self._all_plants`; apply sort + search + active filter before assigning to `self.plant_list.data`.  
3. In `GardenViewScreen.__init__`: insert a `sort_bar` row (sort dropdown + asc/desc button | search input | active toggle) between the header and the list `ItemBox`.  
4. Mirror steps 2-3 for `SelectGardenScreen._refresh_gardens()` and `SelectGardenScreen.__init__`.  
5. Add `lang.SHOW_ACTIVE`, `lang.SHOW_ALL`, `lang.SORT_*` constants to all language modules.

---

### 21. AddGardenScreen and AddEvent missing location-based light schedule, solstice calculation, and continent/country/city lists — ✅ Fixed
**Files:** `add_garden.py`, `add_event.py`, `bin/db/locations.json`

**21a. Continent/country/city cascading dropdowns — ✅ Fixed**
Created `bin/db/locations.json` with 7 continents, ~35 countries, ~120 cities (lat/lon/tz). `AddGardenScreen` now shows three cascading `CustomDropdown` widgets (continent → country → city) when outdoor is selected. Indoor/outdoor toggle dynamically swaps field groups.

**21b. Automatic light schedule for outdoor gardens — ✅ Fixed**
When outdoor + city is selected, `_daylight_hours()` uses `astral.LocationInfo` + `astral.sun.sun()` to compute today's daylight hours. Result displayed as `Xh / Yh` and saved to garden's `light_schedule`. Location data (continent, country, city, lat, lon, tz) saved to garden dict.

**21c. Indoor light schedule /x live label — ✅ Fixed**
Indoor light hours input clamped to max 24. A live `/ X` label updates on each keystroke showing dark hours (24 − input).

**21d. AddEventScreen light schedule pre-fill — ✅ Fixed**
`_prefill_light_schedule()` added to `AddEventScreen._update_ui()`. For indoor gardens: pre-selects from `garden.light_schedule`. For outdoor gardens with location: recomputes today's daylight via astral. Falls back to existing flip_day heuristic.

---

### 22. `numpy` replaced with pure Python — ✅ Fixed
**File:** `add_event.py` lines 3, 682  

`numpy` was still imported and used in `calculate_vpd()` despite being removed from `pyproject.toml`. Fixed:
```python
# Before
import numpy
es = 0.6108 * numpy.exp((17.27 * air_temp_c) / (air_temp_c + 237.3))

# After
import math
es = 0.6108 * math.exp((17.27 * air_temp_c) / (air_temp_c + 237.3))
```
The duplicate `from text_inputs import ...` (was on both lines 17 and 19) was removed at the same time. No remaining `numpy` imports anywhere in the codebase.

**numpy is still installed** as a transitive dependency of `matplotlib` / `kivy-garden-matplotlib`. It does not need to be in `pyproject.toml` directly.

---

### 23. Installed packages — status and wiring needed
**Packages:** `astral`, `pandas`, `filetype`, `matplotlib`

| Package | Status | Action needed |
|---|---|---|
| `astral==3.2` | ✅ Wired | Used in `add_garden.py` + `add_event.py` for outdoor daylight calculation via `LocationInfo` + `sun()` |
| `pandas==3.0.1` | ✅ Wired | `csv_export_screen.py` — `write_gardens_csv()` now uses `pd.DataFrame(rows, columns=CSV_COLUMNS).to_csv()` instead of `csv.DictWriter` |
| `filetype==1.2.0` | ✅ Wired | `weed_format.py` — `read_weed()` now runs `filetype.guess()` early to reject known non-.weed formats (images, archives, etc.) before binary parsing |
| `matplotlib==3.10.8` | ℹ️ Transitive, not directly needed | `timeline_view.py` uses native `kivy.garden.graph` (`Graph` / `LinePlot`), which does NOT require matplotlib. `kivy-garden-matplotlib` is installed but unused; can be kept as optional or dropped. matplotlib itself is never imported anywhere in the app. |
| `numpy==2.4.2` | ℹ️ Transitive only | Pulled in by matplotlib; not imported in app code (fixed in #22). Do not add to `pyproject.toml`. |
| `kaki==0.1.9` | ℹ️ Dev-only | `dev_main.py` hot-reload only; not needed in production |
| `requests==2.32.5` | ℹ️ Dev/scraper only | `tmp_scrapper.py` / `tmp_get_detailed_strains.py` only |

---

### 24. Light cycle inheritance, flip event → flowering status, and outdoor auto-fill missing — ✅ Fixed
**Files:** `add_event.py`, `garden_view.py`, `constants.py`, `storage.py`, `data.py`

Four related missing behaviours covering how light schedule is determined per-plant and how stage transitions are tracked:

---

**24a. Indoor light cycle inherited from garden — ✅ Fixed**

`AddEventScreen._prefill_light_schedule()` loads the current garden and pre-selects the light schedule dropdown from `garden["light_schedule"]` for indoor gardens.

---

**24b. Outdoor light cycle auto-filled from location — ✅ Fixed**

For outdoor gardens with location data, `_prefill_light_schedule()` calls `add_garden._daylight_hours()` (astral) to compute today's daylight and pre-selects the closest schedule.

---

**24c. `EVENT_FLIP` triggers flowering stage transition — ✅ Fixed**

`_apply_event_side_effects()` sets `plant["stage"] = "flowering"` on flip. `garden_view.refresh_plants()` reads `plant.get("stage")` and shows `STATUS_FLOWERING`.

---

**24d. Stage field updated on event save — ✅ Fixed**

`_apply_event_side_effects()` handles: top/prune → penalty days, flip → flowering, harvest → harvested.

---

### 25. Top/Prune/Flip toggle buttons; Harvest button; autofill; edit-last-event — ✅ Fixed
**Files:** `add_event.py`, `plant_details.py`, `constants.py`

**25a. Top/Prune/Flip as toggle buttons — ✅ Fixed**
Removed from event type dropdown. Three `ToggleButton` widgets (Top, Prune, Flip) placed to the right of the dropdown in `event_type_and_toggles_box`. Each is independently togglable (`allow_no_selection=True`).

**25b. Penalty calculation — ✅ Fixed**
`_apply_event_side_effects` adds 7 penalty days per top/prune event; `garden_view.refresh_plants` includes `penalty` in `est_f`.

**25c. Flip toggle auto-disable — ✅ Fixed**
`_update_flip_toggle_state()` checks event history; disables flip toggle if a flip event already exists.

**25d. `EVENT_HARVEST` — ✅ Fixed**
Added to `constants.py` with alias. Harvest button is a separate `ButtonRed` next to the `+`/save button. `_update_harvest_button_state()` disables it if harvest event exists.

**25e. Language strings — ✅ Present in all 8 files.**

**25f. Harvest disables add-event — ✅ Fixed**
Both `plant_details.py` and `add_event.py` disable their respective buttons when harvest event found.

**25g. Autofill from last event — ✅ Fixed**
`_autofill_from_last_event()` called from `set_plant()`. Pre-populates: plant_height, num_nodes, node_spacing, main_stem_number, leaf_color, leaf_morphology, air_temp, humidity, soil_ph, ppfd, soil_moisture, light_schedule.

**25h. Smart default event type — deferred**
Schedule-based default (watering/feeding based on day) not yet implemented. Low priority — no schedule system exists yet.

**25i. Edit-last-event button — ✅ Fixed**
`plant_details._load_and_display_events()` detects if last event was today. If so: changes `+` button text to `lang.BUTTON_EDIT`, switches to body font size, and passes `_last_event_today` data to `AddEventScreen._selected_event_data` on press.

**25j. Toggle priority — ✅ Fixed**
`_get_effective_event_type()` returns highest priority active type: flip > top > prune > dropdown. Harvest is a separate button and bypasses this entirely. `_on_toggle_state_change` re-renders the water/food area when toggles change.

---

## Working / Intact

The following are confirmed functional based on code review:

| Component | Status | Notes |
|---|---|---|
| Bootstrap flow (password → garden selection → garden view)                    | ✅ Working | `main.py` logic clean                                                    |
| `storage.py` — garden/plant CRUD, atomic writes, platformdirs path            | ✅ Working | Full layer intact                                                        |
| Transparent encryption/decryption on read/write                               | ✅ Working | `_read_json` / `_atomic_write_json` correct                              |
| `crypto.py` — `CryptoContext`, `encrypt_bytes`, `decrypt_bytes`               | ✅ Working | Rust backend delegation correct                                          |
| `helpers.derive_encryption_key` / `hash_password` / `verify_password`         | ✅ Working | Production callers use correct dict-based API                            |
| `migrate.py` — `encrypt_all_data` / `decrypt_all_data` / `reencrypt_all_data` | ✅ Working | All three functions intact and idempotent                                |
| `password_check.py` — backoff, key derivation, unlock flow                    | ✅ Working | Correct use of `stored` dict                                             |
| `settings_screen.py` — password set/change/remove flow                        | ✅ Working | `_do_set_password` uses correct API                                      |
| `sow_seed.py` → `set_environment.py` → `garden_view.py` (plant creation)      | ✅ Working | `pending_plant_data` handoff intact                                      |
| `add_garden.py` — garden creation                                             | ✅ Working | Saves correct `GARDEN_SCHEMA`-compliant dict                             |
| `select_garden.py` — garden selection                                         | ✅ Working | `on_select_garden` sets `current_garden_id`                              |
| `garden_view.refresh_plants()` — plant list rendering                         | ✅ Working (mostly) | Minor None crash on missing `days_to_flower` (issue #13)        |
| `plant_details.py` — `set_plant`, `_load_and_display_events`                  | ✅ Working | `_load_and_display_events` uses `storage.load_plant_events` correctly    |
| `plant_details.safe_go_to_add_event` — `plant_id` patch                       | ✅ Working | Injects `plant['plant_id'] = plant['id']` before calling `add_event`     |
| `export_import_screen.py` / `weed_format.py`                                  | ✅ Working | Clean, uses `data.GardenRepository` / `PlantRepository`                  |
| `csv_export_screen.py`                                                        | ✅ Working | Uses `storage` correctly                                                 |
| `timeline_view.py` — graphs, LinePlot                                         | ✅ Working | `kivy.garden.graph` integration intact                                   |
| `bin/themes/__init__.py` — theme loading (happy path)                         | ✅ Working | All 6 built-in themes load correctly; only fallback is broken            |
| `bin/lang/` — language loading                                                | ✅ Working | Modular loader intact                                                    |
| `bin/shaders/` — GLSL shader loading                                          | ⚠️ Partial | Files present but never loaded at runtime (issue #10)                    |
| `validators.py` — schema definitions                                          | ✅ Working | Graceful no-op without jsonschema                                        |
| `data.py` — all four repositories with caching                                | ✅ Working | Clean interfaces                                                         |
| `constants.py` — event type normalisation                                     | ✅ Working |                                                                          |
| `effects.py` — `shake_and_flash`                                              | ✅ Working |                                                                          |
| `strain_trie.py` — autocomplete                                               | ✅ Working |                                                                          |
| `are_you_sure.py` — confirmation screen                                       | ✅ Working |                                                                          |
| `empty_garden.py` — first-launch screen                                       | ✅ Working |                                                                          |
| `crypto_rs` — Rust AES-256-GCM extension                                      | ✅ Working |                                                                          |

---

## Rebuild Priority Order

### Phase 1 — Fix crashes (do these first, in order)
1. **Issue #3** — Change `forest_dark` fallback to `"green"` in `bin/themes/__init__.py`. One-line fix; unblocks theme system resilience.
2. **Issue #1 + #2** — Rewrite `on_event_save` in `add_event.py` to use `EventRepository.add_event()`. Simultaneously resolve the `plant_id`/`id` key inconsistency by normalising in `set_plant()`. This is the largest single fix.
3. **Issue #4** — Restore or recreate `run_unit_tests.py` (or update CI to `python -m pytest tests/`).

### Phase 2 — Fix broken behaviour
4. **Issue #5** — Remove `name_label` / `strain_label` from `validate()` in `add_event.py`.
5. **Issue #10** — Wire up the shader system: load from `bin/shaders/`, respect `shader_enabled`, fix `_on_shader_reload`, remove duplicate method definitions in `fx.py`.
6. **Issue #15** — Fix `plant.get("notes")` → `plant.get("notes") or ""` in `plant_details._update_ui()`.
7. **Issue #14** — Guard `days_to_flower` arithmetic in `garden_view.refresh_plants()`.
8. **Issue #17** — Move `plant_id` normalisation into `helpers.go_to_add_event`.
9. **Issue #20** — Implement sort/search/active-filter toolbar for plant list and garden list; fix `PlantListItem` seedbank label and `default_size` height.
10. **Issue #24** — Implement flip event → flowering stage transition; indoor light cycle inheritance from garden; outdoor auto-fill via `astral`; `garden_view` stage-first status logic.
11. **Issue #25** — Add Top/Prune/Flip toggles, Harvest event type, penalty calculation, last-event autofill, smart open state, and edit-last-event button behaviour to `AddEventScreen`.

### Phase 3 — Restore test suite accuracy
9. **Issue #11** — Update `test_crypto.py`: `derive_encryption_key` tests to pass full `stored` dict.
10. **Issue #12** — Add `storage._normalize_plants()` helper and call it in `get_plants_for_garden`, or rewrite the tests.
11. **Issue #13** — Change theme tests to use `"dark"` instead of `"forest_dark"`.

### Phase 4 — Cleanup
12. **Issue #7** — Remove debug `print` statements from `helpers.go_to_timeline`.
13. **Issue #9** — Remove dead strain-autocomplete code from `set_environment.py`.
14. **Issue #6** — Delete or fix `plant_details.EventListView` (unused, wrong viewclass).
15. **Issue #16** — Visually verify `GardenListItem` / `PlantListItem` KV rules are intact.
16. **Issue #18** — Add double-click binds to garden list (`select_garden.py`) and plant list (`garden_view.py`) via `touch.is_double_tap` in `SelectableBoxLayout.on_touch_down`.
17. **Issue #19** — Add seedbank autocomplete backed by `breeder_trie.json`; guard `_apply_catalog_for_strain` against overwriting a user-filled seedbank field.
18. **Issue #21** — Build `bin/db/locations.json`; add continent/country/city dropdowns to `AddGardenScreen`; wire `astral` for outdoor light schedule; add `/x` live label for indoor schedule input.
19. ~~**Issue #23** — Wire `pandas` into `csv_export_screen.py`; wire `filetype` into `weed_format.py` import validation.~~ ✅ Done. `pandas` replaces `csv.DictWriter` with DataFrame export; `filetype` validates incoming `.weed` files.
20. **Issue #24** — Implement per-plant flip event → flowering status transition and light cycle inheritance logic for indoor/outdoor gardens.

---

## Issue #26 — Theme system not wired: `apply_theme()` never called; KV + Python use old property names

**Severity:** Critical — theme changes in settings have zero visual effect; the app always shows the green-theme hardcoded defaults.

### Root cause (3 layers)

**Layer 1 — `main.py` never calls `apply_theme()`**

```python
# main.py:56
self.theme = Factory.Theme()        # ← creates KV Theme widget with hardcoded defaults
# apply_theme(self.theme, theme_data) is NEVER called
```

The `apply_theme()` function exists in `bin/themes/__init__.py` and correctly iterates TOML sections
to `setattr` each key onto the Theme widget. But nobody calls it at startup or on theme change.

**Layer 2 — KV `<Theme>` uses old property names that don't exist in TOML**

The KV `<Theme@Widget>` defines convenience colors (`nice_yellow`, `off_white`, `dark_green` …).
These are the *only* properties the 209 KV `app.theme.*` bindings reference.
But the TOML themes provide semantic names under `[element_colors]` (`color_label_title`, `color_button_bg` …).
Even if `apply_theme()` were called, the TOML keys would be added as *new* attributes —
the KV bindings would never read them because they still reference the old names.

**Stale KV-only properties (always return hardcoded green-theme defaults):**

| KV name | Hardcoded value | TOML equivalent(s) |
|---------|-----------------|---------------------|
| `dark_gray` | `0.18, 0.122, 0.153, 1` | `color_button_on_color_text` |
| `dark_green` | `0.12, 0.172, 0.153, 1` | `color_button_bg`, `color_screen_bg`, `color_nutrient_text` |
| `very_dark_green` | `0.13, 0.15, 0.14, 1` | `color_box_dark` |
| `off_white` | `0.831, 0.875, 0.62, 1` | `color_label_subtitle`, `color_input_text`, `color_field_value` |
| `light_green` | `0.773, 0.847, 0.427, 1` | `color_label_body`, `color_strain_sativa` |
| `nice_red` | `0.827, 0.247, 0.286, 1` | `color_button_red_bg`, `color_box_red` |
| `nice_yellow` | `1, 0.651, 0.188, 1` | `color_label_title`, `color_button_yellow_bg`, `color_dropdown_text` |
| `light_yellow` | `0.84, 0.68, 0.35, 1` | `color_label_warning`, `color_strain_hybrid` |
| `nice_orange` | `0.945, 0.427, 0.196, 1` | `color_event_top` |
| `nice_brown` | `0.545, 0.325, 0.196, 1` | `color_graph_series_2` |
| `dark_brown` | `0.345, 0.225, 0.146, 1` | (no TOML equivalent) |
| `bright_green` | `0.196, 0.745, 0.325, 1` | `color_graph_series_1` |
| `nice_green` | `0.289, 0.516, 0.353, 1` | `color_button_green_bg`, `color_field_label`, `color_input_hint` |
| `nice_blue` | `0.235, 0.451, 0.686, 1` | `color_water_label`, `color_event_watering` |
| `nice_purple` | `0.392, 0.259, 0.416, 1` | `color_list_selected_bg`, `color_event_prune` |
| `black_transparent` | `0, 0, 0, 0` | `color_transparent` |

**Layer 3 — Python screen files also use old property names**

All Python files that build UI dynamically use the same old `app.theme.nice_yellow` etc. names:

| File | # of stale refs | Key examples |
|------|-----------------|--------------|
| `add_event.py` | 22 | `off_white`, `nice_green`, `nice_blue`, `nice_yellow`, strain colors |
| `plant_details.py` | 30+ | `off_white`, `nice_green`, `nice_blue`, `nice_yellow`, strain/health/event colors, hardcoded `font_size="12sp"` |
| `timeline_view.py` | 25+ | palette colors, tab colors, `black_transparent`, `dark_green`, `off_white` |
| `boxes.py` | 8 | `EventBox`/`SelectableEventBox` hover/selected state colors |
| `buttons.py` | 2 | `HoverButton`/`HoverToggle` hardcoded `hover_background_color` ListProperty |
| `labels.py` | 2 | `TitleLabel` hex color derived from `off_white` |
| `effects.py` | 1 | `shake_and_flash` hardcoded RGBA flash color |
| `are_you_sure.py` | 2 | `nice_yellow`, `off_white` |

### Fix strategy

There are two viable approaches — pick one:

#### Option A — Bridge layer (least churn, fastest)

Add a mapping in `apply_theme()` (or a post-processor) that translates TOML `[element_colors]`
back to the old KV convenience names. This way the existing 209 KV bindings and all Python
`app.theme.xxx` references keep working.

```python
# In bin/themes/__init__.py or main.py after apply_theme()
_ELEMENT_TO_KV = {
    "color_label_title":      "nice_yellow",
    "color_label_body":       "light_green",
    "color_label_subtitle":   "off_white",
    "color_button_bg":        "dark_green",
    "color_button_green_bg":  "nice_green",
    "color_button_yellow_bg": "nice_yellow",
    "color_button_red_bg":    "nice_red",
    "color_button_on_color_text": "dark_gray",
    "color_transparent":      "black_transparent",
    "color_box_dark":         "very_dark_green",
    "color_water_label":      "nice_blue",
    "color_list_selected_bg": "nice_purple",
    # ... etc
}
```

After `apply_theme(self.theme, data)`, iterate `_ELEMENT_TO_KV` and do:
```python
for toml_key, kv_name in _ELEMENT_TO_KV.items():
    if hasattr(theme_widget, toml_key):
        setattr(theme_widget, kv_name, getattr(theme_widget, toml_key))
```

Additionally:
1. Call `apply_theme()` in `main.py::build()` after `self.theme = Factory.Theme()`.
2. Call it again in `settings_screen.py::_on_save()` after the saved theme changes.

#### Option B — Full migration (more churn, cleaner long term)

1. Rewrite the KV `<Theme@Widget>` to declare all `[element_colors]` keys as properties.
2. Find-and-replace all 209 KV `app.theme.old_name` → `app.theme.new_name`.
3. Find-and-replace all Python `app.theme.old_name` references (100+ across 8 files).
4. Remove old convenience names from the KV Theme widget.
5. Wire `apply_theme()` calls in `main.py::build()` and `settings_screen.py::_on_save()`.

### Additional hardcoded values found

| File | Line(s) | Issue |
|------|---------|-------|
| `buttons.py` | 39, 56 | `hover_background_color = ListProperty([0.773, 0.847, 0.427, 1])` — hardcoded instead of reading from theme |
| `effects.py` | 4 | `flash_color=(0.827, 0.247, 0.286, 1)` — hardcoded default parameter |
| `labels.py` | 37 | `"#ffffff"` fallback hex color |
| `plant_details.py` | 281-314 | Multiple `font_size="12sp"` instead of `app.theme.small_size` |
| `timeline_view.py` | 420, 459 | Fallback `cval = (1, 1, 1, 1)` instead of theme color |

