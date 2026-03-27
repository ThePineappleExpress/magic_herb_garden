
'''
░█▄█░█▀█░█▀▀░▀█▀░█▀▀░█░█░█▀▀░█▀▄░█▀▄░▀█▀░█▀▄░█▀█░█▀▀░█░█░█▀▀░█▀▄
░█░█░█▀█░█░█░░█░░█░░░█▀█░█▀▀░█▀▄░█▀▄░░█░░█▀▄░█▀█░█░░░█▀▄░█▀▀░█▀▄
░▀░▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀░▀░▀▀░░░▀░░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀░▀
                                      © 2026 ThePineappleExpress

'''
Desktop grow-log tracker built with Python, Kivy, and Rust.

Plant, cultivate, grow and log. Magic Herb Tracker lets you follow each plant through its
entire lifecycle - from sowing to harvest - logging waterings, feedings, and notes along the
way. A local strain/breeder catalog with trie-based autocomplete gets you started fast.
All data stays on your machine, stored as JSON (optionally AES-256-GCM encrypted with a
Rust-backed crypto layer).

---

## Features

- **Multi-garden support** - create and switch between independent gardens.
- **Plant lifecycle tracking** - log sow date, strain, medium, and days-to-flower estimate; track vegetative and flowering stages.
- **Event logging** - record waterings, feedings (with per-nutrient amounts), environment snapshots, and free-text notes per plant. Real-time VPD calculation on environment events.
- **Timeline & graphs** - tabbed per-plant timeline (Plant / Environment / Water / Food) with native Kivy Garden line graphs for environmental and nutrient data.
- **Watering/feeding profiles** - slider-based profiles stored per plant, with calculated suggestions based on history.
- **Strain autocomplete** - trie-backed local catalog of strains and breeders; suggestions fire as you type.
- **Password protection + encryption** - optional password gate on startup with exponential backoff on failed attempts. When a password is set the entire database is encrypted with AES-256-GCM on disk via a Rust backend (`crypto_rs`). Removing the password decrypts all data back to plain JSON.
- **Export & Import (.weed)** - back up or transfer one or more gardens. Exported as a custom binary `.weed` file (v2 format: magic header, per-section zlib payloads, HMAC-SHA256 footer). Choose *Safe* to encrypt with an independent export password, or *Open* for unencrypted transfer.
- **CSV export** - export selected gardens to a flat CSV (89 columns) for external analysis. One row per event, sorted chronologically.
- **Themes** - six built-in TOML-based themes (dark, green, light, retro, vaporwave, water). User themes can be added to the OS data directory and are discovered automatically.
- **GLSL shaders** - four animated background shaders (smoke, water, ice, rain) with runtime swapping and a pixel-scale slider (1-64). Toggle on/off from Settings.
- **Localisation** - UI language switchable at runtime. Ships with English and Righteous (reggae/patois dialect). Modular loader discovers new languages automatically from `bin/lang/`.
- **Fully offline** - no network calls; all storage is local JSON under the OS data directory.
- **Production builds** - compile to a standalone binary via Nuitka + maturin. No Python runtime required for end users.

---

## Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Language     | Python 3.13+                                    |
| Crypto       | Rust (PyO3) - `crypto_rs` (AES-256-GCM, PBKDF2) |
| UI framework | Kivy 2.3.x + KV language                        |
| Charts       | kivy-garden (Graph / LinePlot)                  |
| Data         | Local JSON (jsonschema validation)              |
| Architecture | Repository pattern + service layer (no Kivy)    |
| Paths        | platformdirs (OS-appropriate data directories)  |
| Build        | maturin (Rust) + Nuitka (native binary)         |
| Tests        | Custom runner (463 tests)                       |
| CI           | GitHub Actions (Python 3.13 / Ubuntu)           |

---

## Security & encryption

### Overview

With no password set, all data files are stored as plain JSON. Once the user sets a
password from the Settings screen, every sensitive data file on disk is transparently
encrypted. The app decrypts files on read and re-encrypts them on write throughout the
session. Removing the password decrypts all files back to plain JSON.

`settings.json` is deliberately **never encrypted** - the app needs to read the language,
theme, shader toggle, and database path before the user has entered a password.

The password unlock screen enforces **exponential backoff** after failed attempts
(2^(n-1) seconds). The fail counter persists across app restarts.

---

### Cryptographic design

All cryptographic primitives (AES-256-GCM, PBKDF2-HMAC-SHA256, constant-time comparison,
OS-random generation) are implemented in Rust via the `crypto_rs` PyO3 extension for
performance and memory safety.

