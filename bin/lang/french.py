APP_TITLE = "Magic Herb Tracker"

# Common buttons
BUTTON_SAVE = "Enregistrer"
BUTTON_CONFIRM = "Confirmer"
BUTTON_CANCEL = "Annuler"
BUTTON_ADD = "Ajouter"
BUTTON_DELETE = "Supprimer"
BUTTON_PLUS = "+"
BUTTON_MINUS = "-"
BUTTON_EDIT = "modifier"

# Generic labels
LABEL_NAME = "Nom"
LABEL_TYPE = "Type"
LABEL_QUANTITY = "Quantité"

# Messages
MSG_CONFIRM_DELETE = "Êtes-vous sûr de vouloir supprimer cet élément ?"
MSG_CONFIRM_DELETE_PLANT = "Êtes-vous sûr de vouloir supprimer la plante sélectionnée ?"
MSG_CONFIRM_CANCEL_CHANGES = "Êtes-vous sûr de vouloir annuler et perdre toutes les modifications non enregistrées ?"

# Confirmation prompt title and variants
ARE_YOU_SURE_TITLE = "Êtes-vous sûr ?"
MSG_CONFIRM_CANCEL = "Abandonner les modifications ?"
MSG_CONFIRM_EXIT = "Quitter le jardin ?"

# Relative / time labels
TODAY = "Aujourd'hui"
YESTERDAY = "Hier"
DAYS_AGO = "il y a {n} jours"
WEEK_AGO_ONE = "il y a {n} semaine"
WEEK_AGO_PLURAL = "il y a {n} semaines"
MONTH_AGO_ONE = "il y a {n} mois"
MONTH_AGO_PLURAL = "il y a {n} mois"
YEAR_AGO_ONE = "il y a {n} an"
YEAR_AGO_PLURAL = "il y a {n} ans"

# Generic labels
BACK = "Retour"
DAY_LABEL = "Jour"

# Plant details / health
HEALTH_HEALTHY = "En bonne santé"
HEALTH_MINOR = "Problèmes mineurs"
HEALTH_MODERATE = "Problèmes modérés"
HEALTH_SEVERE = "Problèmes graves"
STATUS_FLOWERING = "En floraison !"
STATUS_HARVESTED = "Récolté !"

# Event toggle labels
TOGGLE_TOP = "Étêter"
TOGGLE_PRUNE = "Tailler"
TOGGLE_FLIP = "Basculer"
FLIP_DONE = "Basculé"

# Event / plant field titles
EVENT_FIELD_TITLES = {
  "HEIGHT": "Hauteur",
  "NODES": "Nœuds",
  "SPACING": "Espacement",
  "MAIN_STEMS": "Tiges principales",
  "COLOR": "Couleur",
  "MORPHOLOGY": "Morphologie",
  "AIR_TEMP": "Temp. air",
  "HUMIDITY": "Humidité",
  "VPD": "VPD",
  "SOIL_PH": "pH du sol",
  "SOIL": "Sol",
  "PPFD": "PPFD",
  "LIGHT": "Lumière",
}

WATER_FIELD_TITLES = {
  "VOLUME": "Volume",
  "TEMP": "Temp.",
  "PH": "pH",
  "PPM": "PPM",
}

# Common small labels
NAME_SEPARATOR = " | "

# Last event templates
LAST_WATER_TEMPLATE = "Dernier arrosage : {vol} L, pH {ph}, {ppm} ppm @ {ts}"
LAST_EVENT_TEMPLATE = "Dernier événement : {type} @ {ts}"

# Screen titles (used in various views)
SCREEN_TITLE_GARDEN = "Mon [color={color}]JARDIN[/color] magique"
SCREEN_TITLE_DETAILS = "Regardez-moi cette [color={color}]BEAUTÉ[/color]"
SCREEN_TITLE_GRAPH = "Regardez-moi cette [color={color}]BEAUTÉ[/color]"
SCREEN_TITLE_ENV = "Où vais-je le [color={color}]CULTIVER[/color] ?"
SCREEN_TITLE_SOW_SEED = "Parlez-nous de votre [color={color}]graine[/color]"
SCREEN_TITLE_ADD_GARDEN = "Créer un nouveau [color={color}]JARDIN[/color]"
SCREEN_TITLE_SELECT_GARDEN = "Sélectionnez un [color={color}]JARDIN[/color]"
SCREEN_SETTINGS_TITLE = "Ajustons quelques [color={color}]PARAMÈTRES[/color]"
SCREEN_TITLE_PASSWORD = "Entrez votre [color={color}]MOT DE PASSE[/color]"


