"""
backup/restore_backup.py
Restore database dari file backup
"""

import shutil
from pathlib import Path
from datetime import datetime

from config import (
    DATABASE_PATH,
    BACKUP_DIR,
)

from logging_config import get_logger


logger = get_logger(__name__)


def restore_database(
    backup_file: str,
):

    try:

        backup_path = Path(
            backup_file
        )

        if not backup_path.exists():

            raise FileNotFoundError(
                "File backup tidak ditemukan"
            )

        # =====================================
        # SAFETY BACKUP
        # =====================================

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        safety_backup = (
            Path(BACKUP_DIR)
            / f"safety_before_restore_{timestamp}.db"
        )

        shutil.copy2(
            DATABASE_PATH,
            safety_backup,
        )

        logger.info(
            f"Safety backup dibuat: {safety_backup}"
        )

        # =====================================
        # RESTORE DATABASE
        # =====================================

        shutil.copy2(
            backup_path,
            DATABASE_PATH,
        )

        logger.info(
            f"Database berhasil direstore dari {backup_file}"
        )

        return {
            "status": "success",
            "restored_from": backup_file,
            "safety_backup": str(
                safety_backup
            ),
        }

    except Exception as exc:

        logger.error(
            f"Gagal restore database: {exc}"
        )

        raise