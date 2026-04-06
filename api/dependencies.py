"""
api/dependencies.py
Security dependencies untuk JWT authentication
"""

from typing import Dict

from fastapi import (
    Header,
    HTTPException,
    status,
)

from api.auth import get_current_user

from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# GET CURRENT USER FROM HEADER
# =========================================================

def get_current_user_from_header(
    authorization: str = Header(...),
) -> Dict:

    try:

        if not authorization.startswith(
            "Bearer "
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Format token salah",
            )

        token = authorization.replace(
            "Bearer ",
            ""
        )

        user = get_current_user(
            token
        )

        return user

    except HTTPException:

        raise

    except Exception as exc:

        logger.error(
            f"Auth error: {exc}"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
        )


# =========================================================
# REQUIRE ADMIN
# =========================================================

def require_admin(
    user: Dict = None,
):

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    if user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Hanya admin yang boleh",
        )

    return user


# =========================================================
# REQUIRE LOGIN
# =========================================================

def require_login(
    user: Dict = None,
):

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    return user

def audit_success(
    user,
    action,
    endpoint,
):

    from core.activity_logger import log_activity

    log_activity(
        username=user.get("username"),
        action=action,
        endpoint=endpoint,
        status="SUCCESS",
    )


def audit_failed(
    user,
    action,
    endpoint,
    error,
):

    from core.activity_logger import log_activity

    log_activity(
        username=user.get("username"),
        action=action,
        endpoint=endpoint,
        status="FAILED",
        message=str(error),
    )