# Timeline tab labels
TAB_PLANT = "Plante"
TAB_ENVIRONMENT = "Environnement"
TAB_WATER = "Eau"
TAB_FOOD = "Nourriture"

# Set environment
SET_ENV_WARNING_TITLE = "Arrosage et fertilisation :"
SET_ENV_WARNING_BODY = (
    "Consultez l'emballage ou le sélectionneur pour les profils estimés.\n"
    "Les valeurs s'ajusteront automatiquement au cours de la vie de vos plantes.\n"
    "Si vous n'êtes pas sûr, laissez les deux curseurs en position par défaut."
)

# Sow seed / fields
SEEDBANK_LABEL = "Banque de graines : "
HINT_SELECT_NAME = "Choisissez un nom pour votre plante"
STRAIN_LABEL = "Variété : "
HINT_WHATS_ON_BOX = "Qu'est-ce qui est écrit sur la boîte ?"
INFO_LABEL = "Info : "
HINT_SAY_SOMETHING = "Dites quelque chose sur votre plante"
HERITAGE_LABEL = "Héritage : "
GENES_SATIVA = "Sativa"
GENES_INDICA = "Indica"
GENES_HYBRID = "Hybride"
TYPE_LABEL = "Type : "
TYPE_AUTOMATIC = "Automatique"
TYPE_PHOTOPERIODIC = "Photopériodique"
FLOWERING_PERIOD_LABEL = "Période de floraison : "
HINT_DAYS_TO_FLOWER = "Jours avant floraison"

# Buttons
NEXT = "Suivant"

# Feeding / dropdown field labels (used in feeding rows)
FEED_VEG = "Croissance"
FEED_ROOT = "Racine"
FEED_SOIL = "Sol"
FEED_VIT = "Vit"

FEED_FLOWER = "Floraison"
FEED_TOPS = "Têtes"
FEED_CALMAG = "CalMag"
FEED_FUNGI = "Champignons"

# Notes label
LABEL_NOTES = "Notes"
NUTRIENTS = "Nutriments"
VIEW_TIMELINE = "Voir\nChronologie"

# Generic confirmations
YES = "Oui"
NO = "Non"

# Fertilizer / medium strings
FERTILIZED_LABEL = "Fertilisé : "
FERTILIZED = "Fertilisé"
BARE = "Nu"
YOUR_FERTILIZER_LABEL = "Votre engrais : "
FERTILIZER_ORGANIC = "Organique"
FERTILIZER_MINERAL = "Minéral"

# Environment defaults
EVERY_3_DAYS = "Tous les 3 jours"
EVERY_2ND_WATERING = "Un arrosage sur 2"
POT_LABEL_DEFAULT = "9L"

# Set environment labels
WATERING_LABEL = "Arrosage"
FEEDING_LABEL = "Fertilisation"
POT_SIZE_LABEL = "Taille du pot"
MEDIUM_LABEL = "Substrat"
MEDIUM_SOIL = "Terre"
MEDIUM_COCO = "Coco"
MEDIUM_MINERAL = "Minéral"
MEDIUM_HYDRO = "Hydro"

# Additional frequency templates
EVERY_WATERING = "Chaque arrosage"
EVERY_3RD_WATERING = "Un arrosage sur 3"
EVERY_N_DAYS = "Tous les {n} jours"

# Pot size format
POT_SIZE_FMT = "{n}L"

# Numeric/hint defaults
HINT_NUM_DEFAULT = "0.0"
HINT_AIR_TEMP_DEFAULT = "24"
HINT_RH_DEFAULT = "55"

# Misc small tokens
DASH = "–"

# Graph/button small labels
GRAPH_BTN_ABSOLUTE = "Absolu"
ML_PER_LITER = "ml par litre"
ML = "ml"

