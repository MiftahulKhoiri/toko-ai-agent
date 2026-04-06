"""core/user_manager.py - Manajemen user dan role untuk toko-ai-agent

Fitur:
- Login user
- Password hashing
- Role admin / kasir
- Default admin
"""

import hashlib
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, select
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal, Base
from logging_config import get_logger

logger = get_logger(__name__)


# =========================================================
# MODEL USER
# =========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# =========================================================
# UTIL
# =========================================================
def get_session():
    return SessionLocal()


def hash_password(password: str) -> str:
    """Hash password menggunakan SHA256"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verifikasi password"""
    return hash_password(password) == password_hash


# =========================================================
# CREATE USER
# =========================================================
def create_user(username: str, password: str, role: str) -> None:
    session = get_session()
    try:
        if role not in ("admin", "kasir"):
            print("Role tidak valid")
            return
        existing = session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        if existing:
            print("User sudah ada")
            return
        password_hash = hash_password(password)
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
        )
        session.add(user)
        session.commit()
        logger.info(f"User dibuat: {username}")
        print("User berhasil dibuat")
    except SQLAlchemyError as exc:
        session.rollback()
        logger.error(f"Gagal membuat user: {exc}")
    finally:
        session.close()


# =========================================================
# LOGIN
# =========================================================
def login_user(username: str, password: str) -> Optional[str]:
    session = get_session()
    try:
        user = session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        if not user:
            print("User tidak ditemukan")
            return None
        if not verify_password(password, user.password_hash):
            print("Password salah")
            return None
        logger.info(f"Login sukses: {username}")
        print(f"Login berhasil ({user.role})")
        return user.role
    except SQLAlchemyError as exc:
        logger.error(f"Login error: {exc}")
        return None
    finally:
        session.close()


# =========================================================
# DEFAULT ADMIN
# =========================================================
def create_default_admin():
    session = get_session()
    try:
        existing = session.execute(
            select(User).where(User.username == "admin")
        ).scalar_one_or_none()
        if existing:
            return
        password_hash = hash_password("admin123")
        admin = User(
            username="admin",
            password_hash=password_hash,
            role="admin",
        )
        session.add(admin)
        session.commit()
        logger.info("Default admin dibuat")
        print("Default admin dibuat")
        print("username: admin")
        print("password: admin123")
    except SQLAlchemyError as exc:
        session.rollback()
        logger.error(f"Gagal membuat admin default: {exc}")
    finally:
        session.close()


# =========================================================
# ROLE CHECK
# =========================================================
def require_admin(role: str) -> bool:
    if role != "admin":
        print("Akses ditolak — hanya admin")
        return False
    return True


# =========================================================
# TEST
# =========================================================
if __name__ == "__main__":
    print("TEST USER SYSTEM")
    create_default_admin()
    create_user(username="kasir1", password="123", role="kasir")
    login_user(username="admin", password="admin123")