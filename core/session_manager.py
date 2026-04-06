"""
core/session_manager.py
Manajemen session timeout untuk toko-ai-agent

Fitur:
- Session timeout otomatis
- Reset timer saat ada aktivitas
- Thread aman (daemon)
- Tidak mengganggu main loop
"""

import threading
import time
from datetime import datetime
from typing import Optional

from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

DEFAULT_TIMEOUT_SECONDS = 600  # 10 menit


# =========================================================
# SESSION MANAGER
# =========================================================

class SessionManager:

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:

        self.timeout_seconds = timeout_seconds

        self.last_activity: datetime = datetime.now()

        self.active: bool = False

        self.thread: Optional[threading.Thread] = None

        self.lock = threading.Lock()

        self.on_timeout_callback = None

    # =====================================================
    # START
    # =====================================================

    def start(self) -> None:
        """
        Mulai monitoring session
        """

        try:

            if self.active:

                return

            self.active = True

            self.thread = threading.Thread(
                target=self._monitor,
                daemon=True,
            )

            self.thread.start()

            logger.info(
                "Session monitor started"
            )

        except Exception as exc:

            logger.error(
                f"Gagal start session monitor: {exc}"
            )

    # =====================================================
    # STOP
    # =====================================================

    def stop(self) -> None:
        """
        Stop monitoring
        """

        try:

            self.active = False

            logger.info(
                "Session monitor stopped"
            )

        except Exception as exc:

            logger.error(
                f"Gagal stop session monitor: {exc}"
            )

    # =====================================================
    # RESET TIMER
    # =====================================================

    def reset_timer(self) -> None:
        """
        Reset timer aktivitas
        """

        try:

            with self.lock:

                self.last_activity = datetime.now()

        except Exception as exc:

            logger.error(
                f"Gagal reset timer: {exc}"
            )

    # =====================================================
    # SET CALLBACK
    # =====================================================

    def set_timeout_callback(
        self,
        callback,
    ) -> None:
        """
        Set fungsi yang dijalankan saat timeout
        """

        self.on_timeout_callback = callback

    # =====================================================
    # MONITOR LOOP
    # =====================================================

    def _monitor(self) -> None:

        try:

            while self.active:

                time.sleep(5)

                with self.lock:

                    elapsed = (
                        datetime.now()
                        - self.last_activity
                    ).total_seconds()

                if elapsed >= self.timeout_seconds:

                    logger.warning(
                        "Session timeout"
                    )

                    if self.on_timeout_callback:

                        try:

                            self.on_timeout_callback()

                        except Exception as exc:

                            logger.error(
                                f"Callback error: {exc}"
                            )

                    self.reset_timer()

        except Exception as exc:

            logger.error(
                f"Session monitor error: {exc}"
            )