# Settings screen
SETTINGS_CURRENT_PASSWORD = "Mot de passe actuel : "
SETTINGS_PASSWORD = "Nouveau mot de passe : "
HINT_CURRENT_PASSWORD = "Entrez le mot de passe actuel"
HINT_NO_PASSWORD_SET = "Aucun mot de passe défini"
SETTINGS_PASSWORD_CONFIRM = "Confirmer le mot de passe : "
SETTINGS_DB_PATH = "Chemin de la base de données : "
SETTINGS_SHADER_TOGGLE = "Arrière-plan animé : "
HINT_ENTER_PASSWORD = "Entrez le mot de passe"
HINT_CONFIRM_PASSWORD = "Confirmez le mot de passe"
HINT_DB_PATH = "Chemin vers le dossier de la base de données"
SETTINGS_SHADER_ON = "Activé"
SETTINGS_SHADER_OFF = "Désactivé"
SETTINGS_THEME = "Thème : "
SETTINGS_SHADER_SELECT = "Style de shader : "
SETTINGS_SHADER_RELOAD = "Recharger"
SETTINGS_PIXEL_SCALE = "Échelle de pixels : "
SETTINGS_REMOVE_PASSWORD = "Supprimer le mot de passe"
WARN_SET_PASSWORD = "ATTENTION : Définir un mot de passe chiffrera l'intégralité de la base de données.\nSi vous oubliez ou perdez le mot de passe, vous ne pourrez pas récupérer vos données.\nÊtes-vous sûr de vouloir continuer ?"
WARN_REMOVE_PASSWORD = "Êtes-vous sûr de vouloir supprimer la protection par mot de passe et déchiffrer la base de données ?\nVos données seront stockées en JSON non chiffré après cette opération."
WARN_MOVE_DB_PATH = "Cela déplacera tous les fichiers de jardins et de plantes vers le nouvel emplacement.\nL'application redémarrera automatiquement après le déplacement.\nÊtes-vous sûr de vouloir continuer ?"
SETTINGS_SELECT_FOLDER = "Sélectionner"
SETTINGS_LANGUAGE = "Langue : "
SETTINGS_LANGUAGE_RESTART = "(redémarrage nécessaire)"

# Sort / filter bar
SORT_BY = "Trier par :"
SORT_NAME = "Nom"
SORT_BREEDER = "Sélectionneur"
SORT_DATE_PLANTED = "Date de plantation"
SORT_DATE_CREATED = "Date de création"
SORT_DAYS_TO_HARVEST = "Jours avant récolte"
SORT_DAYS_TO_WATER = "Jours avant arrosage"
SORT_MEDIUM = "Substrat"
SORT_PLANT_COUNT = "Plantes"
SORT_NEXT_EVENT = "Prochain événement"
SORT_ASCENDING = "Croissant"
SORT_DESCENDING = "Décroissant"
FILTER_ACTIVE_ONLY = "Afficher uniquement les actifs"
SEARCH_HINT = "Rechercher..."

# Garden list legend headers
LEGEND_GENES = "Gènes"
LEGEND_PLANT = "Plante"
LEGEND_MEDIUM = "Substrat"
LEGEND_LAST_WATER = "Dernier arrosage"
LEGEND_NEXT_WATER = "Prochain arrosage"
LEGEND_FLOWER = "Floraison"
LEGEND_HARVEST = "Récolte"
LEGEND_GARDEN_NAME = "Jardin"
LEGEND_GARDEN_TYPE = "Type"
LEGEND_PLANT_COUNT = "Plantes"

# Garden / header buttons
OPTIONS = "Options"
EXIT_APP = "Quitter\nl'appli"
EXIT_GARDEN = "Quitter le\njardin"
ENTER_GARDEN = "Entrer dans le jardin"
ADD_PLANT = "Ajouter une plante"
ADD_GARDEN = "Ajouter un jardin"
SELECT_GARDEN = "Choisir un jardin"
VIEW_GARDENS = "Voir les\njardins"
DELETE_GARDEN = "Supprimer le jardin"
MSG_CONFIRM_DELETE_GARDEN = "Êtes-vous sûr de vouloir supprimer le jardin sélectionné et toutes ses plantes ?"
VIEW_SELECTED_PLANT = "Voir la plante sélectionnée"
DELETE_SELECTED_PLANT = "Supprimer la plante sélectionnée"

# Password check screen
PW_TOO_MANY_ATTEMPTS = "Trop de tentatives. Patientez {n}s."
PW_WRONG_PASSWORD = "Mauvais mot de passe. Patientez {n}s avant de réessayer."
PW_BUTTON_UNLOCK = "Déverrouiller"

# Add event
HINT_EVENT_NOTES = "Racontez ce qui s'est passé aujourd'hui..."

# Garden management screens
GARDEN_NAME_LABEL = "Nom du jardin : "
HINT_GARDEN_NAME = "Nommez votre jardin"
GARDEN_TYPE_LABEL = "Type : "
GARDEN_TYPE_INDOOR = "Intérieur"
GARDEN_TYPE_OUTDOOR = "Extérieur"
LIGHT_TYPE_LABEL = "Type d'éclairage : "
LIGHT_WATTAGE_LABEL = "Puissance : "
HINT_LIGHT_WATTAGE = "Watts"
LIGHT_SCHEDULE_LABEL = "Programme d'éclairage : "
HINT_LIGHT_HOURS = "Heures allumées"
LOCATION_LABEL = "Emplacement : "

# Light types
LIGHT_LED = "LED"
LIGHT_HPS = "HPS"
LIGHT_CFL = "CFL"

