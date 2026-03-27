# Test Plan - Magic Herb Tracker

Full-coverage test strategy organized into prioritized phases.
Each phase builds on the previous one, moving from pure-logic units to integration/UI.

---

## Current State

**Baseline**: 14 test files, ~114 test functions.
**After implementation (Phases 1–8)**: **463 tests, 0 failures.**

All 8 phases are **COMPLETE**.

### Implemented coverage

| Module | Tests | Status |
|--------|-------|--------|
| `constants.py` | 28 tests - normalize_event_type, ALL_EVENT_TYPES | ✅ new |
| `helpers.py` | ~30 tests - coerce_to_date, get_difference_days, parse_ts, rgba_to_hex | ✅ extended |
| `validators.py` | 24 tests - validate_* bool API, check_* error-list API | ✅ new |
| `csv_export_screen.py` | 14 tests - row builders via AST extraction | ✅ new |
| `add_garden.py` | 6 tests - _daylight_hours via AST extraction | ✅ new |
| `storage.py` | 25 tests - _read_json, _atomic_write_json, garden/plant/event/settings CRUD | ✅ new |
| `data.py` | ~38 tests - PlantRepo, EventRepo, GardenRepo, IndexRepo CRUD | ✅ extended |
| `weed_format.py` | 12 tests - roundtrip, password, corruption detection | ✅ new |
| `migrate.py` | 9 tests - encrypt/decrypt/reencrypt/migrate_db_path | ✅ new |
| `breeder_trie.py` | 9 tests - search, load, limit, case-insensitive | ✅ new |
| `strain_trie.py` | 8 tests - search, load, limit, case-insensitive | ✅ extended |
| `catalog_service.py` | 9 tests - get_catalog, lookup_strain | ✅ new |
| `lang.py` / `bin/lang/` | 8 tests - load_language, constants, reload | ✅ new |
| `services/` | ~51 tests - all services + settings + formatting edge cases | ✅ extended |
| `photo_utils.py` | 22 tests - validate, dimensions, mime, thumbnail, process | ✅ new |
| `photo_storage.py` | 16 tests - save/load/delete photo+thumbnail, index | ✅ new |
| Integration | 10 tests - lifecycle, side-effects, weed roundtrip, crypto cycle | ✅ new |
| Screen logic | 45 tests - VPD, graph ticks, prepare_series, food_relative, health, is_harvested, backoff, export | ✅ new (AST extraction) |
| Widgets/UI | 67 tests - boxes, buttons, labels, text inputs, dropdown, ui_builders, theme, hover, effects | ✅ new (headless Kivy) |
| `crypto.py` | 18 tests (pre-existing) | ✅ |
| Shader/theme | 12 tests (pre-existing) | ✅ |
| Timeline graphs | 5 tests (pre-existing) | ✅ |

**Test runner**: Custom `run_unit_tests.py` - discovers `test_*` functions in `tests/test_*.py`.
**Mock pattern**: Manual `_FakeStorage` monkey-patching + `_setup()` per test. No pytest/unittest.mock.
**Assertions**: Plain `assert` statements, try/except for expected exceptions.

---

## Phase 1 - Pure Logic Functions (No Dependencies)

Zero-dependency functions that can be tested immediately with plain asserts.
**Estimated effort: ~1 hour. ~35 new tests.**

### 1.1 `constants.py` - `normalize_event_type()`

| Test | Description |
|------|-------------|
| `test_normalize_canonical_types` | Each canonical type (WATERING, FEEDING, LOG, etc.) returns itself |
| `test_normalize_aliases` | Known aliases map correctly (e.g. "water" → EVENT_WATERING) |
| `test_normalize_case_insensitive` | Mixed-case input normalizes correctly |
| `test_normalize_unknown_returns_log` | Unknown strings fall back to EVENT_LOG |
| `test_normalize_none_returns_log` | None input returns EVENT_LOG |
| `test_all_event_types_list` | `ALL_EVENT_TYPES` contains all 7 canonical types |

