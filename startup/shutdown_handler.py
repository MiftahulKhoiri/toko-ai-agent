"""
startup/shutdown_handler.py
Graceful shutdown handler untuk toko-ai-agent

Fitur:
- Tangkap CTRL+C / SIGTERM
- Backup terakhir saat shutdown
- Stop session manager
- Logging shutdown
- Aman untuk production
"""

import signal
import sys
from typing import Optional

from backup.auto_backup import backup_all
from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# GLOBAL REFERENCES
# =========================================================

SESSION_MANAGER = None


# =========================================================
# REGISTER SESSION
# =========================================================

def register_session_manager(session_manager) -> None:
    """
    Simpan reference session manager
    """

    global SESSION_MANAGER

    SESSION_MANAGER = session_manager


# =========================================================
# SHUTDOWN LOGIC
# =========================================================

def graceful_shutdown(signum: Optional[int], frame) -> None:
    """
    Jalankan proses shutdown aman
    """

    try:

        logger.info(
            f"Shutdown signal diterima: {signum}"
        )

        print()
        print("Menjalankan shutdown aman...")

        # Stop session manager

        if SESSION_MANAGER:

            try:

                SESSION_MANAGER.stop()

                logger.info(
                    "Session manager stopped"
                )

            except Exception as exc:

                logger.error(
                    f"Gagal stop session: {exc}"
                )

        # Backup terakhir

        try:

            print("Membuat backup terakhir...")

            backup_all()

            logger.info(
                "Backup terakhir selesai"
            )

        except Exception as exc:

            logger.error(
                f"Gagal backup saat shutdown: {exc}"
            )

        print("Shutdown selesai")

    except Exception as exc:

        logger.error(
            f"Shutdown error: {exc}"
        )

    finally:

        sys.exit(0)


# =========================================================
# REGISTER SIGNAL
# =========================================================

def register_shutdown_handler() -> None:
    """
    Daftarkan handler untuk shutdown
    """

    try:

        signal.signal(
            signal.SIGINT,
            graceful_shutdown,
        )

        signal.signal(
            signal.SIGTERM,
            graceful_shutdown,
        )

        logger.info(
            "Shutdown handler registered"
        )

    except Exception as exc:

        logger.error(
            f"Gagal register shutdown handler: {exc}"
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("TEST SHUTDOWN HANDLER")

    register_shutdown_handler()

    print("Tekan CTRL+C untuk test")

    while True:
        pass