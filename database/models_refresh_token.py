"""
database/models_refresh_token.py
Model refresh token
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)

from database.db import Base


class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

    id = Column(
        Integer,
        primary_key=True,
    )

    username = Column(
        String,
        nullable=False,
    )

    token = Column(
        String,
        nullable=False,
        unique=True,
    )

    is_revoked = Column(
        Boolean,
        default=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )