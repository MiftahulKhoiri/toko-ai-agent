"""startup/startup_tasks.py - Auto startup tasks untuk toko-ai-agent

Fungsi:
- Auto lock hari kemarin
- Validasi database
- Cek model AI
- Start backup scheduler
- Logging startup
"""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal

from core.lock_manager import auto_lock_yesterday
from backup.auto_backup import start_scheduler
from config import MODEL_PATH
from logging_config import get_logger

logger = get_logger(__name__)


# =========================================================
# UTIL
# =========================================================

def get_session():
    return SessionLocal()


# =========================================================
# VALIDASI DATABASE
# =========================================================

def validate_database() -> bool:
    """Cek apakah database bisa diakses"""
    session = get_session()
    try:
        session.execute(text("SELECT 1"))
        logger.info("Database OK")
        return True
    except SQLAlchemyError as exc:
        logger.error(f"Database error: {exc}")
        return False
    finally:
        session.close()


# =========================================================
# CEK MODEL AI
# =========================================================

def check_model() -> bool:
    """Cek apakah file model ada"""
    try:
        if not Path(MODEL_PATH).exists():
            logger.warning(f"Model tidak ditemukan: {MODEL_PATH}")
            return False
        logger.info("Model AI ditemukan")
        return True
    except Exception as exc:
        logger.error(f"Gagal cek model: {exc}")
        return False


# =========================================================
# START BACKUP SCHEDULER
# =========================================================

def start_backup_scheduler():
    try:
        logger.info("Memulai scheduler backup")
        start_scheduler()
    except Exception as exc:
        logger.error(f"Scheduler error: {exc}")


# =========================================================
# AUTO LOCK
# =========================================================

def run_auto_lock():
    try:
        auto_lock_yesterday()
        logger.info("Auto lock selesai")
    except Exception as exc:
        logger.error(f"Auto lock gagal: {exc}")


# =========================================================
# MAIN STARTUP
# =========================================================

def run_startup_tasks():
    """Jalankan semua startup tasks"""
    logger.info("=== STARTUP SYSTEM ===")
    try:
        # 1. Validasi database
        if not validate_database():
            logger.error("Database tidak siap")
            return
        # 2. Auto lock kemarin
        run_auto_lock()
        # 3. Cek model AI
        check_model()
        logger.info("Startup tasks selesai")
    except Exception as exc:
        logger.error(f"Startup error: {exc}")


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":
    run_startup_tasks()