"""
core/audit_log.py
Audit log user action untuk toko-ai-agent

Fungsi:
- Mencatat aktivitas user
- Logging ke database
- Status SUCCESS / FAILED
- Digunakan oleh semua modul
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal, Base
from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# MODEL
# =========================================================

class AuditLog(Base):

    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)

    username = Column(
        String,
        nullable=False,
    )

    action = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
    )

    message = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
    )


# =========================================================
# UTIL
# =========================================================

def get_session():
    return SessionLocal()


# =========================================================
# LOG ACTION
# =========================================================

def log_action(
    username: str,
    action: str,
    status: str,
    message: Optional[str] = None,
) -> None:
    """
    Simpan log aktivitas user
    """

    session = get_session()

    try:

        log = AuditLog(
            username=username,
            action=action,
            status=status,
            message=message,
        )

        session.add(log)

        session.commit()

        logger.info(
            f"{username} | {action} | {status}"
        )

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal menyimpan audit log: {exc}"
        )

    finally:

        session.close()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("TEST AUDIT LOG")

    log_action(
        username="admin",
        action="tambah_barang",
        status="SUCCESS",
        message="Barang berhasil dibuat",
    )