"""
api/user_api.py
User Management API untuk toko-ai-agent

Fitur:
- List user
- Tambah user
- Update role user
- Hapus user
- Admin-only access
"""

from typing import List, Dict

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from core.user_manager import (
    User,
    hash_password,
)

from api.dependencies import (
    get_current_user_from_header,
    require_admin,
)

from logging_config import get_logger


logger = get_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# =========================================================
# UTIL
# =========================================================

def get_session():

    return SessionLocal()


VALID_ROLES = [
    "admin",
    "kasir",
]


# =========================================================
# LIST USERS
# =========================================================

@router.get("/")
def list_users(
    user=Depends(
        get_current_user_from_header
    ),
) -> List[Dict]:

    require_admin(user)

    session = get_session()

    try:

        results = session.execute(
            select(User)
            .order_by(
                User.username.asc()
            )
        ).scalars().all()

        data = []

        for u in results:

            data.append(
                {
                    "id": u.id,
                    "username": u.username,
                    "role": u.role,
                    "created_at": (
                        u.created_at.isoformat()
                        if u.created_at
                        else None
                    ),
                }
            )

        return data

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal list users: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()


# =========================================================
# CREATE USER
# =========================================================

@router.post("/")
def create_user_api(
    data: Dict,
    user=Depends(
        get_current_user_from_header
    ),
) -> Dict:

    require_admin(user)

    session = get_session()

    try:

        username = data.get(
            "username"
        )

        password = data.get(
            "password"
        )

        role = data.get(
            "role"
        )

        if not username:

            raise HTTPException(
                status_code=400,
                detail="Username wajib",
            )

        if not password:

            raise HTTPException(
                status_code=400,
                detail="Password wajib",
            )

        if role not in VALID_ROLES:

            raise HTTPException(
                status_code=400,
                detail="Role tidak valid",
            )

        existing = session.execute(
            select(User)
            .where(
                User.username == username
            )
        ).scalar_one_or_none()

        if existing:

            raise HTTPException(
                status_code=409,
                detail="User sudah ada",
            )

        password_hash = hash_password(
            password
        )

        new_user = User(
            username=username,
            password_hash=password_hash,
            role=role,
        )

        session.add(
            new_user
        )

        session.commit()

        logger.info(
            f"User dibuat: {username}"
        )

        return {
            "status": "success",
            "username": username,
            "role": role,
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal create user: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()


# =========================================================
# UPDATE ROLE USER
# =========================================================

@router.put("/{user_id}")
def update_user_role(
    user_id: int,
    data: Dict,
    user=Depends(
        get_current_user_from_header
    ),
) -> Dict:

    require_admin(user)

    session = get_session()

    try:

        role = data.get(
            "role"
        )

        if role not in VALID_ROLES:

            raise HTTPException(
                status_code=400,
                detail="Role tidak valid",
            )

        target_user = session.execute(
            select(User)
            .where(
                User.id == user_id
            )
        ).scalar_one_or_none()

        if not target_user:

            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan",
            )

        target_user.role = role

        session.commit()

        logger.info(
            f"User role updated: {user_id}"
        )

        return {
            "status": "success",
            "user_id": user_id,
            "role": role,
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal update role: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()


# =========================================================
# DELETE USER
# =========================================================

@router.delete("/{user_id}")
def delete_user_api(
    user_id: int,
    user=Depends(
        get_current_user_from_header
    ),
) -> Dict:

    require_admin(user)

    session = get_session()

    try:

        target_user = session.execute(
            select(User)
            .where(
                User.id == user_id
            )
        ).scalar_one_or_none()

        if not target_user:

            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan",
            )

        if target_user.role == "admin":

            raise HTTPException(
                status_code=403,
                detail="Admin tidak boleh dihapus",
            )

        username = target_user.username

        session.delete(
            target_user
        )

        session.commit()

        logger.info(
            f"User dihapus: {username}"
        )

        return {
            "status": "success",
            "username": username,
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal delete user: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()

# =========================================================
# CHANGE PASSWORD
# =========================================================

from core.user_manager import verify_password


@router.put("/change-password")
def change_password(
    data: Dict,
    user=Depends(
        get_current_user_from_header
    ),
) -> Dict:

    session = get_session()

    try:

        username = user.get(
            "username"
        )

        old_password = data.get(
            "old_password"
        )

        new_password = data.get(
            "new_password"
        )

        # -------------------------------------------------
        # VALIDASI INPUT
        # -------------------------------------------------

        if not old_password:

            raise HTTPException(
                status_code=400,
                detail="Password lama wajib",
            )

        if not new_password:

            raise HTTPException(
                status_code=400,
                detail="Password baru wajib",
            )

        if len(new_password) < 4:

            raise HTTPException(
                status_code=400,
                detail="Password minimal 4 karakter",
            )

        # -------------------------------------------------
        # AMBIL USER
        # -------------------------------------------------

        db_user = session.execute(
            select(User)
            .where(
                User.username == username
            )
        ).scalar_one_or_none()

        if not db_user:

            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan",
            )

        # -------------------------------------------------
        # VERIFIKASI PASSWORD LAMA
        # -------------------------------------------------

        if not verify_password(
            old_password,
            db_user.password_hash,
        ):

            raise HTTPException(
                status_code=401,
                detail="Password lama salah",
            )

        # -------------------------------------------------
        # UPDATE PASSWORD
        # -------------------------------------------------

        db_user.password_hash = hash_password(
            new_password
        )

        session.commit()

        logger.info(
            f"Password diganti: {username}"
        )

        return {
            "status": "success",
            "message": "Password berhasil diganti",
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal change password: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        session.rollback()

        logger.error(
            f"Unexpected error change password: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()

# =========================================================
# LIST ACTIVITY LOG
# =========================================================

@router.get("/activity")
def list_activity_logs(
    user=Depends(
        get_current_user_from_header
    ),
):

    require_admin(user)

    session = get_session()

    try:

        results = session.execute(
            select(ActivityLog)
            .order_by(
                ActivityLog.created_at.desc()
            )
            .limit(100)
        ).scalars().all()

        data = []

        for log in results:

            data.append(
                {
                    "username": log.username,
                    "action": log.action,
                    "endpoint": log.endpoint,
                    "status": log.status,
                    "message": log.message,
                    "created_at": log.created_at.isoformat(),
                }
            )

        return data

    finally:

        session.close()

# =========================================================
# RESET PASSWORD OLEH ADMIN
# =========================================================

@router.put("/reset-password/{user_id}")
def admin_reset_password(
    user_id: int,
    data: Dict,
    user=Depends(
        get_current_user_from_header
    ),
) -> Dict:

    require_admin(user)

    session = get_session()

    try:

        new_password = data.get(
            "new_password"
        )

        if not new_password:

            raise HTTPException(
                status_code=400,
                detail="Password baru wajib",
            )

        if len(new_password) < 4:

            raise HTTPException(
                status_code=400,
                detail="Password minimal 4 karakter",
            )

        # =============================
        # AMBIL USER TARGET
        # =============================

        target_user = session.execute(
            select(User)
            .where(
                User.id == user_id
            )
        ).scalar_one_or_none()

        if not target_user:

            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan",
            )

        # =============================
        # UPDATE PASSWORD
        # =============================

        target_user.password_hash = hash_password(
            new_password
        )

        # =============================
        # UNLOCK ACCOUNT
        # =============================

        target_user.failed_login_attempts = 0

        target_user.is_locked = False

        target_user.locked_until = None

        session.commit()

        logger.info(
            f"Admin reset password user: {target_user.username}"
        )

        return {
            "status": "success",
            "username": target_user.username,
            "message": "Password berhasil direset",
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal reset password: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()

# =========================================================
# LOGOUT USER
# =========================================================

from fastapi import Header
from core.token_manager import blacklist_token


@router.post("/logout")
def logout_user(
    authorization: str = Header(...),
):

    try:

        if not authorization.startswith(
            "Bearer "
        ):

            raise HTTPException(
                status_code=401,
                detail="Format token salah",
            )

        token = authorization.replace(
            "Bearer ",
            ""
        )

        blacklist_token(
            token
        )

        logger.info(
            "User logout"
        )

        return {
            "status": "success",
            "message": "Logout berhasil",
        }

    except Exception as exc:

        logger.error(
            f"Logout error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Logout gagal",
        )

# =========================================================
# REFRESH TOKEN
# =========================================================

from database.models_refresh_token import (
    RefreshToken,
)

from api.auth import (
    create_access_token,
)

import datetime


@router.post("/refresh-token")
def refresh_token_api(
    data: Dict,
):

    session = get_session()

    try:

        token = data.get(
            "refresh_token"
        )

        if not token:

            raise HTTPException(
                status_code=400,
                detail="Refresh token wajib",
            )

        record = session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.token == token
            )
        ).scalar_one_or_none()

        if not record:

            raise HTTPException(
                status_code=401,
                detail="Refresh token invalid",
            )

        if record.is_revoked:

            raise HTTPException(
                status_code=401,
                detail="Refresh token revoked",
            )

        new_access_token = create_access_token(
            data={
                "sub": record.username,
            }
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }

    finally:

        session.close()


