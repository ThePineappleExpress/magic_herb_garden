APP_TITLE = "Magic Herb Tracker"

# Common buttons
BUTTON_SAVE = "Save"
BUTTON_CONFIRM = "Confirm"
BUTTON_CANCEL = "Cancel"
BUTTON_ADD = "Add"
BUTTON_DELETE = "Delete"
BUTTON_PLUS = "+"
BUTTON_MINUS = "-"
BUTTON_EDIT = "edit"

# Generic labels
LABEL_NAME = "Name"
LABEL_TYPE = "Type"
LABEL_QUANTITY = "Quantity"

# Messages
MSG_CONFIRM_DELETE = "Are you sure you want to delete this item?"

# Confirmation prompt title and variants
ARE_YOU_SURE_TITLE = "Are you sure?"
MSG_CONFIRM_CANCEL = "Discard changes?"
MSG_CONFIRM_EXIT = "Exit the garden?"

# Relative / time labels
TODAY = "Today"
YESTERDAY = "Yesterday"
DAYS_AGO = "{n} days ago"
WEEK_AGO_ONE = "{n} week ago"
WEEK_AGO_PLURAL = "{n} weeks ago"
MONTH_AGO_ONE = "{n} month ago"
MONTH_AGO_PLURAL = "{n} months ago"
YEAR_AGO_ONE = "{n} year ago"
YEAR_AGO_PLURAL = "{n} years ago"

# Generic labels
BACK = "Back"
DAY_LABEL = "Day"

# Plant details / health
HEALTH_HEALTHY = "Healthy"
HEALTH_MINOR = "Minor issues"
HEALTH_MODERATE = "Moderate issues"
HEALTH_SEVERE = "Severe issues"
STATUS_FLOWERING = "Flowering!"
STATUS_HARVESTED = "Harvested!"

# Event toggle labels
TOGGLE_TOP = "Top"
TOGGLE_PRUNE = "Prune"
TOGGLE_FLIP = "Flip"
FLIP_DONE = "Flipped"

# Event / plant field titles
EVENT_FIELD_TITLES = {
  "HEIGHT": "Height",
  "NODES": "Nodes",
  "SPACING": "Spacing",
  "MAIN_STEMS": "Main Stems",
  "COLOR": "Color",
  "MORPHOLOGY": "Morphology",
  "AIR_TEMP": "Air Temp",
  "HUMIDITY": "Humidity",
  "VPD": "VPD",
  "SOIL_PH": "Soil pH",
  "SOIL": "Soil",
  "PPFD": "PPFD",
  "LIGHT": "Light",
}

WATER_FIELD_TITLES = {
  "VOLUME": "Volume",
  "TEMP": "Temp",
  "PH": "pH",
  "PPM": "PPM",
}

# Common small labels
NAME_SEPARATOR = " | "

# Last event templates
LAST_WATER_TEMPLATE = "Last water: {vol} L, pH {ph}, {ppm} ppm @ {ts}"
LAST_EVENT_TEMPLATE = "Last event: {type} @ {ts}"

# Screen titles (used in various views)
SCREEN_TITLE_GARDEN = "looks [color={color}]NICE[/color]"
SCREEN_TITLE_DETAILS = "Just look at this [color={color}]BEAUTY[/color]"
SCREEN_TITLE_GRAPH = "Just look at this [color={color}]BEAUTY[/color]"
SCREEN_TITLE_ENV = "Let's talk [color={color}]ENVIRONMENT[/color] it?"
SCREEN_TITLE_ADD_GARDEN = "Create a new [color={color}]GARDEN[/color]"
SCREEN_TITLE_SELECT_GARDEN = "My magical [color={color}]GARDENS[/color]"
SCREEN_SETTINGS_TITLE = "Let's tweak some [color={color}]SETTINGS[/color]"


# Timeline tab labels
TAB_PLANT = "Plant"
TAB_ENVIRONMENT = "Environment"
TAB_WATER = "Water"
TAB_FOOD = "Food"

# Set environment
SET_ENV_WARNING_TITLE = "Watering and feeding:"
SET_ENV_WARNING_BODY = (
    "Consult the packaging or the breeder for estimated profiles.\n"
    "Values will adjust automatically during your plants life.\n"
    "If you are not sure just leave both sliders in the default position."
)

# Sow seed / fields
SEEDBANK_LABEL = "Seedbank: "
HINT_SELECT_NAME = "Select a name for your plant"
STRAIN_LABEL = "Strain: "
HINT_WHATS_ON_BOX = "What's on the box?"
INFO_LABEL = "Info: "
HINT_SAY_SOMETHING = "Say something about your plant"
HERITAGE_LABEL = "Heritage: "
GENES_SATIVA = "Sativa"
GENES_INDICA = "Indica"
GENES_HYBRID = "Hybrid"
TYPE_LABEL = "Type: "
TYPE_AUTOMATIC = "Automatic"
TYPE_PHOTOPERIODIC = "Photoperiodic"
FLOWERING_PERIOD_LABEL = "Flowering period: "
HINT_DAYS_TO_FLOWER = "Days to flower"