#### 1. Password verification (PBKDF2-HMAC-SHA256)

When a password is set, two independent key-derivation operations are performed from
the same password:

```
verification_salt = os.urandom(16) # 16 random bytes
enc_salt = os.urandom(16) # separate 16 random bytes

verification_hash = PBKDF2-HMAC-SHA256(password, verification_salt, iterations=600_000)
encryption_key = PBKDF2-HMAC-SHA256(password, enc_salt, iterations=600_000, dklen=32)
```

Stored in `settings.json` under `"password"`:

```json
{
  "salt": "<32 hex chars - verification salt>",
  "hash": "<64 hex chars - PBKDF2 verification digest>",
  "enc_salt": "<32 hex chars - encryption key derivation salt>",
  "iterations": 600000
}
```

At unlock time the app re-derives the verification hash and compares it with
constant-time comparison (via Rust `subtle` crate). The hash stored in `settings.json`
**cannot** be used to derive the encryption key - the two PBKDF2 calls use different
salts, so their outputs are cryptographically independent.

#### 2. Data encryption (AES-256-GCM)

The 32-byte encryption key derived above is passed to the Rust `aes_gcm` crate.
Each write produces a new random 12-byte IV (nonce):

```
iv = os.urandom(12) # random per write
aad = filename.encode() # binds ciphertext to this specific file
ciphertext = encrypt(key, iv, plaintext_bytes, aad)

file bytes = b"ENC1" + iv (12 B) + ciphertext+tag (variable)
```

- **`b"ENC1"`** - 4-byte magic prefix. Lets the app detect whether a file is encrypted
  or plaintext without any external state machine, enabling graceful migration.
- **AAD (Additional Authenticated Data)** - the filename (e.g. `abc123.json`) is passed
  as AAD, binding each ciphertext to its intended file. Moving an encrypted blob to a
  different filename causes GCM authentication to fail on decrypt.
- **GCM authentication tag** - appended automatically by the encrypt function; checked
  automatically on decrypt. A corrupt file, wrong key, or mismatched AAD raises an
  error which the storage layer catches and logs; the caller receives `None`/empty data
  rather than a crash.
- **Unique IV per write** - encrypting the same JSON twice produces different
  ciphertext blobs, so attackers cannot detect whether a record changed by comparing
  file hashes.

#### 3. Key lifetime

`CryptoContext` (in `crypto.py`) is a process-wide singleton that holds the
active key in memory as a mutable `bytearray`:

```
app start      -> CryptoContext._key = None
successful unlock -> CryptoContext.set_key(derived_key) # stores as bytearray
pw changed     -> old bytearray zeroed, new key stored
pw removed     -> CryptoContext.clear() # zeros bytearray, then sets None
app exit       -> process memory freed
```

The key is stored as a `bytearray` (not immutable `bytes`) so it can be
explicitly zeroed in-place before replacement or clearing, minimising the
window where key material is recoverable from process memory. The key is
never written to disk. `settings.json` contains only the PBKDF2
verification hash and the two salts - neither can reconstruct the key without
the original password.

#### 4. Migration (encrypt / decrypt / re-encrypt)

`migrate.py` provides three functions that iterate every protected path
(`garden/*.json`, `plants/*.json`, `plants_index.json`) and transform them in-place
using atomic `.tmp` sibling writes:

| Function                               | When used               |
|----------------------------------------|-------------------------|
| `encrypt_all_data(key)`                | First-time password set |
| `decrypt_all_data(key)`                | Password removed        |
| `reencrypt_all_data(old_key, new_key)` | Password changed        |

Each function is idempotent: already-encrypted files are skipped by
`encrypt_all_data`; already-plaintext files are skipped by `decrypt_all_data`.
`reencrypt_all_data` leaves a file untouched and logs a warning if decryption
with the old key fails.

#### 5. UI confirmation prompts

Before any destructive encryption operation the user sees a confirmation screen:

- **Setting a password for the first time** - warns that a forgotten password means
  permanent data loss; requires explicit YES.
- **Removing a password** - confirms intent to decrypt and store data as plain JSON;
  requires the current password to be typed in settings before the prompt is shown.

---

### Threat model & limitations

