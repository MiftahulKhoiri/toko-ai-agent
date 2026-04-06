"""
config.py
Konfigurasi utama sistem toko-ai-agent
"""

from pathlib import Path
from datetime import datetime
import os

=========================================================

ROOT DIRECTORY

=========================================================

BASE_DIR = Path(file).resolve().parent

DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backup"
LOG_DIR = BASE_DIR / "logs"
MODEL_DIR = BASE_DIR / "ai" / "model"
DATABASE_DIR = BASE_DIR / "database"

Pastikan folder ada

for folder in [
DATA_DIR,
BACKUP_DIR,
LOG_DIR,
MODEL_DIR,
DATABASE_DIR,
]:
folder.mkdir(parents=True, exist_ok=True)

=========================================================

DATABASE

=========================================================

DATABASE_NAME = "db.sqlite"

DATABASE_PATH = DATABASE_DIR / DATABASE_NAME

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

=========================================================

FILE DATA

=========================================================

STOK_FILE = DATA_DIR / "stok.csv"
TRANSAKSI_FILE = DATA_DIR / "transaksi.csv"
BIAYA_FILE = DATA_DIR / "biaya.csv"

=========================================================

BACKUP

=========================================================

BACKUP_AUTO_DIR = BACKUP_DIR / "auto"
BACKUP_MANUAL_DIR = BACKUP_DIR / "manual"

BACKUP_AUTO_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_MANUAL_DIR.mkdir(parents=True, exist_ok=True)

BACKUP_TIME = "23:00"   # Backup harian jam 23:00

=========================================================

LOGGING

=========================================================

LOG_FILE = LOG_DIR / "system.log"

LOG_LEVEL = "INFO"

=========================================================

AI MODEL

=========================================================

MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"

MODEL_PATH = MODEL_DIR / MODEL_FILE

AI_MAX_TOKENS = 512
AI_TEMPERATURE = 0.2
AI_CONTEXT_LENGTH = 4096

=========================================================

AUDIT SYSTEM

=========================================================

AUDIT_FREQUENCY = "harian"

SATUAN_VALID = [
"kg",
"liter",
"pcs"
]

=========================================================

DATE FORMAT

=========================================================

DATE_FORMAT = "%Y-%m-%d"

TODAY = datetime.now().strftime(DATE_FORMAT)

=========================================================

SYSTEM INFO

=========================================================

APP_NAME = "toko-ai-agent"

VERSION = "1.0"

ENVIRONMENT = os.getenv("ENV", "production")

=========================================================

DEBUG

=========================================================

DEBUG = False

if DEBUG:
print("Config loaded")
print("Database:", DATABASE_PATH)
print("Model:", MODEL_PATH)