# Buttons
NEXT = "Next"

# Feeding / dropdown field labels (used in feeding rows)
FEED_VEG = "Veg"
FEED_ROOT = "Root"
FEED_SOIL = "Soil"
FEED_VIT = "Vit"

FEED_FLOWER = "Flower"
FEED_TOPS = "Tops"
FEED_CALMAG = "CalMag"
FEED_FUNGI = "Fungi"

# Notes label
LABEL_NOTES = "Notes"
NUTRIENTS = "Nutrients"
VIEW_TIMELINE = "View\nTimeline"

# Generic confirmations
YES = "Yes"
NO = "No"

# Fertilizer / medium strings
FERTILIZED_LABEL = "Fertilized: "
FERTILIZED = "Fertilized"
BARE = "Bare"
YOUR_FERTILIZER_LABEL = "Your fertilizer: "
FERTILIZER_ORGANIC = "Organic"
FERTILIZER_MINERAL = "Mineral"

# Environment defaults
EVERY_3_DAYS = "Every 3 days"
EVERY_2ND_WATERING = "Every 2nd Watering"
POT_LABEL_DEFAULT = "9L"

# Set environment labels
WATERING_LABEL = "Watering"
FEEDING_LABEL = "Feeding"
POT_SIZE_LABEL = "Pot size"
MEDIUM_LABEL = "Medium"
MEDIUM_SOIL = "Soil"
MEDIUM_COCO = "Coco"
MEDIUM_MINERAL = "Mineral"
MEDIUM_HYDRO = "Hydro"

# Additional frequency templates
EVERY_WATERING = "Every watering"
EVERY_3RD_WATERING = "Every 3rd watering"
EVERY_N_DAYS = "Every {n} days"

# Pot size format
POT_SIZE_FMT = "{n}L"

# Numeric/hint defaults
HINT_NUM_DEFAULT = "0.0"
HINT_AIR_TEMP_DEFAULT = "24"
HINT_RH_DEFAULT = "55"

# Misc small tokens
DASH = "–"

# Graph/button small labels
GRAPH_BTN_ABSOLUTE = "Absolute"
ML_PER_LITER = "ml Per liter"
ML = "ml"

# Settings screen
SETTINGS_CURRENT_PASSWORD = "Current password: "
SETTINGS_PASSWORD = "New password: "
HINT_CURRENT_PASSWORD = "Enter current password"
HINT_NO_PASSWORD_SET = "No password set"
SETTINGS_PASSWORD_CONFIRM = "Confirm password: "
SETTINGS_DB_PATH = "Database path: "
SETTINGS_SHADER_TOGGLE = "Animated background: "
HINT_ENTER_PASSWORD = "Enter password"
HINT_CONFIRM_PASSWORD = "Confirm password"
HINT_DB_PATH = "Path to database folder"
SETTINGS_SHADER_ON = "On"
SETTINGS_SHADER_OFF = "Off"
SETTINGS_THEME = "Theme: "
SETTINGS_SHADER_SELECT = "Shader style: "
SETTINGS_SHADER_RELOAD = "Reload"
SETTINGS_PIXEL_SCALE = "Pixel scale: "
SETTINGS_REMOVE_PASSWORD = "Remove Password"
WARN_SET_PASSWORD = "WARNING: Setting a password will encrypt the entire database.\nIf you forget or lose the password you will not be able to retrieve your data.\nAre you sure you want to continue?"
WARN_REMOVE_PASSWORD = "Are you sure you want to remove password protection and decrypt the database?\nYour data will be stored in plain JSON after this operation."
WARN_MOVE_DB_PATH = "This will move all garden and plant data files to the new location.\nThe app will restart automatically after the move.\nAre you sure you want to continue?"
SETTINGS_SELECT_FOLDER = "Select"
SETTINGS_LANGUAGE = "Language: "
SETTINGS_LANGUAGE_RESTART = "(restart required)"

# Sort / filter bar
SORT_BY = "Sort by:"
SORT_NAME = "Name"
SORT_BREEDER = "Breeder"
SORT_DATE_PLANTED = "Date Planted"
SORT_DATE_CREATED = "Date Created"
SORT_DAYS_TO_HARVEST = "Days to Harvest"
SORT_DAYS_TO_WATER = "Days to Water"
SORT_MEDIUM = "Medium"
SORT_PLANT_COUNT = "Plants"
SORT_NEXT_EVENT = "Next Event"
SORT_ASCENDING = "Ascending"
SORT_DESCENDING = "Descending"
FILTER_ACTIVE_ONLY = "Show only active"
SEARCH_HINT = "Search..."

# Garden list legend headers
LEGEND_GENES = "Genes"
LEGEND_PLANT = "Plant"
LEGEND_MEDIUM = "Medium"
LEGEND_LAST_WATER = "Last Water"
LEGEND_NEXT_WATER = "Next Water"
LEGEND_FLOWER = "Flower"
LEGEND_HARVEST = "Harvest"
LEGEND_GARDEN_NAME = "Garden"
LEGEND_GARDEN_TYPE = "Type"
LEGEND_PLANT_COUNT = "Plants"

