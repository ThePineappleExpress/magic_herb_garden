APP_TITLE = "Magic Herb Tracker"

# Common buttons
BUTTON_SAVE = "Speichern"
BUTTON_CONFIRM = "Bestätigen"
BUTTON_CANCEL = "Abbrechen"
BUTTON_ADD = "Hinzufügen"
BUTTON_DELETE = "Löschen"
BUTTON_PLUS = "+"
BUTTON_MINUS = "-"
BUTTON_EDIT = "bearbeiten"

# Generic labels
LABEL_NAME = "Name"
LABEL_TYPE = "Typ"
LABEL_QUANTITY = "Menge"

# Messages
MSG_CONFIRM_DELETE = "Bist du sicher, dass du dieses Element löschen möchtest?"
MSG_CONFIRM_DELETE_PLANT = "Bist du sicher, dass du die ausgewählte Pflanze löschen möchtest?"
MSG_CONFIRM_CANCEL_CHANGES = "Bist du sicher, dass du abbrechen und alle ungespeicherten Änderungen verlieren möchtest?"

# Confirmation prompt title and variants
ARE_YOU_SURE_TITLE = "Bist du sicher?"
MSG_CONFIRM_CANCEL = "Änderungen verwerfen?"
MSG_CONFIRM_EXIT = "Den Garten verlassen?"

# Relative / time labels
TODAY = "Heute"
YESTERDAY = "Gestern"
DAYS_AGO = "vor {n} Tagen"
WEEK_AGO_ONE = "vor {n} Woche"
WEEK_AGO_PLURAL = "vor {n} Wochen"
MONTH_AGO_ONE = "vor {n} Monat"
MONTH_AGO_PLURAL = "vor {n} Monaten"
YEAR_AGO_ONE = "vor {n} Jahr"
YEAR_AGO_PLURAL = "vor {n} Jahren"

# Generic labels
BACK = "Zurück"
DAY_LABEL = "Tag"

# Plant details / health
HEALTH_HEALTHY = "Gesund"
HEALTH_MINOR = "Leichte Probleme"
HEALTH_MODERATE = "Mäßige Probleme"
HEALTH_SEVERE = "Schwere Probleme"
STATUS_FLOWERING = "Blüht!"
STATUS_HARVESTED = "Geerntet!"

# Event toggle labels
TOGGLE_TOP = "Kappen"
TOGGLE_PRUNE = "Beschneiden"
TOGGLE_FLIP = "Umschalten"
FLIP_DONE = "Umgeschaltet"

# Event / plant field titles
EVENT_FIELD_TITLES = {
  "HEIGHT": "Höhe",
  "NODES": "Knoten",
  "SPACING": "Abstand",
  "MAIN_STEMS": "Haupttriebe",
  "COLOR": "Farbe",
  "MORPHOLOGY": "Morphologie",
  "AIR_TEMP": "Lufttemp.",
  "HUMIDITY": "Luftfeuchte",
  "VPD": "VPD",
  "SOIL_PH": "Boden-pH",
  "SOIL": "Boden",
  "PPFD": "PPFD",
  "LIGHT": "Licht",
}

WATER_FIELD_TITLES = {
  "VOLUME": "Volumen",
  "TEMP": "Temp.",
  "PH": "pH",
  "PPM": "PPM",
}

# Common small labels
NAME_SEPARATOR = " | "

# Last event templates
LAST_WATER_TEMPLATE = "Letzte Bewässerung: {vol} L, pH {ph}, {ppm} ppm @ {ts}"
LAST_EVENT_TEMPLATE = "Letztes Ereignis: {type} @ {ts}"

# Screen titles (used in various views)
SCREEN_TITLE_GARDEN = "Mein magischer [color={color}]GARTEN[/color]"
SCREEN_TITLE_DETAILS = "Schau dir diese [color={color}]SCHÖNHEIT[/color] an"
SCREEN_TITLE_GRAPH = "Schau dir diese [color={color}]SCHÖNHEIT[/color] an"
SCREEN_TITLE_ENV = "Wo werde ich es [color={color}]ANBAUEN[/color]?"
SCREEN_TITLE_SOW_SEED = "Erzähl etwas über deinen [color={color}]Samen[/color]"
SCREEN_TITLE_ADD_GARDEN = "Erstelle einen neuen [color={color}]GARTEN[/color]"
SCREEN_TITLE_SELECT_GARDEN = "Wähle einen [color={color}]GARTEN[/color]"
SCREEN_SETTINGS_TITLE = "Passen wir die [color={color}]EINSTELLUNGEN[/color] an"
SCREEN_TITLE_PASSWORD = "Gib dein [color={color}]PASSWORT[/color] ein"


