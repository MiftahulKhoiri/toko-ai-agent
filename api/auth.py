"""
api/auth.py
JWT authentication untuk toko-ai-agent
"""

from datetime import datetime, timedelta
from typing import Optional, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select

from database.db import SessionLocal
from core.user_manager import User

from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

SECRET_KEY = "CHANGE_THIS_SECRET_KEY"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# =========================================================
# UTIL
# =========================================================

def get_session():

    return SessionLocal()


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None,
) -> str:

    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


# =========================================================
# LOGIN
# =========================================================

def login_user_api(
    username: str,
    password: str,
) -> Dict:

    session = get_session()

    try:

        user = session.execute(
            select(User)
            .where(
                User.username == username
            )
        ).scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User tidak ditemukan",
            )

        if not verify_password(
            password,
            user.password_hash,
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password salah",
            )

        access_token = create_access_token(
            data={
                "sub": user.username,
                "role": user.role,
            }
        )

        logger.info(
            f"Login sukses: {username}"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role,
        }

    finally:

        session.close()


# =========================================================
# VERIFY TOKEN
# =========================================================

def get_current_user(
    token: str,
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username: str = payload.get(
            "sub"
        )

        role: str = payload.get(
            "role"
        )

        if username is None:

            raise HTTPException(
                status_code=401,
                detail="Token invalid",
            )

        return {
            "username": username,
            "role": role,
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Token invalid",
        )