# Garden / header buttons
OPTIONS = "Options"
EXIT_APP = "Exit\nApp"
ADD_PLANT = "Add Plant"
ADD_GARDEN = "Add\nGarden"
SELECT_GARDEN = "Select Garden"
VIEW_GARDENS = "View\nGardens"
DELETE_GARDEN = "Delete\nGarden"
MSG_CONFIRM_DELETE_GARDEN = "Are you sure you want to delete the selected garden and all plants in it?"
VIEW_SELECTED_PLANT = "View Selected Plant"
DELETE_SELECTED_PLANT = "Delete Selected Plant"

# Garden management screens
GARDEN_NAME_LABEL = "Garden name: "
HINT_GARDEN_NAME = "Name your garden"
GARDEN_TYPE_LABEL = "Type: "
GARDEN_TYPE_INDOOR = "Indoor"
GARDEN_TYPE_OUTDOOR = "Outdoor"
LIGHT_TYPE_LABEL = "Light type: "
LIGHT_WATTAGE_LABEL = "Wattage: "
HINT_LIGHT_WATTAGE = "Watts"
LIGHT_SCHEDULE_LABEL = "Light schedule: "
HINT_LIGHT_HOURS = "Hours on"
LOCATION_LABEL = "Location: "

# Light types
LIGHT_LED = "LED"
LIGHT_HPS = "HPS"
LIGHT_CFL = "CFL"

# Climate regions
CLIMATE_NH_TEMPERATE = "N. Hemisphere Temperate"
CLIMATE_MEDITERRANEAN = "Mediterranean"
CLIMATE_TROPICAL = "Tropical"
CLIMATE_SH_TEMPERATE = "S. Hemisphere Temperate"
CLIMATE_EQUATORIAL = "Equatorial"

# Location cascading dropdowns (outdoor gardens)
CONTINENT_LABEL = "Continent: "
COUNTRY_LABEL = "Country: "
CITY_LABEL = "City: "


LEGEND_TITLES = {
  "plant_height": "Plant Height (cm)",
  "num_nodes": "Number of Nodes",
  "node_spacing": "Node Spacing (cm)",
  "main_stem_number": "Main Stem Number",
  "air_temp_c": "Air Temperature (°C)",
  "rh_percent": "Relative Humidity (%)",
  "soil_moisture": "Soil Moisture Level",
  "soil_ph": "Soil pH",
  "vpd_kpa": "VPD (kPa)",
  "ppfd": "PPFD (µmol/m²/s)",
  "volume_l": "Water Volume (L)",
  "water_temp_c": "Water Temperature (°C)",
  "ph": "Water pH",
  "ppm": "Water PPM",
}

# Export / Import screen
EXPORT_IMPORT_TITLE = "Share and backup your [color={color}]TREASURE[/color]"
EXPORT_SELECT_GARDENS = "Select gardens:"
EXPORT_SELECT_ALL = "Select all"
EXPORT_DESELECT_ALL = "Deselect all"
EXPORT_TYPE_LABEL = "Export type:"
EXPORT_SAFE = "Safe (encrypted)"
EXPORT_OPEN = "Open (no password)"
EXPORT_PASSWORD = "Export password:"
EXPORT_PASSWORD_CONFIRM = "Confirm password:"
EXPORT_FILENAME_LABEL = "Filename:"
EXPORT_CHOOSE_LOCATION = "Choose export location"
BUTTON_EXPORT = "Export"
BUTTON_IMPORT = "Import"
EXPORT_NO_GARDENS_SELECTED = "Please select at least one garden to export."
EXPORT_SUCCESS = "Export complete:"
EXPORT_ERROR = "Export failed:"
IMPORT_CHOOSE_FILE = "Choose a .weed file to import"
IMPORT_PASSWORD_PROMPT = "This file is encrypted. Enter the export password:"
IMPORT_CONFLICT_WARNING = "{n} garden(s) in this file already exist and will be overwritten.\nAre you sure you want to continue?"
IMPORT_ERROR_CORRUPT = "The file appears to be corrupted or is not a valid .weed file."
IMPORT_ERROR_WRONG_PW = "Wrong password or the file is corrupted."
IMPORT_SUCCESS = "Import complete: {gardens} garden(s) and {events} event file(s) imported."
SETTINGS_EXPORT_IMPORT = "Export / Import Data"
SETTINGS_EXPORT_CSV = "Export to CSV"
CSV_EXPORT_TITLE = "Export gardens to [color={color}]CSV[/color]"
CSV_EXPORT_CHOOSE_LOCATION = "Choose export location"
CSV_EXPORT_FILENAME_LABEL = "Filename:"
CSV_EXPORT_SUCCESS = "CSV export complete:"
CSV_EXPORT_ERROR = "CSV export failed:"
CSV_EXPORT_NO_GARDENS = "Please select at least one garden to export."

import sys

def get(key: str) -> str:
    """Return the string for a constant-like key, or the key itself."""
    return getattr(sys.modules[__name__], key, key)
