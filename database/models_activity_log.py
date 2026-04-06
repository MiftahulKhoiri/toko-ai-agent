"""
database/models_activity_log.py
Model Activity Log untuk audit trail user
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from database.db import Base


class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id = Column(
        Integer,
        primary_key=True,
    )

    username = Column(
        String,
        nullable=False,
    )

    action = Column(
        String,
        nullable=False,
    )

    endpoint = Column(
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
        default=datetime.utcnow,
    )