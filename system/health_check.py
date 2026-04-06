"""
system/health_check.py
Health check system untuk toko-ai-agent

Fitur:
- Cek database
- Cek folder penting
- Cek model AI
- Cek disk space
- Laporan status sistem
"""

import shutil
from pathlib import Path
from typing import Dict

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from config import (
    DATABASE_PATH,
    LOG_DIR,
    BACKUP_DIR,
    DATA_DIR,
    MODEL_PATH,
)

from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# UTIL
# =========================================================

def get_session():
    return SessionLocal()


# =========================================================
# CHECK DATABASE
# =========================================================

def check_database() -> bool:

    session = get_session()

    try:

        session.execute(
            text("SELECT 1")
        )

        logger.info("Database OK")

        return True

    except SQLAlchemyError as exc:

        logger.error(
            f"Database error: {exc}"
        )

        return False

    finally:

        session.close()


# =========================================================
# CHECK PATH
# =========================================================

def check_path(path: Path) -> bool:

    try:

        if not path.exists():

            logger.warning(
                f"Tidak ditemukan: {path}"
            )

            return False

        return True

    except Exception as exc:

        logger.error(
            f"Gagal cek path {path}: {exc}"
        )

        return False


# =========================================================
# CHECK DISK SPACE
# =========================================================

def check_disk_space(
    path: Path,
    min_gb: int = 1,
) -> bool:

    try:

        usage = shutil.disk_usage(path)

        free_gb = usage.free / (
            1024 * 1024 * 1024
        )

        if free_gb < min_gb:

            logger.warning(
                f"Disk hampir penuh: {free_gb:.2f} GB"
            )

            return False

        logger.info(
            f"Disk space OK: {free_gb:.2f} GB"
        )

        return True

    except Exception as exc:

        logger.error(
            f"Gagal cek disk: {exc}"
        )

        return False


# =========================================================
# SYSTEM HEALTH
# =========================================================

def run_health_check() -> Dict[str, bool]:

    print()
    print("=== SYSTEM HEALTH CHECK ===")

    results = {}

    try:

        results["database"] = check_database()

        results["data_dir"] = check_path(
            DATA_DIR
        )

        results["backup_dir"] = check_path(
            BACKUP_DIR
        )

        results["log_dir"] = check_path(
            LOG_DIR
        )

        results["model"] = check_path(
            Path(MODEL_PATH)
        )

        results["disk"] = check_disk_space(
            Path(".")
        )

        print()
        print("Status:")

        for key, value in results.items():

            status = (
                "OK"
                if value
                else "FAIL"
            )

            print(
                f"{key:12} : {status}"
            )

        print()

        if all(results.values()):

            print(
                "SYSTEM STATUS: HEALTHY"
            )

        else:

            print(
                "SYSTEM STATUS: WARNING"
            )

        logger.info(
            f"Health check result: {results}"
        )

        return results

    except Exception as exc:

        logger.error(
            f"Health check error: {exc}"
        )

        return results


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    run_health_check()