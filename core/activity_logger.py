"""
core/activity_logger.py
Utility logging aktivitas user
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from database.models_activity_log import ActivityLog

from logging_config import get_logger


logger = get_logger(__name__)


def log_activity(
    username: str,
    action: str,
    endpoint: str,
    status: str,
    message: Optional[str] = None,
) -> None:

    session = SessionLocal()

    try:

        log = ActivityLog(
            username=username,
            action=action,
            endpoint=endpoint,
            status=status,
            message=message,
        )

        session.add(log)

        session.commit()

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal simpan activity log: {exc}"
        )

    finally:

        session.close()