import os
from pathlib import Path
from typing import List, Set

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / 'data'
STATIC_DIR = BASE_DIR / 'static'
MODELS_DIR = BASE_DIR / 'models_cache'
UPLOADS_DIR = BASE_DIR / 'uploads'

DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# Environment & Server Config
APP_ENV = os.getenv('APP_ENV', 'development').lower()
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = int(os.getenv('APP_PORT', '8000'))
APP_RELOAD = os.getenv('APP_RELOAD', 'true').lower() in ('true', '1', 'yes') if APP_ENV == 'development' else False

# Security & CORS
_raw_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000')
if APP_ENV == 'development' and _raw_origins.strip() == '*':
    ALLOWED_ORIGINS = ['*']
else:
    ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(',') if o.strip()]

MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '10'))
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))

# Database
DB_PATH = BASE_DIR / 'krishi_saathi.db'
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH}')

# Device Selection (safe detection without heavy operations)
def get_model_device() -> str:
    env_device = os.getenv('MODEL_DEVICE')
    if env_device:
        return env_device
    try:
        import torch
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    except Exception:
        return 'cpu'

MODEL_DEVICE = get_model_device()

# Weather Settings & Abstraction
WEATHER_PROVIDER = os.getenv('WEATHER_PROVIDER', 'open-meteo').lower()
WEATHER_CACHE_TTL_SECONDS = int(os.getenv('WEATHER_CACHE_TTL_SECONDS', '1800'))  # 30 mins
OPEN_METEO_URL = os.getenv('OPEN_METEO_URL', 'https://api.open-meteo.com/v1/forecast')

DEFAULT_LATITUDE = 26.8467  # Uttar Pradesh (Central Indo-Gangetic Plains)
DEFAULT_LONGITUDE = 80.9462
DEFAULT_DISTRICT = 'Lucknow'
DEFAULT_STATE = 'Uttar Pradesh'

# Thresholds & Safety
DISEASE_CONFIDENCE_THRESHOLD = 0.60
MIN_NUTRIENT_CONFIDENCE = 0.70

# Banned or Highly Hazardous Agro-Chemicals in India (CIBRC Schedule)
BANNED_CHEMICALS: Set[str] = {
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