File: `tests/test_constants.py`

### 1.2 `helpers.py` - Remaining Pure Functions

| Test | Description |
|------|-------------|
| `test_parse_ts_iso_string` | ISO datetime string → datetime object |
| `test_parse_ts_datetime_passthrough` | datetime input returned unchanged |
| `test_parse_ts_none_returns_none` | None → None |
| `test_parse_ts_invalid_returns_none` | Garbage string → None |
| `test_parse_ts_date_only_string` | "2024-01-15" → datetime |
| `test_rgba_to_hex_basic` | `[1, 0, 0, 1]` → `"#ff0000"` or similar |
| `test_rgba_to_hex_with_alpha` | Alpha channel handling |
| `test_rgba_to_hex_floats` | Float RGBA values (0.0–1.0) → hex |

File: `tests/test_helpers.py` (extend existing)

### 1.3 `validators.py` - Bool API

| Test | Description |
|------|-------------|
| `test_validate_plant_valid` | Valid plant dict → True |
| `test_validate_plant_invalid` | Missing required fields → False |
| `test_validate_event_valid` | Valid event dict → True |
| `test_validate_event_invalid` | Missing fields → False |
| `test_validate_garden_valid` | Valid garden dict → True |
| `test_validate_garden_invalid` | Missing fields → False |

File: `tests/test_validators.py` (new)

### 1.4 `csv_export_screen.py` - Pure Row Builders

| Test | Description |
|------|-------------|
| `test_garden_base_row` | Garden dict → expected flat row values |
| `test_plant_base_row` | Plant dict → expected flat row values |
| `test_event_row` | Event dict → expected flat row values |
| `test_event_row_missing_fields` | Graceful handling of missing optional fields |

File: `tests/test_csv_export.py`

### 1.5 `add_garden.py` - `_daylight_hours()`

| Test | Description |
|------|-------------|
| `test_daylight_hours_summer_solstice` | June 21 at 45°N ≈ ~15–16h |
| `test_daylight_hours_winter_solstice` | Dec 21 at 45°N ≈ ~8–9h |
| `test_daylight_hours_equator` | Latitude 0° ≈ ~12h year-round |
| `test_daylight_hours_equinox` | March/Sep equinox ≈ ~12h any latitude |

File: `tests/test_daylight.py`

---

## Phase 2 - Data Layer & File I/O (Temp Dirs / Mocks)

Functions that do file I/O. Use `tempfile.mkdtemp()` to create isolated directories.
**Estimated effort: ~2–3 hours. ~45 new tests.**

### 2.1 `storage.py` - Core File Operations

| Test | Description |
|------|-------------|
| `test_read_json_valid_file` | Read a valid JSON file from a temp dir |
| `test_read_json_missing_file` | Missing file → returns default |
| `test_read_json_corrupt_json` | Malformed JSON → returns default |
| `test_atomic_write_json_creates_file` | Write creates file atomically |
| `test_atomic_write_json_overwrites` | Overwrite existing file |
| `test_atomic_write_no_tmp_leftover` | No `.tmp` file remains after write |
| `test_load_gardens_empty_dir` | No garden files → empty list |
| `test_load_garden_roundtrip` | save_garden → load_garden produces same data |
| `test_delete_garden_removes_file` | Garden file is deleted |
| `test_delete_garden_missing_noop` | Deleting non-existent garden doesn't raise |
| `test_add_plant_to_garden` | Plant added to garden file |
| `test_remove_plant_from_garden` | Plant removed from garden file |
| `test_load_save_plant_events_roundtrip` | Events persist and load back |
| `test_load_save_settings_roundtrip` | Settings persist and load back |
| `test_load_save_index_roundtrip` | Index persists and loads back |
| `test_encrypted_roundtrip` | Write with key → read with key succeeds |
| `test_encrypted_wrong_key_fails` | Read with wrong key fails gracefully |

**Setup helper**: A `_make_tmp_storage(tmp_dir)` function that patches `storage` module paths to point at `tmp_dir`.

