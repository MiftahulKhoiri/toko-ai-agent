"""
backup/manual_backup.py
Backup database manual
"""

import shutil
from datetime import datetime
from pathlib import Path

from config import (
    DATABASE_PATH,
    BACKUP_DIR,
)

from logging_config import get_logger


logger = get_logger(__name__)


def create_backup():

    try:

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_file = (
            Path(BACKUP_DIR)
            / f"backup_{timestamp}.db"
        )

        shutil.copy2(
            DATABASE_PATH,
            backup_file,
        )

        logger.info(
            f"Backup dibuat: {backup_file}"
        )

        return str(backup_file)

    except Exception as exc:

        logger.error(
            f"Gagal backup: {exc}"
        )

        raise