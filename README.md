```
#######################################################################################
#   __  __             _      _   _           _   _____                _              #
#  |  \/  | __ _  __ _(_) ___| | | | ___ _ __| |_|_   _|___ __ _  ___ | | _____ _ __  #
#  | |\/| |/ _` |/ _` | |/ __| |_| |/ _ \ '__| '_ \| || '__| _` |/ __|| |/ / _ \ '__| #
#  | |  | | (_| | (_| | | (__|  _  |  __/ |  | |_) | || | | (_| | (__ |   <  __/ |    #
#  |_|  |_|\__,_|\__, |_|\___|_| |_|\___|_|  |_.__/|_||_|  \__,_|\___||_|\_\___|_|    #
#                                                        © 2026 ThePineappleExpress   #
# #####################################################################################

No-AI private desktop grow-log tracker built with Python and Kivy. 

Plant, cultivate, grow and log. 
Magic Herb Tracker allows user to track plants health and growth throughout it's whole life.  
Track many internal and environmental data points and take advantage of in-built suggestions 
for watering and feeding and master your grow. Vast database of strains and breeders allows
you to get started quickly. Choose your medium and fertilizers for optimal profiling.  

Current functionality:
- Empty garden landing with quick actions to add a seed.
- Seed entry form with validation, sliders for watering/feeding profiles, 
  and strain auto-suggestions (trie-based) from a local catalog.
- Garden list view containing all your plants.
- Plant details view with a horizontal event timeline and last-watering summary.
- Local JSON storage for plants and per-plant event logs.

Framework & stack
- Language: Python 3.13+
- UI Framework: Kivy 2.3.x (kv language + Python widgets).
- Data: Local JSON files in usr/db.

Project layout
- main.py: App entry point, screen manager.
- magicherbtracker.kv: Theme + Kivy rules/styles.
- labels.py, boxes.py, buttons.py, text_inputs.py: UI elements custom classes .
- empty_garden.py: Starting splash screen for when no garden is present.
- sow_seed.py: Seed entry workflow and validation.
- garden_view.py: Default view if garden is present.
- plant_details.py: Detail screen and events timeline.
- storage.py: JSON persistence helpers, saving, loading, etc.
- bin/db: seed catalog + trie data, for manual updates .
- usr/db: user garden database, plants.json to store basic info for all plants .
- usr/db/plants: events stored in individual json files for each plant.
  Name generated on save based on id from usr/db/plants.json.

Known issues
- Catalog auto-fill: `_apply_catalog_for_strain()` assumes a catalog record exists; 
  if the trie and catalog get out of sync it can throw.

Unknown/untested areas
- Cross-platform packaging (Windows/macOS/Linux builds) has not been validated here.
- Data migrations for schema changes are not implemented. We ball for now.
- Large event lists performance on the timeline view is unverified but we should be good, will test later.

Plan for finish
- Event editor (create/update/delete watering/feed/notes per plant).
- Feeding and watering profiles. Medium and gene dependent, adjusted on the fly from data on recent events. 
- Search/filter/sort in garden view.
- Maybe a small hint with last events data on mouse over in the garden list 
- Analytics (watering cadence, nutrient trends, stage timelines).
- Graphs screen (Detailed timeline views for environment and events).
- Password protection - privacy is a priority
- Database encryption
- Export/import for backups and sharing.
- Packaging workflow (PyInstaller or Briefcase).

Running locally
1. Create/activate a Python 3.13+ environment.
2. Install dependencies from pyproject.toml.
3. Run main.py.
```