File: `tests/test_storage.py`

### 2.2 `data.py` - Uncovered Repository Methods

| Test | Description |
|------|-------------|
| `test_event_repo_update_event` | Update existing event in list |
| `test_event_repo_update_event_missing` | Update non-existent event is no-op |
| `test_event_repo_updates_plants_index` | Adding event updates index timestamps |
| `test_garden_repo_list_all` | Multiple gardens listed |
| `test_garden_repo_list_all_empty` | No gardens → empty list |
| `test_garden_repo_save` | New garden persists |
| `test_garden_repo_delete` | Garden removed from cache |
| `test_photo_repo_attach` | Attach photo meta to event |
| `test_photo_repo_detach` | Detach photo from event |
| `test_photo_repo_detach_all_for_event` | Clear all photos for event |
| `test_photo_repo_detach_all_for_plant` | Clear all photos for plant |
| `test_photo_repo_get_meta` | Retrieve photo metadata |
| `test_photo_repo_list_for_event` | List photos attached to event |
| `test_photo_repo_list_for_plant` | List photos attached to plant |
| `test_photo_repo_load_photo_bytes` | Load stored photo bytes |
| `test_photo_repo_load_thumb_bytes` | Load stored thumbnail bytes |

File: `tests/test_data_repos.py` (extend existing) + `tests/test_photo_repo.py` (new)

### 2.3 `weed_format.py` - Binary Export/Import

| Test | Description |
|------|-------------|
| `test_write_read_roundtrip` | Export → import produces identical data |
| `test_write_read_with_password` | Password-protected export → import with correct pw |
| `test_read_wrong_password_raises` | Wrong password → `WeedWrongPassword` |
| `test_read_password_required_raises` | Encrypted file, no pw → `WeedPasswordRequired` |
| `test_read_corrupted_raises` | Truncated/corrupt file → `WeedCorrupted` |
| `test_read_tampered_hmac_raises` | Modified bytes → HMAC mismatch → `WeedCorrupted` |
| `test_roundtrip_multiple_gardens` | Multi-garden export/import |
| `test_roundtrip_with_photos` | Export includes photo section |
| `test_roundtrip_empty_gardens` | Edge: no gardens |

File: `tests/test_weed_format.py`

### 2.4 `migrate.py` - Encryption Migration

| Test | Description |
|------|-------------|
| `test_encrypt_all_data` | Plaintext files → encrypted; settings stays plain |
| `test_decrypt_all_data` | Encrypted files → plaintext |
| `test_reencrypt_all_data` | Reencrypt with new key |
| `test_migrate_db_path` | Moves data files to new directory |
| `test_migrate_db_path_missing_src` | Source doesn't exist → graceful handling |

File: `tests/test_migrate.py`

---

## Phase 3 - Trie & Catalog Modules

**Estimated effort: ~1 hour. ~15 new tests.**

### 3.1 `breeder_trie.py`

| Test | Description |
|------|-------------|
| `test_breeder_search_prefix` | Prefix returns matching breeders |
| `test_breeder_search_empty_prefix` | Empty/short prefix → empty results |
| `test_breeder_search_limit` | Results capped at limit |
| `test_breeder_search_no_match` | Non-matching prefix → empty |
| `test_load_trie` | Trie loads from bin/db without error |

File: `tests/test_breeder_trie.py`

### 3.2 `strain_trie.py` - Extended Tests

| Test | Description |
|------|-------------|
| `test_trie_search_with_results` | Known prefix returns results |
| `test_trie_search_limit` | Results respect limit parameter |
| `test_trie_search_case_insensitive` | Case doesn't affect results |
| `test_load_trie_from_disk` | Real trie file loads |

File: `tests/test_strain_trie.py` (extend existing)

### 3.3 `services/catalog_service.py`

| Test | Description |
|------|-------------|
| `test_get_catalog_loads` | Catalog loads without error |
| `test_lookup_strain_found` | Known strain returns data |
| `test_lookup_strain_not_found` | Unknown strain → None |
| `test_lookup_strain_empty_catalog` | Empty catalog → None |

