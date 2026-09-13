import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
STATIC_DIR = BASE_DIR / 'static'
MODELS_DIR = BASE_DIR / 'models_cache'

DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Database
DB_PATH = BASE_DIR / 'krishi_saathi.db'

# Weather Settings
DEFAULT_LATITUDE = 26.8467  # Uttar Pradesh (Central Indo-Gangetic Plains)
DEFAULT_LONGITUDE = 80.9462
DEFAULT_DISTRICT = 'Lucknow'
DEFAULT_STATE = 'Uttar Pradesh'
OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'

# Thresholds & Safety
DISEASE_CONFIDENCE_THRESHOLD = 0.60
MIN_NUTRIENT_CONFIDENCE = 0.70

# Banned or Highly Hazardous Agro-Chemicals in India (for safety filter)
BANNED_CHEMICALS = {
    'endosulfan', 'aldrin', 'dieldrin', 'chlordane', 'heptachlor',
    'ddt', 'lindane', 'paraquat dichloride', 'monocrotophos', 'methyl parathion',
    'phorate', 'phosphamidon', 'diazinon', 'captan'
}

# Agro-Climatic Zones of India
AGRO_CLIMATIC_ZONES = {
    'Western Himalayan': ['Jammu and Kashmir', 'Himachal Pradesh', 'Uttarakhand'],
    'Eastern Himalayan': ['Assam', 'Sikkim', 'Arunachal Pradesh', 'Nagaland', 'Manipur', 'Mizoram', 'Tripura', 'Meghalaya'],
    'Lower Gangetic Plain': ['West Bengal'],
    'Middle Gangetic Plain': ['Uttar Pradesh', 'Bihar'],
    'Upper Gangetic Plain': ['Uttar Pradesh', 'Delhi', 'Haryana'],
    'Trans-Gangetic Plain': ['Punjab', 'Haryana', 'Rajasthan'],
    'Eastern Plateau and Hills': ['Jharkhand', 'Odisha', 'Chhattisgarh'],
    'Central Plateau and Hills': ['Madhya Pradesh', 'Rajasthan', 'Uttar Pradesh'],
    'Western Plateau and Hills': ['Maharashtra', 'Madhya Pradesh'],
    'Southern Plateau and Hills': ['Andhra Pradesh', 'Karnataka', 'Tamil Nadu', 'Telangana'],
    'East Coast Plains and Hills': ['Tamil Nadu', 'Andhra Pradesh', 'Odisha'],
    'West Coast Plains and Ghats': ['Kerala', 'Goa', 'Karnataka', 'Maharashtra'],
    'Gujarat Plains and Hills': ['Gujarat'],
    'Western Dry Region': ['Rajasthan'],
    'Islands': ['Andaman and Nicobar', 'Lakshadweep']
}