# Climate regions
CLIMATE_NH_TEMPERATE = "Hémisphère Nord Tempéré"
CLIMATE_MEDITERRANEAN = "Méditerranéen"
CLIMATE_TROPICAL = "Tropical"
CLIMATE_SH_TEMPERATE = "Hémisphère Sud Tempéré"
CLIMATE_EQUATORIAL = "Équatorial"

# Location cascading dropdowns (outdoor gardens)
CONTINENT_LABEL = "Continent : "
COUNTRY_LABEL = "Pays : "
CITY_LABEL = "Ville : "


LEGEND_TITLES = {
  "plant_height": "Hauteur de la plante (cm)",
  "num_nodes": "Nombre de nœuds",
  "node_spacing": "Espacement des nœuds (cm)",
  "main_stem_number": "Nombre de tiges principales",
  "air_temp_c": "Température de l'air (°C)",
  "rh_percent": "Humidité relative (%)",
  "soil_moisture": "Niveau d'humidité du sol",
  "soil_ph": "pH du sol",
  "vpd_kpa": "VPD (kPa)",
  "ppfd": "PPFD (µmol/m²/s)",
  "volume_l": "Volume d'eau (L)",
  "water_temp_c": "Température de l'eau (°C)",
  "ph": "pH de l'eau",
  "ppm": "PPM de l'eau",
}

# Export / Import screen
EXPORT_IMPORT_TITLE = "Partagez et sauvegardez votre [color={color}]TRÉSOR[/color]"
EXPORT_SELECT_GARDENS = "Sélectionnez les jardins :"
EXPORT_SELECT_ALL = "Tout sélectionner"
EXPORT_DESELECT_ALL = "Tout désélectionner"
EXPORT_TYPE_LABEL = "Type d'export :"
EXPORT_SAFE = "Sécurisé (chiffré)"
EXPORT_OPEN = "Ouvert (sans mot de passe)"
EXPORT_PASSWORD = "Mot de passe d'export :"
EXPORT_PASSWORD_CONFIRM = "Confirmer le mot de passe :"
EXPORT_FILENAME_LABEL = "Nom du fichier :"
EXPORT_CHOOSE_LOCATION = "Choisir l'emplacement d'export"
BUTTON_EXPORT = "Exporter"
BUTTON_IMPORT = "Importer"
EXPORT_NO_GARDENS_SELECTED = "Veuillez sélectionner au moins un jardin à exporter."
EXPORT_SUCCESS = "Export terminé :"
EXPORT_ERROR = "Échec de l'export :"
IMPORT_CHOOSE_FILE = "Choisir un fichier .weed à importer"
IMPORT_PASSWORD_PROMPT = "Ce fichier est chiffré. Entrez le mot de passe d'export :"
IMPORT_CONFLICT_WARNING = "{n} jardin(s) de ce fichier existent déjà et seront écrasés.\nÊtes-vous sûr de vouloir continuer ?"
IMPORT_ERROR_CORRUPT = "Le fichier semble corrompu ou n'est pas un fichier .weed valide."
IMPORT_ERROR_WRONG_PW = "Mot de passe incorrect ou fichier corrompu."
IMPORT_SUCCESS = "Import terminé : {gardens} jardin(s) et {events} fichier(s) d'événements importés."
SETTINGS_EXPORT_IMPORT = "Exporter / Importer les données"
SETTINGS_EXPORT_CSV = "Exporter en CSV"
CSV_EXPORT_TITLE = "Exporter les jardins en [color={color}]CSV[/color]"
CSV_EXPORT_CHOOSE_LOCATION = "Choisir l'emplacement d'export"
CSV_EXPORT_FILENAME_LABEL = "Nom du fichier :"
CSV_EXPORT_SUCCESS = "Export CSV terminé :"
CSV_EXPORT_ERROR = "Échec de l'export CSV :"
CSV_EXPORT_NO_GARDENS = "Veuillez sélectionner au moins un jardin à exporter."

# Photos
PHOTOS_TITLE = "Photos"
PHOTO_ADD = "Ajouter une photo"
PHOTO_VIEW = "Voir la photo"
PHOTO_DELETE = "Supprimer la photo"
PHOTO_VIEW_GALLERY = "Voir\nGalerie"
PHOTO_SHOW_GALLERY = "Afficher\nGalerie"
PHOTO_NONE = "Aucune photo"
MSG_CONFIRM_DELETE_PHOTO = "Êtes-vous sûr de vouloir supprimer cette photo ?"
PHOTO_GALLERY_TITLE = "Votre [color={color}]GALERIE[/color]"

import sys

def get(key: str) -> str:
    """Return the string for a constant-like key, or the key itself."""
    return getattr(sys.modules[__name__], key, key)
