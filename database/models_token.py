"""
database/models_token.py
Model blacklist token JWT
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from database.db import Base


class TokenBlacklist(Base):

    __tablename__ = "token_blacklist"

    id = Column(
        Integer,
        primary_key=True,
    )

    token = Column(
        String,
        nullable=False,
        unique=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )