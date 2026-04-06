"""
system/notification_manager.py
System notification manager untuk toko-ai-agent

Fitur:
- Notifikasi stok minimum
- Notifikasi disk hampir penuh
- Notifikasi backup gagal
- Notifikasi error sistem
- Logging notifikasi
"""

import shutil
from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from database.models import Barang, StokAudit

from config import DATA_DIR

from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

MIN_STOCK_THRESHOLD = 5

MIN_DISK_GB = 1


# =========================================================
# UTIL
# =========================================================

def get_session():
    return SessionLocal()


def notify(message: str):

    try:

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        print()

        print("=== NOTIFICATION ===")

        print(timestamp)

        print(message)

        print()

        logger.warning(message)

    except Exception as exc:

        logger.error(
            f"Gagal menampilkan notifikasi: {exc}"
        )


# =========================================================
# CHECK LOW STOCK
# =========================================================

def check_low_stock() -> List[str]:

    session = get_session()

    alerts = []

    try:

        results = session.execute(
            select(
                Barang.nama,
                StokAudit.stok_akhir,
            )
            .join(
                Barang,
                Barang.id == StokAudit.barang_id,
            )
            .where(
                StokAudit.stok_akhir <= MIN_STOCK_THRESHOLD,
            )
        ).all()

        for row in results:

            message = (
                f"Stok rendah: "
                f"{row.nama} = {row.stok_akhir}"
            )

            alerts.append(message)

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal cek stok rendah: {exc}"
        )

    finally:

        session.close()

    return alerts


# =========================================================
# CHECK DISK SPACE
# =========================================================

def check_disk_space() -> bool:

    try:

        usage = shutil.disk_usage(DATA_DIR)

        free_gb = usage.free / (
            1024 * 1024 * 1024
        )

        if free_gb < MIN_DISK_GB:

            notify(
                f"Disk hampir penuh: {free_gb:.2f} GB tersisa"
            )

            return False

        return True

    except Exception as exc:

        logger.error(
            f"Gagal cek disk: {exc}"
        )

        return False


# =========================================================
# CHECK SYSTEM ALERT
# =========================================================

def run_notifications():

    try:

        print()

        print("Checking system notifications...")

        alerts = check_low_stock()

        if alerts:

            for alert in alerts:

                notify(alert)

        check_disk_space()

        logger.info(
            "Notification check selesai"
        )

    except Exception as exc:

        logger.error(
            f"Notification error: {exc}"
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    run_notifications()