| Threat | Status |
|---|---|
| Bypass UI gate by deleting `"password"` from `settings.json` | Mitigated - data files contain unreadable ciphertext without the derived key |
| Brute-force offline password attack on `settings.json` | Mitigated by 600,000-iteration PBKDF2; exponential backoff on unlock screen |
| Attacker reads source code to find the key | No hardcoded key; key is never written anywhere - only derivable from the correct password |
| In-memory key extraction | Partially mitigated - key stored as mutable `bytearray` and zeroed on clear/replace |
| `settings.json` tampered to provide a forged `enc_salt`| Results in a wrong derived key -> GCM tag check fails -> data unreadable; no silent bypass|


---

## Installation (pre-built binaries)

Download the latest release from the [Releases](https://github.com/ThePineappleExpress/magic_herb_tracker/releases) page.

### Linux

```bash
tar xzf magic-herb-tracker-*-linux-x86_64.tar.gz
cd magic-herb-tracker-*-linux-x86_64
chmod +x magic-herb-tracker
./magic-herb-tracker
```

The archive includes a `.desktop` file - copy it to `~/.local/share/applications/` for menu integration.

If you get missing library errors, install the SDL2/OpenGL runtime:

```bash
sudo apt install libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 \
  libsdl2-ttf-2.0-0 libgl1-mesa-glx
```

### Windows

- **Installer:** Download the `-setup.exe`, run it, follow the wizard. Creates a desktop shortcut and Start Menu entry.
- **Portable:** Download the `.zip`, extract anywhere, run `magic-herb-tracker.exe`.

> Windows SmartScreen may warn "Windows protected your PC" because the binary is not code-signed.
> Click **More info** → **Run anyway**.

### Data location

Your grow data is stored in your OS data directory, separate from the application:

- **Linux:** `~/.local/share/MagicHerbTracker/db/`
- **Windows:** `%APPDATA%\MagicHerbTracker\db\`

Uninstalling the app does not delete your data.

---

## Development setup

```bash
# 1. Clone and enter the project
git clone https://github.com/ThePineappleExpress/magic_herb_tracker.git
cd magic_herb_tracker

# 2. Install dependencies (requires uv and Rust toolchain)
uv sync --group build

# 3. Build the Rust crypto extension
uv run maturin develop --release --manifest-path crypto_rs/Cargo.toml

# 4. Run the app
uv run python main.py
```

Run the test suite:

```bash
uv run python run_unit_tests.py
```

### Building a standalone binary

```bash
# Full build: Rust extension + Nuitka compilation + archive
uv run python build.py

# Skip Rust step if already built
uv run python build.py --skip-maturin

# Folder mode (faster, useful for debugging)
uv run python build.py --no-onefile
```

Output lands in `dist/magic-herb-tracker-<version>-<platform>.zip`.

CI builds for both Linux and Windows are triggered automatically by pushing a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

---

## Use manual

> Full instructions with screenshots are available on the [landing page](https://thepineapple.express/instructions.html).

### First launch

On first launch the app opens at **Select Garden** (or directly into your only garden if
exactly one exists). No password is required until you set one in Settings.

If upgrading from a previous version, the app automatically migrates data from the legacy
`usr/db/` location to the OS-appropriate data directory on first run.

### Managing gardens

- From **Select Garden**, click **Add Garden** to create a new garden with a name and
  optional description.
- Click any existing garden card to make it the active garden and enter Garden View.

### Garden View

The main list of all plants in the active garden. Each row shows the plant name, strain,
current stage indicator (vegetative / flowering), days-old counter, and last-watering
status - green = watered recently, yellow = due soon, red = overdue.

- **Add Plant**
1. **Name Plant** - enter strain name (autocomplete fires after 2 characters), breeder,
   sow date, medium (soil / coco / hydro), and a days-to-flower estimate. Watering and
   feeding profile sliders set the baseline cadence used by suggestions.
2. **Set Environment** - record grow-space parameters (tent dimensions, lights, temperature
   range). Saved with the plant and used by the suggestion engine.
3. Confirm to save and return to Garden View.

### Plant Details

Shows a summary card (strain, stage, days old, last watering) and a horizontally
scrollable mini-timeline of recent events.

- **Add Event** - opens the event entry screen.
- **Timeline** - opens the full timeline and graphs screen for this plant.
- **Delete** - triggers a confirmation screen before permanently removing the plant
  and all its events.

### Adding an event

Choose an event type from the dropdown:

| Type        | What to fill in                                      |
|-------------|------------------------------------------------------|
| Environment | Air temp, Humidity, medium pH, light, light schedule |
| Watering    | Volume (ml/L), input pH                              |
| Feeding     | Per-nutrient amounts, EC, input pH, runoff pH        |
| Log         | Free-text note                                       |

Hit **Save** to record the event with the current timestamp. The plant's last-watering
counter in Garden View updates immediately. Environment events include real-time VPD
calculation.

### Timeline & graphs

Tabbed view with four sections:

- **Plant** - lifecycle events (sow, top, prune, flip).
- **Environment** - temperature, humidity, VPD, light data.
- **Water** - watering volume, pH, PPM over time.
- **Food** - per-nutrient feeding amounts, EC, runoff pH.

Each tab shows per-metric line graphs. Toggle a metric with its legend button. Pan
left/right through the full event history.

### Settings

Accessible from the navigation area on any main screen.

- **Language** - select a locale from the dropdown; takes effect immediately.
- **Theme** - choose from six built-in themes (dark, green, light, retro, vaporwave, water).
- **Animated background** - toggle the GLSL shader on/off. When enabled, choose a shader
  (smoke, water, ice, rain) and adjust the pixel scale (1-64). Reload button applies
  changes without restart.
- **Password** - enter the current password (disabled and greyed-out when none is set),
  then type and confirm a new password to set or change one.
- **Remove Password** - inline button in the current-password row, visible only when a
  password is active. Enter the current password and press it; a confirmation prompt
  explains that this will decrypt the database before proceeding.
- **Database path** - relocate the database to a custom directory.
- **Export / Import Data** - navigates to the Export & Import screen (see below).
- **Export to CSV** - navigates to the CSV Export screen.

### Export & Import

Reach from Settings -> **Export / Import Data**.

**Export**
1. Select which gardens to include (all are pre-checked; use *Select all* / *Deselect all*).
2. Choose *Safe (encrypted)* to protect the file with a separate export password, or
   *Open (no password)* for an unencrypted transfer.
3. If Safe: type a password and confirm it.
4. Press **Export** - a directory chooser opens. Pick a destination folder and adjust the
   default filename (`export_YYYY-MM-DD.weed`) if desired, then confirm.

**Import**
1. Press **Import** - a file chooser opens filtered to `*.weed` files.
2. Select the file. If it is encrypted, a password prompt appears.
3. If any garden in the file already exists on disk, a confirmation prompt warns of
   overwrite before proceeding.
4. Imported data is written to disk and the garden list refreshes automatically.

### CSV Export

Reach from Settings -> **Export to CSV**.

1. Select which gardens to include.
2. Press **Export** - choose a destination for the `.csv` file.
3. The CSV contains 89 columns covering garden info, plant metadata, event data,
   measurements (watering, feeding, environment), and IDs. One row per event, sorted
   chronologically per plant.

---

## Project layout

```
main.py                 App entry point, ScreenManager setup, theme/lang init
magicherbtracker.kv     Theme colours, fonts, KV layout rules
screens.py              BaseScreen (GLSL shader background via fx.py)
fx.py                   SmokeShaderWidget - RenderContext GLSL rendering with live uniforms

# Data layer (repository pattern)
data.py                 PlantRepository, EventRepository, GardenRepository, SettingsRepository,
                        IndexRepository, PhotoRepository - cached CRUD with schema validation
storage.py              Low-level JSON read/write with transparent encryption, atomic writes
validators.py           jsonschema definitions + error-list validators (check_plant/event/garden)
constants.py            Canonical event type strings + normalize_event_type()

# Service layer (pure Python, no Kivy imports)
services/
  garden_service.py     Garden plants view, filtering, sorting
  plant_service.py      Plant lifecycle: create, update, event side-effects
  event_service.py      Event CRUD wrappers, sorted loading
  settings_service.py   Settings read/write, shader prefs, password checks
  catalog_service.py    Seed catalog lookup, strain/breeder resolution
  formatting.py         Relative time, health indicators, nutrient status

helpers.py              Date helpers, password hashing (PBKDF2), key derivation, nav utils
crypto.py               CryptoContext singleton, delegates to crypto_rs for AES-256-GCM
crypto_rs/              Rust PyO3 extension: AES-256-GCM, PBKDF2, constant-time comparison
migrate.py              In-place encrypt_all_data / decrypt_all_data / reencrypt_all_data
weed_format.py          .weed binary export/import format v2 (zlib + optional AES-GCM, HMAC-SHA256 footer)
export_import_screen.py Export & Import screen (.weed file handling)
csv_export_screen.py    CSV Export screen (flat 89-column export)
build.py                Production build script (maturin + Nuitka + archive)
effects.py              Shake-and-flash animation helper
ui_builders.py          Reusable layout builders: screen scaffolding, water/feeding fields,
                        nutrients panel (dual-mode: input widgets or read-only display)
lang.py                 Language proxy - reads preference, loads module dynamically

# Screens (Kivy UI - no direct storage imports)
password_check.py       Password gate screen (exponential backoff)
select_garden.py        Multi-garden picker
add_garden.py           New garden creation
sow_seed.py             Plant entry form + strain autocomplete
set_environment.py      Grow-space parameter entry
garden_view.py          Plant list (RecycleView) with status indicators
plant_details.py        Per-plant summary + mini event timeline
add_event.py            Event entry form (watering / feeding / environment / log) + VPD
timeline_view.py        Tabbed timeline + native Kivy graphs (Plant / Env / Water / Food)
are_you_sure.py         Confirmation dialog screen
settings_screen.py      Language, theme, shader, password, db path, export/import navigation

# Custom Kivy widgets
boxes.py                Custom Kivy BoxLayout subclasses
buttons.py              Custom buttons + HoverBehavior mixin
labels.py               Custom label widgets
text_inputs.py          Custom text input widgets
custom_dropdown.py      Styled dropdown widget
strain_trie.py          Trie for strain/breeder autocomplete

# Tests (463 total)
tests/
  test_widgets.py            Kivy widget smoke tests (67)
  test_services.py           Service layer + event side-effects (50)
  test_screen_logic.py       VPD, graphs, health, harvest, export logic (45)
  test_data_repos.py         Repository + index + validator tests (40)
  test_constants.py          Event type normalisation (31)
  test_helpers.py            Date/password/colour helpers (29)
  test_validators.py         JSON schema validation (27)
  test_photo_utils.py        Image processing + thumbnails (23)
  test_storage.py            JSON read/write + atomic writes (22)
  test_crypto.py             AES-256-GCM encryption round-trips (22)
  test_photo_storage.py      Photo file I/O (12)
  test_weed_format.py        Binary .weed export/import (11)
  test_csv_export.py         CSV row builders (11)
  test_theme_loader.py       TOML theme loading + shader colours (9)
  test_catalog_service.py    Strain catalog lookups (9)
  test_breeder_trie.py       Breeder trie search (9)
  test_strain_trie.py        Strain trie search (8)
  test_migrate.py            Encrypt/decrypt/re-encrypt migrations (8)
  test_lang.py               Language module loading (8)
  test_integration.py        Multi-layer lifecycle workflows (8)
  test_daylight.py           Astral daylight calculations (6)
  test_storage_helpers.py    Plant list normalisation (4)
  test_shader_loader.py      GLSL shader discovery + loading (4)
  kivy_test_helper.py        Headless Kivy test harness (shared fixture)

# Resources
bin/db/                 Read-only seed catalog + pre-built trie JSON files + locations
bin/lang/               Language modules + loader
bin/themes/             TOML theme files (dark, green, light, retro, vaporwave, water)
bin/shaders/            GLSL fragment shaders (smoke, water, ice, rain)
res/branding/           Application icons (.ico, .icns, .png)
packaging/              Platform installer configs (Inno Setup)
landing/                Web landing page assets
```

---

## Data layout

```
<OS data dir>/   (e.g. ~/.local/share/MagicHerbTracker/db/ on Linux)
  settings.json          App settings (password hash, language, theme, shader) - always plaintext
  plants_index.json      Lightweight index: plant_id -> last_event_ts, event_count
                         (AES-256-GCM encrypted when a password is set)
  garden/<uuid>.json     Garden metadata + plants array
                         (AES-256-GCM encrypted when a password is set)
  plants/<uuid>.json     Per-plant event log
                         (AES-256-GCM encrypted when a password is set)

  Encrypted file format: b"ENC1" (4 bytes) + IV (12 bytes) + ciphertext+GCM-tag (AAD = filename)

bin/db/
  seed_catalog.json      Strain/breeder reference data (read-only, never encrypted)
  seed_trie.json         Pre-built trie for strain autocomplete
  breeder_trie.json      Pre-built trie for breeder autocomplete
  locations.json         Location reference data
```

---

## Known limitations

- `_apply_catalog_for_strain()` assumes trie and catalog are in sync; mismatches log an error.

---

## Pending work

- Garden timeline in garden view: a calendar-like scrollable/zoomable view with rows for plants and columns for dates that shows all plants laid out through time.
- Background I/O and improved cache invalidation for large datasets.
- Potential API entry points to grab data from commercially available devices (SpiderFarmer, MarsHydro, ViparSpectra)