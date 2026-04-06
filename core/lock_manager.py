"""core/lock_manager.py - Manajemen lock data harian untuk toko-ai-agent

Fungsi:
- Lock tanggal
- Cek apakah tanggal terkunci
- Unlock tanggal (admin)
- Otomatis lock hari sebelumnya
"""

from datetime import datetime, date, timedelta
from typing import Optional

from sqlalchemy import Column, Integer, Date, DateTime, select
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal, Base
from config import TODAY


# =========================================================
# MODEL LOCK DATE
# =========================================================
class LockDate(Base):
    __tablename__ = "lock_date"

    id = Column(Integer, primary_key=True)
    tanggal = Column(Date, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# =========================================================
# UTIL
# =========================================================
def get_session():
    return SessionLocal()


def get_today() -> date:
    return datetime.strptime(TODAY, "%Y-%m-%d").date()


# =========================================================
# CEK LOCK
# =========================================================
def is_locked(tanggal: date) -> bool:
    """Cek apakah tanggal sudah terkunci"""
    session = get_session()
    try:
        result = session.execute(
            select(LockDate).where(LockDate.tanggal == tanggal)
        ).scalar_one_or_none()
        return result is not None
    except SQLAlchemyError as exc:
        print(f"[ERROR] Gagal cek lock: {exc}")
        return False
    finally:
        session.close()


# =========================================================
# LOCK TANGGAL
# =========================================================
def lock_date(tanggal: Optional[date] = None) -> None:
    """Lock tanggal tertentu"""
    session = get_session()
    try:
        if tanggal is None:
            tanggal = get_today()
        if is_locked(tanggal):
            print(f"Tanggal sudah terkunci: {tanggal}")
            return
        lock = LockDate(tanggal=tanggal)
        session.add(lock)
        session.commit()
        print(f"Tanggal berhasil dikunci: {tanggal}")
    except SQLAlchemyError as exc:
        session.rollback()
        print(f"[ERROR] Gagal lock tanggal: {exc}")
    finally:
        session.close()


# =========================================================
# UNLOCK
# =========================================================
def unlock_date(tanggal: date) -> None:
    """Unlock tanggal (admin)"""
    session = get_session()
    try:
        result = session.execute(
            select(LockDate).where(LockDate.tanggal == tanggal)
        ).scalar_one_or_none()
        if not result:
            print("Tanggal tidak terkunci")
            return
        session.delete(result)
        session.commit()
        print(f"Tanggal berhasil dibuka: {tanggal}")
    except SQLAlchemyError as exc:
        session.rollback()
        print(f"[ERROR] Gagal unlock tanggal: {exc}")
    finally:
        session.close()


# =========================================================
# AUTO LOCK KEMARIN
# =========================================================
def auto_lock_yesterday() -> None:
    """Otomatis lock hari kemarin"""
    try:
        today = get_today()
        yesterday = today - timedelta(days=1)
        if is_locked(yesterday):
            return
        lock_date(yesterday)
        print(f"Auto lock tanggal: {yesterday}")
    except Exception as exc:
        print(f"[ERROR] Auto lock gagal: {exc}")


# =========================================================
# VALIDASI INPUT DATA
# =========================================================
def validate_input_date() -> bool:
    """Cek apakah hari ini terkunci"""
    try:
        today = get_today()
        if is_locked(today):
            print("Hari ini sudah terkunci")
            return False
        return True
    except Exception as exc:
        print(f"[ERROR] Validasi lock gagal: {exc}")
        return False


# =========================================================
# TEST
# =========================================================
if __name__ == "__main__":
    print("TEST LOCK SYSTEM")
    auto_lock_yesterday()
    if validate_input_date():
        print("Hari ini boleh input")
    else:
        print("Hari ini terkunci")