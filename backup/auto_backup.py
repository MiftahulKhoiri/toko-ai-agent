"""backup/auto_backup.py - Modul backup otomatis untuk toko-ai-agent

Fungsi:
- Backup database SQLite
- Backup file data CSV
- Backup terjadwal
- Logging hasil backup
"""

import shutil
import schedule
import time

from datetime import datetime
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from config import (
    DATABASE_PATH,
    BACKUP_AUTO_DIR,
    BACKUP_TIME,
    STOK_FILE,
    TRANSAKSI_FILE,
    BIAYA_FILE,
    LOG_FILE,
)

from database.db import SessionLocal
from database.models import BackupLog


# =========================================================
# UTIL
# =========================================================

def get_session():
    """Membuat session database"""
    return SessionLocal()


def get_timestamp() -> str:
    """Generate timestamp untuk nama file"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def log_backup(status: str, file_name: str, catatan: str = "") -> None:
    """Simpan log backup ke database"""
    session = get_session()
    try:
        log = BackupLog(
            file_backup=file_name,
            status=status,
            catatan=catatan,
        )
        session.add(log)
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        print(f"[ERROR] Gagal menyimpan log backup: {exc}")
    finally:
        session.close()


# =========================================================
# BACKUP FILE
# =========================================================

def backup_file(source: Path, destination: Path) -> None:
    """Backup satu file"""
    try:
        if not source.exists():
            print(f"[WARNING] File tidak ditemukan: {source}")
            return
        shutil.copy2(source, destination)
        print(f"[OK] Backup: {destination.name}")
    except Exception as exc:
        print(f"[ERROR] Gagal backup file {source}: {exc}")
        raise


# =========================================================
# BACKUP UTAMA
# =========================================================

def backup_all() -> None:
    """Backup semua data sistem"""
    print("Memulai proses backup...")
    timestamp = get_timestamp()
    try:
        # Pastikan folder backup ada
        BACKUP_AUTO_DIR.mkdir(parents=True, exist_ok=True)

        # Backup database
        db_backup_name = f"db_backup_{timestamp}.sqlite"
        db_backup_path = BACKUP_AUTO_DIR / db_backup_name
        backup_file(DATABASE_PATH, db_backup_path)

        # Backup file data
        files_to_backup = [
            STOK_FILE,
            TRANSAKSI_FILE,
            BIAYA_FILE,
        ]
        for file in files_to_backup:
            backup_name = f"{file.stem}_{timestamp}{file.suffix}"
            backup_path = BACKUP_AUTO_DIR / backup_name
            backup_file(file, backup_path)

        log_backup(
            status="SUCCESS",
            file_name=db_backup_name,
            catatan="Backup otomatis berhasil",
        )
        print("Backup selesai")
    except Exception as exc:
        log_backup(
            status="FAILED",
            file_name="backup_error",
            catatan=str(exc),
        )
        print(f"[ERROR] Backup gagal: {exc}")


# =========================================================
# SCHEDULER
# =========================================================

def start_scheduler() -> None:
    """Jalankan scheduler backup otomatis"""
    try:
        schedule.every().day.at(BACKUP_TIME).do(backup_all)
        print(f"Scheduler aktif — backup setiap {BACKUP_TIME}")
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Scheduler dihentikan user")
    except Exception as exc:
        print(f"[ERROR] Scheduler error: {exc}")


# =========================================================
# TEST MANUAL
# =========================================================

if __name__ == "__main__":
    print("TEST BACKUP")
    # Backup sekali
    backup_all()
    # Atau jalankan scheduler
    # start_scheduler()