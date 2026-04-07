"""
core/token_manager.py
Token blacklist manager
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from database.db import SessionLocal
from database.models_token import TokenBlacklist

from logging_config import get_logger


logger = get_logger(__name__)


def blacklist_token(
    token: str,
) -> None:

    session = SessionLocal()

    try:

        existing = session.execute(
            select(TokenBlacklist)
            .where(
                TokenBlacklist.token == token
            )
        ).scalar_one_or_none()

        if existing:

            return

        record = TokenBlacklist(
            token=token
        )

        session.add(record)

        session.commit()

        logger.info(
            "Token diblacklist"
        )

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal blacklist token: {exc}"
        )

    finally:

        session.close()


def is_token_blacklisted(
    token: str,
) -> bool:

    session = SessionLocal()

    try:

        record = session.execute(
            select(TokenBlacklist)
            .where(
                TokenBlacklist.token == token
            )
        ).scalar_one_or_none()

        return record is not None

    finally:

        session.close()

# =========================================================
# REVOKE SEMUA REFRESH TOKEN USER
# =========================================================

from database.models_refresh_token import RefreshToken


def revoke_all_user_tokens(
    username: str,
):

    session = SessionLocal()

    try:

        tokens = session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.username == username,
                RefreshToken.is_revoked == False,
            )
        ).scalars().all()

        for token in tokens:

            token.is_revoked = True

        session.commit()

        logger.info(
            f"Semua token direvoke: {username}"
        )

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal revoke token: {exc}"
        )

    finally:

        session.close()