# =========================================================
# FORCE LOGOUT USER (ADMIN)
# =========================================================

from core.token_manager import (
    revoke_all_user_tokens,
)


@router.post("/force-logout/{user_id}")
def force_logout_user(
    user_id: int,
    user=Depends(
        get_current_user_from_header
    ),
):

    require_admin(user)

    session = get_session()

    try:

        target_user = session.execute(
            select(User)
            .where(
                User.id == user_id
            )
        ).scalar_one_or_none()

        if not target_user:

            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan",
            )

        username = target_user.username

        revoke_all_user_tokens(
            username
        )

        logger.info(
            f"Force logout user: {username}"
        )

        return {
            "status": "success",
            "username": username,
            "message": "User berhasil logout paksa",
        }

    except HTTPException:

        raise

    except Exception as exc:

        logger.error(
            f"Force logout error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Force logout gagal",
        )

    finally:

        session.close()


# =========================================================
# BACKUP DATABASE
# =========================================================

from backup.manual_backup import create_backup


@router.post("/backup")
def backup_database_api(
    user=Depends(
        get_current_user_from_header
    ),
):

    require_admin(user)

    try:

        backup_path = create_backup()

        logger.info(
            f"Backup oleh admin: {user.get('username')}"
        )

        return {
            "status": "success",
            "backup_file": backup_path,
        }

    except Exception as exc:

        logger.error(
            f"Backup error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Backup gagal",
        )

# =========================================================
# RESTORE DATABASE
# =========================================================

from backup.restore_backup import (
    restore_database,
)


@router.post("/restore")
def restore_database_api(
    data: Dict,
    user=Depends(
        get_current_user_from_header
    ),
):

    require_admin(user)

    try:

        backup_file = data.get(
            "backup_file"
        )

        if not backup_file:

            raise HTTPException(
                status_code=400,
                detail="Backup file wajib diisi",
            )

        result = restore_database(
            backup_file
        )

        logger.warning(
            f"Database direstore oleh admin: {user.get('username')}"
        )

        return result

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="File backup tidak ditemukan",
        )

    except Exception as exc:

        logger.error(
            f"Restore error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Restore gagal",
        )


# =========================================================
# LIST BACKUP FILES
# =========================================================

from backup.list_backups import (
    list_backup_files,
)


@router.get("/backups")
def list_backups_api(
    user=Depends(
        get_current_user_from_header
    ),
):

    require_admin(user)

    try:

        backups = list_backup_files()

        return {
            "status": "success",
            "total": len(backups),
            "data": backups,
        }

    except Exception as exc:

        logger.error(
            f"Gagal ambil list backup: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal membaca backup",
        )