File: `tests/test_catalog_service.py`

---

## Phase 4 - Language & Configuration

**Estimated effort: ~45 min. ~10 new tests.**

### 4.1 `lang.py`

| Test | Description |
|------|-------------|
| `test_load_english` | English module loads, has expected constants |
| `test_load_unknown_falls_back` | Unknown language name → falls back to English |
| `test_reload_changes_language` | `reload()` switches active language |
| `test_lang_constants_are_strings` | All exported constants are strings |

File: `tests/test_lang.py`

### 4.2 `bin/lang/__init__.py`

| Test | Description |
|------|-------------|
| `test_get_available_languages` | Returns list including "english" |
| `test_load_language_english` | `load_language("english")` returns module |
| `test_load_language_invalid` | Invalid name → None or fallback |

File: `tests/test_lang.py` (same file)

### 4.3 `services/settings_service.py` - Extended

| Test | Description |
|------|-------------|
| `test_get_setting_default` | Missing key → returns default |
| `test_get_theme_name` | Returns theme name from settings |
| `test_get_shader_prefs` | Returns shader preferences dict |

File: `tests/test_services.py` (extend existing)

---

## Phase 5 - Photo Pipeline

**Estimated effort: ~2 hours. ~20 new tests.**
Requires: `Pillow` (optional dep), test image fixtures.

### 5.1 `photo_utils.py`

| Test | Description |
|------|-------------|
| `test_validate_image_valid_jpeg` | Valid JPEG bytes → True |
| `test_validate_image_invalid_bytes` | Random bytes → False |
| `test_validate_image_empty` | Empty bytes → False |
| `test_get_image_dimensions` | Returns (width, height) for known image |
| `test_get_mime_type_jpeg` | JPEG bytes → "image/jpeg" |
| `test_get_mime_type_png` | PNG bytes → "image/png" |
| `test_generate_thumbnail` | Returns smaller image bytes |
| `test_generate_thumbnail_respects_size` | Output dimensions ≤ max |
| `test_process_image` | Full pipeline: validate → resize → thumb |
| `test_pillow_available` | Returns bool (True if Pillow installed) |

File: `tests/test_photo_utils.py`

### 5.2 `photo_storage.py`

| Test | Description |
|------|-------------|
| `test_save_load_photo_roundtrip` | Save bytes → load returns same bytes |
| `test_save_load_thumbnail_roundtrip` | Save thumb → load returns same |
| `test_delete_photo` | File removed after delete |
| `test_delete_plant_photos` | All plant photos removed |
| `test_list_photo_files` | Lists all photo files for plant |
| `test_load_save_photo_index_roundtrip` | Index persists and loads |
| `test_load_missing_photo_returns_none` | Missing photo → None |
| `test_save_photo_creates_dirs` | Directories created if missing |

File: `tests/test_photo_storage.py`

---

## Phase 6 - Services Edge Cases & Integration

**Estimated effort: ~1.5 hours. ~20 new tests.**

### 6.1 `services/garden_service.py` - Edge Cases

| Test | Description |
|------|-------------|
| `test_filter_plants_empty_search` | Empty query returns all |
| `test_filter_plants_by_stage` | Stage filter works |
| `test_sort_plants_no_plants` | Empty list → empty list |
| `test_sort_plants_by_health` | Health sort uses penalty |

### 6.2 `services/plant_service.py` - Edge Cases

| Test | Description |
|------|-------------|
| `test_apply_event_unknown_type` | Unknown event type → True (no-op) |
| `test_create_plant_minimal_data` | Minimal plant fields succeeds |

### 6.3 `services/event_service.py` - Edge Cases

| Test | Description |
|------|-------------|
| `test_get_events_non_list` | Non-list storage → empty list |
| `test_add_event_normalizes_timestamp` | Timestamp normalized to ISO |

### 6.4 `services/formatting.py` - Edge Cases

