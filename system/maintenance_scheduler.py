"""
system/maintenance_scheduler.py
Scheduled maintenance system untuk toko-ai-agent

Fitur:
- Backup harian
- Integrity check
- Auto repair
- Cleanup log lama
- Scheduler stabil
"""

import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path

from backup.auto_backup import backup_all
from system.integrity_checker import run_integrity_check
from system.auto_repair import run_auto_repair

from config import LOG_DIR

from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

DAILY_BACKUP_TIME = "23:00"
INTEGRITY_CHECK_TIME = "02:00"
AUTO_REPAIR_TIME = "02:30"

WEEKLY_CLEANUP_DAY = "sunday"
WEEKLY_CLEANUP_TIME = "03:00"

LOG_RETENTION_DAYS = 30


# =========================================================
# CLEANUP LOG
# =========================================================

def cleanup_old_logs():

    try:

        print("Cleanup log lama...")

        cutoff_date = datetime.now() - timedelta(
            days=LOG_RETENTION_DAYS
        )

        for file in Path(LOG_DIR).glob("*.log"):

            modified_time = datetime.fromtimestamp(
                file.stat().st_mtime
            )

            if modified_time < cutoff_date:

                file.unlink()

                logger.info(
                    f"Log dihapus: {file}"
                )

        print("Cleanup selesai")

    except Exception as exc:

        logger.error(
            f"Gagal cleanup log: {exc}"
        )


# =========================================================
# TASKS
# =========================================================

def daily_backup_task():

    try:

        print("Running daily backup...")

        backup_all()

        logger.info(
            "Daily backup selesai"
        )

    except Exception as exc:

        logger.error(
            f"Daily backup error: {exc}"
        )


def integrity_check_task():

    try:

        print("Running integrity check...")

        run_integrity_check()

        logger.info(
            "Integrity check selesai"
        )

    except Exception as exc:

        logger.error(
            f"Integrity check error: {exc}"
        )


def auto_repair_task():

    try:

        print("Running auto repair...")

        run_auto_repair()

        logger.info(
            "Auto repair selesai"
        )

    except Exception as exc:

        logger.error(
            f"Auto repair error: {exc}"
        )


# =========================================================
# SCHEDULER SETUP
# =========================================================

def setup_scheduler():

    try:

        print("Setup maintenance scheduler...")

        # Backup harian

        schedule.every().day.at(
            DAILY_BACKUP_TIME
        ).do(
            daily_backup_task
        )

        # Integrity check

        schedule.every().day.at(
            INTEGRITY_CHECK_TIME
        ).do(
            integrity_check_task
        )

        # Auto repair

        schedule.every().day.at(
            AUTO_REPAIR_TIME
        ).do(
            auto_repair_task
        )

        # Weekly cleanup

        getattr(
            schedule.every(),
            WEEKLY_CLEANUP_DAY
        ).at(
            WEEKLY_CLEANUP_TIME
        ).do(
            cleanup_old_logs
        )

        logger.info(
            "Scheduler setup selesai"
        )

    except Exception as exc:

        logger.error(
            f"Gagal setup scheduler: {exc}"
        )


# =========================================================
# RUN SCHEDULER
# =========================================================

def run_scheduler():

    try:

        setup_scheduler()

        print("Maintenance scheduler berjalan")

        while True:

            schedule.run_pending()

            time.sleep(60)

    except KeyboardInterrupt:

        print("Scheduler dihentikan")

    except Exception as exc:

        logger.error(
            f"Scheduler error: {exc}"
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    run_scheduler()