# Timeline tab labels
TAB_PLANT = "Pflanze"
TAB_ENVIRONMENT = "Umgebung"
TAB_WATER = "Wasser"
TAB_FOOD = "Dünger"

# Set environment
SET_ENV_WARNING_TITLE = "Bewässerung und Düngung:"
SET_ENV_WARNING_BODY = (
    "Schaue auf der Verpackung oder beim Züchter nach geschätzten Profilen.\n"
    "Die Werte passen sich automatisch im Laufe des Pflanzenlebens an.\n"
    "Wenn du unsicher bist, lass beide Regler in der Standardposition."
)

# Sow seed / fields
SEEDBANK_LABEL = "Samenbank: "
HINT_SELECT_NAME = "Wähle einen Namen für deine Pflanze"
STRAIN_LABEL = "Sorte: "
HINT_WHATS_ON_BOX = "Was steht auf der Packung?"
INFO_LABEL = "Info: "
HINT_SAY_SOMETHING = "Sag etwas über deine Pflanze"
HERITAGE_LABEL = "Herkunft: "
GENES_SATIVA = "Sativa"
GENES_INDICA = "Indica"
GENES_HYBRID = "Hybrid"
TYPE_LABEL = "Typ: "
TYPE_AUTOMATIC = "Automatisch"
TYPE_PHOTOPERIODIC = "Photoperiodisch"
FLOWERING_PERIOD_LABEL = "Blütezeit: "
HINT_DAYS_TO_FLOWER = "Tage bis zur Blüte"

# Buttons
NEXT = "Weiter"

# Feeding / dropdown field labels (used in feeding rows)
FEED_VEG = "Wuchs"
FEED_ROOT = "Wurzel"
FEED_SOIL = "Boden"
FEED_VIT = "Vit"

FEED_FLOWER = "Blüte"
FEED_TOPS = "Spitzen"
FEED_CALMAG = "CalMag"
FEED_FUNGI = "Pilze"

# Notes label
LABEL_NOTES = "Notizen"
NUTRIENTS = "Nährstoffe"
VIEW_TIMELINE = "Zeitleiste\nanzeigen"

# Generic confirmations
YES = "Ja"
NO = "Nein"

# Fertilizer / medium strings
FERTILIZED_LABEL = "Gedüngt: "
FERTILIZED = "Gedüngt"
BARE = "Ohne Dünger"
YOUR_FERTILIZER_LABEL = "Dein Dünger: "
FERTILIZER_ORGANIC = "Organisch"
FERTILIZER_MINERAL = "Mineralisch"

# Environment defaults
EVERY_3_DAYS = "Alle 3 Tage"
EVERY_2ND_WATERING = "Jede 2. Bewässerung"
POT_LABEL_DEFAULT = "9L"

# Set environment labels
WATERING_LABEL = "Bewässerung"
FEEDING_LABEL = "Düngung"
POT_SIZE_LABEL = "Topfgröße"
MEDIUM_LABEL = "Substrat"
MEDIUM_SOIL = "Erde"
MEDIUM_COCO = "Kokos"
MEDIUM_MINERAL = "Mineralisch"
MEDIUM_HYDRO = "Hydro"

# Additional frequency templates
EVERY_WATERING = "Bei jeder Bewässerung"
EVERY_3RD_WATERING = "Jede 3. Bewässerung"
EVERY_N_DAYS = "Alle {n} Tage"

# Pot size format
POT_SIZE_FMT = "{n}L"

# Numeric/hint defaults
HINT_NUM_DEFAULT = "0.0"
HINT_AIR_TEMP_DEFAULT = "24"
HINT_RH_DEFAULT = "55"

# Misc small tokens
DASH = "–"

# Graph/button small labels
GRAPH_BTN_ABSOLUTE = "Absolut"
ML_PER_LITER = "ml pro Liter"
ML = "ml"

