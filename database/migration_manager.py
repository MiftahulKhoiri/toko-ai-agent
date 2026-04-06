"""
database/migration_manager.py
Database migration manager untuk toko-ai-agent

Fitur:
- Versioning database
- Apply migration
- Tracking migration history
- Aman untuk production
"""

from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    select,
)
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal, Base
from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# MODEL MIGRATION HISTORY
# =========================================================

class MigrationHistory(Base):

    __tablename__ = "migration_history"

    id = Column(Integer, primary_key=True)

    version = Column(
        String,
        unique=True,
        nullable=False,
    )

    description = Column(
        String,
        nullable=False,
    )

    applied_at = Column(
        DateTime,
        default=datetime.now,
    )


# =========================================================
# UTIL
# =========================================================

def get_session():
    return SessionLocal()


def get_applied_versions() -> List[str]:

    session = get_session()

    try:

        results = session.execute(
            select(MigrationHistory.version)
        ).scalars().all()

        return list(results)

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal mengambil migration history: {exc}"
        )

        return []

    finally:

        session.close()


def record_migration(
    version: str,
    description: str,
) -> None:

    session = get_session()

    try:

        migration = MigrationHistory(
            version=version,
            description=description,
        )

        session.add(migration)

        session.commit()

        logger.info(
            f"Migration recorded: {version}"
        )

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal mencatat migration: {exc}"
        )

    finally:

        session.close()


# =========================================================
# MIGRATION REGISTRY
# =========================================================

def migration_001():

    """
    Contoh migration pertama
    """

    logger.info(
        "Menjalankan migration 001"
    )

    # Contoh:
    # Tambah kolom / tabel
    # atau update data


MIGRATIONS = [

    (
        "001_initial_setup",
        "Initial database setup",
        migration_001,
    ),

]


# =========================================================
# APPLY MIGRATIONS
# =========================================================

def apply_migrations():

    logger.info(
        "Memulai database migration"
    )

    applied_versions = get_applied_versions()

    for version, description, func in MIGRATIONS:

        if version in applied_versions:

            logger.info(
                f"Migration sudah ada: {version}"
            )

            continue

        try:

            logger.info(
                f"Applying migration: {version}"
            )

            func()

            record_migration(
                version,
                description,
            )

            logger.info(
                f"Migration sukses: {version}"
            )

        except Exception as exc:

            logger.error(
                f"Migration gagal: {version} | {exc}"
            )

            break

    logger.info(
        "Migration selesai"
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    apply_migrations()