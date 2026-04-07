"""
backup/list_backups.py
Utility untuk membaca daftar file backup
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict

from config import BACKUP_DIR

from logging_config import get_logger


logger = get_logger(__name__)


def list_backup_files() -> List[Dict]:

    try:

        backup_path = Path(
            BACKUP_DIR
        )

        if not backup_path.exists():

            logger.warning(
                "Folder backup tidak ditemukan"
            )

            return []

        files = list(
            backup_path.glob(
                "*.db"
            )
        )

        data = []

        for file in files:

            stat = file.stat()

            created_time = datetime.fromtimestamp(
                stat.st_mtime
            )

            size_mb = (
                stat.st_size
                / (1024 * 1024)
            )

            data.append(
                {
                    "filename": file.name,
                    "path": str(file),
                    "size_mb": round(
                        size_mb,
                        2,
                    ),
                    "created_at": created_time.isoformat(),
                }
            )

        # Urutkan terbaru dulu
        data.sort(
            key=lambda x: x[
                "created_at"
            ],
            reverse=True,
        )

        return data

    except Exception as exc:

        logger.error(
            f"Gagal list backup: {exc}"
        )

        raise