| Test | Description |
|------|-------------|
| `test_health_indicator_moderate` | Moderate issues branch |
| `test_format_relative_time_future` | Future date handling |
| `test_format_relative_time_edge_cases` | Just now, 1 min, 1 hour, etc. |

### 6.5 Integration Tests

| Test | Description |
|------|-------------|
| `test_full_plant_lifecycle` | Create garden → add plant → add events → verify timeline data |
| `test_event_side_effects_chain` | Top → Prune → Flip → verify counts accumulate |
| `test_export_import_roundtrip` | Create data → .weed export → fresh import → verify identical |
| `test_password_encrypt_decrypt_cycle` | Set password → encrypt all → decrypt all → data intact |

File: `tests/test_integration.py`

---

## Phase 7 - Screen Logic Extraction (Kivy-Adjacent)

Extract testable logic from screen classes into standalone functions/methods.
**Estimated effort: ~3 hours. ~25 new tests. Requires minor refactoring.**

### Strategy
Many screens contain pure logic buried inside Kivy callbacks. Extract these into module-level functions or static methods that can be tested without Kivy.

### 7.1 `add_event.py` - Extractable Logic

| Function to Extract | Test |
|---------------------|------|
| `_validate_event_fields(data)` | Test validation of event form data |
| `_build_event_dict(fields)` | Test event dict construction |

### 7.2 `sow_seed.py` - Extractable Logic

| Function to Extract | Test |
|---------------------|------|
| `_validate_seed_fields(data)` | Test seed form validation |
| `_build_plant_dict(fields)` | Test plant dict construction |

### 7.3 `timeline_view.py` - Already Partially Tested

| Test | Description |
|------|-------------|
| `test_apply_and_preserve_x_initialized` | Initialized graph preserves x-window |
| `test_compute_graph_series` | Raw events → graph data points |
| `test_food_graph_data_transform` | Nutrients → series arrays |

### 7.4 `garden_view.py` - Extractable Logic

| Function to Extract | Test |
|---------------------|------|
| `_compute_plant_card_data(plant)` | Test card data computation |

### 7.5 `settings_screen.py` - Extractable Logic

| Function to Extract | Test |
|---------------------|------|
| `_validate_settings(data)` | Test settings validation |

File: `tests/test_screen_logic.py`

---

## Phase 8 - UI Widget Smoke Tests (Kivy Required)

Requires a Kivy test harness. Lower priority - these are visual components.
**Estimated effort: ~3–4 hours. ~30 new tests. Requires Kivy test setup.**

### Kivy Test Harness Setup
```python
# tests/kivy_test_helper.py
from types import SimpleNamespace
from kivy.app import App

def make_fake_app(theme=None, lang=None):
    """Create minimal fake app for widget testing."""
    if theme is None:
        theme = SimpleNamespace(
            bg=[0.1, 0.1, 0.1, 1],
            fg=[1, 1, 1, 1],
            accent=[0, 0.8, 0, 1],
            # ... all required theme attrs
        )
    if lang is None:
        from bin.lang import load_language
        lang = load_language("english")
    app = SimpleNamespace(theme=theme, lang=lang, screen=SimpleNamespace())
    App.get_running_app = lambda: app
    return app
```

### 8.1 Widget Instantiation Tests

| Test | Description |
|------|-------------|
| `test_hover_button_creates` | HoverButton instantiates without error |
| `test_content_box_creates` | ContentBox instantiates |
| `test_num_text_input_filters` | NumTextInput rejects non-numeric |
| `test_days_text_input_filters` | DaysTextInput rejects invalid days |
| `test_custom_dropdown_creates` | CustomDropdown instantiates |
| `test_nutrient_button_creates` | NutrientButton instantiates |

### 8.2 `ui_builders.py` - Builder Smoke Tests

| Test | Description |
|------|-------------|
| `test_create_stripes_logo` | Returns widget without error |
| `test_create_initial_layout` | Returns layout with expected structure |
| `test_create_event_item` | Returns event widget |
| `test_create_nutrients_panel` | Returns nutrients panel |

