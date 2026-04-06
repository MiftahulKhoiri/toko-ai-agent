"""logging_config.py - Konfigurasi logging untuk toko-ai-agent

Fitur:
- File log otomatis
- Rotating log (maks 5 file)
- Format log profesional
- Level log configurable
"""

import logging
import logging.handlers
from pathlib import Path

from config import LOG_DIR, LOG_LEVEL


# =========================================================
# SETUP LOG DIRECTORY
# =========================================================

try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception as exc:
    print(f"[ERROR] Gagal membuat folder log: {exc}")

LOG_FILE = LOG_DIR / "system.log"


# =========================================================
# LOG LEVEL
# =========================================================

LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

LOG_LEVEL_VALUE = LEVEL_MAP.get(LOG_LEVEL.upper(), logging.INFO)


# =========================================================
# FORMAT
# =========================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# =========================================================
# HANDLER
# =========================================================

handler = logging.handlers.RotatingFileHandler(
    filename=str(LOG_FILE),
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding="utf-8",
)

handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))


# =========================================================
# ROOT LOGGER
# =========================================================

root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL_VALUE)

if not root_logger.handlers:
    root_logger.addHandler(handler)


# =========================================================
# GET LOGGER
# =========================================================

def get_logger(name: str) -> logging.Logger:
    """Ambil logger untuk module

    Contoh:
    logger = get_logger(__name__)
    logger.info("Program berjalan")
    """
    try:
        logger = logging.getLogger(name)
        return logger
    except Exception as exc:
        print(f"[ERROR] Gagal membuat logger: {exc}")
        return logging.getLogger()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":
    logger = get_logger("test")
    logger.info("Logging system aktif")
    logger.warning("Ini warning")
    logger.error("Ini error")