"""
api/dashboard_api.py
Dashboard API menggunakan FastAPI untuk toko-ai-agent

Perbaikan:
- Session management lebih aman
- Error handling lebih stabil
- Logging lebih jelas
- Type hint lengkap
- Response konsisten
"""

from datetime import datetime, date
from typing import List, Dict, Generator

from fastapi import FastAPI, HTTPException

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from database.models import (
    Barang,
    StokAudit,
    Transaksi,
    Biaya,
)

from system.health_check import run_health_check
from logging_config import get_logger


logger = get_logger(__name__)


app = FastAPI(
    title="Toko AI Agent API",
    version="1.0",
)


# =========================================================
# UTIL
# =========================================================

def get_session() -> Generator:
    """
    Generator session database aman
    """

    session = SessionLocal()

    try:

        yield session

    finally:

        try:

            session.close()

        except Exception as exc:

            logger.error(
                f"Gagal menutup session: {exc}"
            )


def get_today() -> date:

    return datetime.now().date()


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root() -> Dict[str, str]:

    logger.info("API root accessed")

    return {
        "status": "running",
        "service": "toko-ai-agent",
    }


# =========================================================
# STOK HARI INI
# =========================================================

@app.get("/stok")
def get_stok_hari_ini() -> List[Dict]:

    session = SessionLocal()

    try:

        tanggal = get_today()

        logger.info(
            f"Request stok untuk tanggal: {tanggal}"
        )

        results = session.execute(
            select(
                Barang.nama,
                StokAudit.stok_akhir,
            )
            .join(
                Barang,
                Barang.id == StokAudit.barang_id,
            )
            .where(
                StokAudit.tanggal == tanggal,
            )
        ).all()

        data: List[Dict] = []

        for row in results:

            data.append(
                {
                    "nama": row.nama,
                    "stok": float(
                        row.stok_akhir or 0
                    ),
                }
            )

        logger.info(
            f"Jumlah data stok: {len(data)}"
        )

        return data

    except SQLAlchemyError as exc:

        logger.error(
            f"Database error stok: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        logger.error(
            f"Unexpected error stok: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()


# =========================================================
# LAPORAN HARIAN
# =========================================================

@app.get("/laporan/hari-ini")
def get_laporan_harian() -> Dict:

    session = SessionLocal()

    try:

        tanggal = get_today()

        logger.info(
            f"Request laporan harian: {tanggal}"
        )

        pendapatan = session.execute(
            select(
                func.sum(
                    Transaksi.pendapatan
                )
            )
            .where(
                Transaksi.tanggal == tanggal
            )
        ).scalar()

        biaya = session.execute(
            select(
                func.sum(
                    Biaya.jumlah
                )
            )
            .where(
                Biaya.tanggal == tanggal
            )
        ).scalar()

        total_pendapatan = float(
            pendapatan or 0
        )

        total_biaya = float(
            biaya or 0
        )

        laba = total_pendapatan - total_biaya

        response = {
            "tanggal": str(tanggal),
            "pendapatan": total_pendapatan,
            "biaya": total_biaya,
            "laba": laba,
        }

        logger.info(
            f"Laporan harian berhasil"
        )

        return response

    except SQLAlchemyError as exc:

        logger.error(
            f"Database error laporan: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        logger.error(
            f"Unexpected error laporan: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check() -> Dict:

    try:

        logger.info(
            "Health check requested"
        )

        result = run_health_check()

        return {
            "status": "ok",
            "detail": result,
        }

    except Exception as exc:

        logger.error(
            f"Health check error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Health check failed",
        )


# =========================================================
# INFO SYSTEM
# =========================================================

@app.get("/info")
def system_info() -> Dict:

    try:

        return {
            "app": "toko-ai-agent",
            "version": "1.0",
            "server_time": datetime.now().isoformat(),
        }

    except Exception as exc:

        logger.error(
            f"System info error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="System info failed",
        )