File: `tests/test_widgets.py`

---

## Implementation Order & Priority

| Phase | Priority | Tests | Effort | Dependencies |
|-------|----------|-------|--------|--------------|
| **1** | **Critical** | ~35 | 1h | None |
| **2** | **Critical** | ~45 | 2–3h | `tempfile` |
| **3** | **High** | ~15 | 1h | Trie data files |
| **4** | **High** | ~10 | 45m | Language modules |
| **5** | **Medium** | ~20 | 2h | Pillow, test images |
| **6** | **Medium** | ~20 | 1.5h | Phases 1–2 |
| **7** | **Low** | ~25 | 3h | Light refactoring |
| **8** | **Low** | ~30 | 3–4h | Kivy test harness |

**Total: ~200 new tests across 8 phases.**

---

## Conventions to Follow

1. **File naming**: `tests/test_<module>.py`
2. **Function naming**: `test_<what>_<scenario>` (e.g. `test_normalize_event_type_unknown`)
3. **Setup**: Each test file has a `_setup()` function for state reset; call at start of every test
4. **Assertions**: Plain `assert` with descriptive messages: `assert result == expected, f"got {result}"`
5. **Mocking**: Continue using `_FakeStorage` monkey-patching pattern for data layer tests
6. **Temp dirs**: Use `tempfile.mkdtemp()` + `shutil.rmtree()` in teardown for file I/O tests
7. **No external deps**: Avoid pytest/unittest - stick with the custom runner
8. **CI compatibility**: All Phase 1–6 tests must run headless (no display needed)
9. **Test isolation**: Each `test_*` function is fully independent - no shared mutable state

---

## CI Considerations

- Phases 1–6 run headlessly on Ubuntu CI (Python 3.13)
- Phases 7–8 may need `xvfb-run` for Kivy display initialization
- Add CI step: `xvfb-run python run_unit_tests.py` (or set `KIVY_NO_ARGS=1` + `DISPLAY=:99`)
- Photo tests (Phase 5) should skip gracefully if Pillow is not installed

---

## File Checklist

New test files to create:

- [x] `tests/test_constants.py` - Phase 1 (28 tests)
- [x] `tests/test_validators.py` - Phase 1 (24 tests)
- [x] `tests/test_csv_export.py` - Phase 1 (14 tests)
- [x] `tests/test_daylight.py` - Phase 1 (6 tests)
- [x] `tests/test_storage.py` - Phase 2 (25 tests)
- [ ] `tests/test_photo_repo.py` - Phase 2 (skipped: covered by test_photo_storage.py)
- [x] `tests/test_weed_format.py` - Phase 2 (12 tests)
- [x] `tests/test_migrate.py` - Phase 2 (9 tests)
- [x] `tests/test_breeder_trie.py` - Phase 3 (9 tests)
- [x] `tests/test_catalog_service.py` - Phase 3 (9 tests)
- [x] `tests/test_lang.py` - Phase 4 (8 tests)
- [x] `tests/test_photo_utils.py` - Phase 5 (22 tests)
- [x] `tests/test_photo_storage.py` - Phase 5 (16 tests)
- [x] `tests/test_integration.py` - Phase 6 (10 tests)
- [x] `tests/test_screen_logic.py` - Phase 7 (45 tests)
- [x] `tests/kivy_test_helper.py` - Phase 8 (test harness)
- [x] `tests/test_widgets.py` - Phase 8 (67 tests)

Existing test files to extend:

- [x] `tests/test_helpers.py` - Phase 1 (added parse_ts, rgba_to_hex; ~26 new tests)
- [x] `tests/test_strain_trie.py` - Phase 3 (added real trie tests; +6 tests)
- [x] `tests/test_data_repos.py` - Phase 2 (added EventRepo.update, GardenRepo CRUD; +12 tests)
- [x] `tests/test_services.py` - Phases 4 & 6 (added settings + edge cases; +13 tests)