# Settings screen
SETTINGS_CURRENT_PASSWORD = "Aktuelles Passwort: "
SETTINGS_PASSWORD = "Neues Passwort: "
HINT_CURRENT_PASSWORD = "Aktuelles Passwort eingeben"
HINT_NO_PASSWORD_SET = "Kein Passwort gesetzt"
SETTINGS_PASSWORD_CONFIRM = "Passwort bestätigen: "
SETTINGS_DB_PATH = "Datenbankpfad: "
SETTINGS_SHADER_TOGGLE = "Animierter Hintergrund: "
HINT_ENTER_PASSWORD = "Passwort eingeben"
HINT_CONFIRM_PASSWORD = "Passwort bestätigen"
HINT_DB_PATH = "Pfad zum Datenbankordner"
SETTINGS_SHADER_ON = "An"
SETTINGS_SHADER_OFF = "Aus"
SETTINGS_THEME = "Design: "
SETTINGS_SHADER_SELECT = "Shader-Stil: "
SETTINGS_SHADER_RELOAD = "Neu laden"
SETTINGS_PIXEL_SCALE = "Pixelskalierung: "
SETTINGS_REMOVE_PASSWORD = "Passwort entfernen"
WARN_SET_PASSWORD = "WARNUNG: Das Setzen eines Passworts verschlüsselt die gesamte Datenbank.\nWenn du das Passwort vergisst oder verlierst, kannst du deine Daten nicht wiederherstellen.\nBist du sicher, dass du fortfahren möchtest?"
WARN_REMOVE_PASSWORD = "Bist du sicher, dass du den Passwortschutz entfernen und die Datenbank entschlüsseln möchtest?\nDeine Daten werden danach als einfaches JSON gespeichert."
WARN_MOVE_DB_PATH = "Dadurch werden alle Garten- und Pflanzendateien an den neuen Speicherort verschoben.\nDie App startet nach dem Verschieben automatisch neu.\nBist du sicher, dass du fortfahren möchtest?"
SETTINGS_SELECT_FOLDER = "Auswählen"
SETTINGS_LANGUAGE = "Sprache: "
SETTINGS_LANGUAGE_RESTART = "(Neustart erforderlich)"

# Sort / filter bar
SORT_BY = "Sortieren:"
SORT_NAME = "Name"
SORT_BREEDER = "Züchter"
SORT_DATE_PLANTED = "Pflanzdatum"
SORT_DATE_CREATED = "Erstelldatum"
SORT_DAYS_TO_HARVEST = "Tage bis Ernte"
SORT_DAYS_TO_WATER = "Tage bis Bewässerung"
SORT_MEDIUM = "Substrat"
SORT_PLANT_COUNT = "Pflanzen"
SORT_NEXT_EVENT = "Nächstes Ereignis"
SORT_ASCENDING = "Aufsteigend"
SORT_DESCENDING = "Absteigend"
FILTER_ACTIVE_ONLY = "Nur aktive anzeigen"
SEARCH_HINT = "Suchen..."

# Garden list legend headers
LEGEND_GENES = "Gene"
LEGEND_PLANT = "Pflanze"
LEGEND_MEDIUM = "Substrat"
LEGEND_LAST_WATER = "Letzte Bewässerung"
LEGEND_NEXT_WATER = "Nächste Bewässerung"
LEGEND_FLOWER = "Blüte"
LEGEND_HARVEST = "Ernte"
LEGEND_GARDEN_NAME = "Garten"
LEGEND_GARDEN_TYPE = "Typ"
LEGEND_PLANT_COUNT = "Pflanzen"

# Garden / header buttons
OPTIONS = "Optionen"
EXIT_APP = "App\nbeenden"
EXIT_GARDEN = "Garten\nverlassen"
ENTER_GARDEN = "Garten betreten"
ADD_PLANT = "Pflanze hinzufügen"
ADD_GARDEN = "Garten hinzufügen"
SELECT_GARDEN = "Garten auswählen"
VIEW_GARDENS = "Gärten\nanzeigen"
DELETE_GARDEN = "Garten löschen"
MSG_CONFIRM_DELETE_GARDEN = "Bist du sicher, dass du den ausgewählten Garten und alle Pflanzen darin löschen möchtest?"
VIEW_SELECTED_PLANT = "Ausgewählte Pflanze anzeigen"
DELETE_SELECTED_PLANT = "Ausgewählte Pflanze löschen"

# Password check screen
PW_TOO_MANY_ATTEMPTS = "Zu viele Versuche. Warte {n}s."
PW_WRONG_PASSWORD = "Falsches Passwort. Warte {n}s vor erneutem Versuch."
PW_BUTTON_UNLOCK = "Entsperren"

# Add event
HINT_EVENT_NOTES = "Erzähl, was heute passiert ist..."

# Garden management screens
GARDEN_NAME_LABEL = "Gartenname: "
HINT_GARDEN_NAME = "Benenne deinen Garten"
GARDEN_TYPE_LABEL = "Typ: "
GARDEN_TYPE_INDOOR = "Innen"
GARDEN_TYPE_OUTDOOR = "Außen"
LIGHT_TYPE_LABEL = "Lichttyp: "
LIGHT_WATTAGE_LABEL = "Leistung: "
HINT_LIGHT_WATTAGE = "Watt"
LIGHT_SCHEDULE_LABEL = "Beleuchtungsplan: "
HINT_LIGHT_HOURS = "Stunden an"
LOCATION_LABEL = "Standort: "

# Light types
LIGHT_LED = "LED"
LIGHT_HPS = "HPS"
LIGHT_CFL = "CFL"

# Climate regions
CLIMATE_NH_TEMPERATE = "Nördl. gemäßigte Zone"
CLIMATE_MEDITERRANEAN = "Mittelmeerraum"
CLIMATE_TROPICAL = "Tropisch"
CLIMATE_SH_TEMPERATE = "Südl. gemäßigte Zone"
CLIMATE_EQUATORIAL = "Äquatorial"

# Location cascading dropdowns (outdoor gardens)
CONTINENT_LABEL = "Kontinent: "
COUNTRY_LABEL = "Land: "
CITY_LABEL = "Stadt: "


LEGEND_TITLES = {
  "plant_height": "Pflanzenhöhe (cm)",
  "num_nodes": "Anzahl Knoten",
  "node_spacing": "Knotenabstand (cm)",
  "main_stem_number": "Anzahl Haupttriebe",
  "air_temp_c": "Lufttemperatur (°C)",
  "rh_percent": "Relative Luftfeuchte (%)",
  "soil_moisture": "Bodenfeuchte",
  "soil_ph": "Boden-pH",
  "vpd_kpa": "VPD (kPa)",
  "ppfd": "PPFD (µmol/m²/s)",
  "volume_l": "Wasservolumen (L)",
  "water_temp_c": "Wassertemperatur (°C)",
  "ph": "Wasser-pH",
  "ppm": "Wasser-PPM",
}

# Export / Import screen
EXPORT_IMPORT_TITLE = "Teile und sichere deinen [color={color}]SCHATZ[/color]"
EXPORT_SELECT_GARDENS = "Gärten auswählen:"
EXPORT_SELECT_ALL = "Alle auswählen"
EXPORT_DESELECT_ALL = "Alle abwählen"
EXPORT_TYPE_LABEL = "Exporttyp:"
EXPORT_SAFE = "Sicher (verschlüsselt)"
EXPORT_OPEN = "Offen (ohne Passwort)"
EXPORT_PASSWORD = "Export-Passwort:"
EXPORT_PASSWORD_CONFIRM = "Passwort bestätigen:"
EXPORT_FILENAME_LABEL = "Dateiname:"
EXPORT_CHOOSE_LOCATION = "Exportspeicherort wählen"
BUTTON_EXPORT = "Exportieren"
BUTTON_IMPORT = "Importieren"
EXPORT_NO_GARDENS_SELECTED = "Bitte wähle mindestens einen Garten zum Exportieren aus."
EXPORT_SUCCESS = "Export abgeschlossen:"
EXPORT_ERROR = "Export fehlgeschlagen:"
IMPORT_CHOOSE_FILE = "Wähle eine .weed-Datei zum Importieren"
IMPORT_PASSWORD_PROMPT = "Diese Datei ist verschlüsselt. Gib das Export-Passwort ein:"
IMPORT_CONFLICT_WARNING = "{n} Garten/Gärten in dieser Datei existieren bereits und werden überschrieben.\nBist du sicher, dass du fortfahren möchtest?"
IMPORT_ERROR_CORRUPT = "Die Datei scheint beschädigt zu sein oder ist keine gültige .weed-Datei."
IMPORT_ERROR_WRONG_PW = "Falsches Passwort oder die Datei ist beschädigt."
IMPORT_SUCCESS = "Import abgeschlossen: {gardens} Garten/Gärten und {events} Ereignisdatei(en) importiert."
SETTINGS_EXPORT_IMPORT = "Daten exportieren / importieren"
SETTINGS_EXPORT_CSV = "Als CSV exportieren"
CSV_EXPORT_TITLE = "Gärten als [color={color}]CSV[/color] exportieren"
CSV_EXPORT_CHOOSE_LOCATION = "Exportspeicherort wählen"
CSV_EXPORT_FILENAME_LABEL = "Dateiname:"
CSV_EXPORT_SUCCESS = "CSV-Export abgeschlossen:"
CSV_EXPORT_ERROR = "CSV-Export fehlgeschlagen:"
CSV_EXPORT_NO_GARDENS = "Bitte wähle mindestens einen Garten zum Exportieren aus."

import sys

def get(key: str) -> str:
    """Return the string for a constant-like key, or the key itself."""
    return getattr(sys.modules[__name__], key, key)
