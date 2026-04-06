"""
api/dashboard_api.py
Dashboard API menggunakan FastAPI untuk toko-ai-agent

Fitur:
- API stok hari ini
- API laporan harian
- API health check
- Logging
- Error handling
"""

from datetime import datetime
from typing import List, Dict

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

def get_session():
    return SessionLocal()


def get_today():

    return datetime.now().date()


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "status": "running",
        "service": "toko-ai-agent",
    }


# =========================================================
# STOK HARI INI
# =========================================================

@app.get("/stok")
def get_stok_hari_ini() -> List[Dict]:

    session = get_session()

    try:

        tanggal = get_today()

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

        data = []

        for row in results:

            data.append(
                {
                    "nama": row.nama,
                    "stok": row.stok_akhir,
                }
            )

        return data

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal ambil stok: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()


# =========================================================
# LAPORAN HARIAN
# =========================================================

@app.get("/laporan/hari-ini")
def get_laporan_harian():

    session = get_session()

    try:

        tanggal = get_today()

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

        pendapatan = float(pendapatan or 0)

        biaya = float(biaya or 0)

        laba = pendapatan - biaya

        return {
            "tanggal": str(tanggal),
            "pendapatan": pendapatan,
            "biaya": biaya,
            "laba": laba,
        }

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal ambil laporan: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    try:

        result = run_health_check()

        return result

    except Exception as exc:

        logger.error(
            f"Health check error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Health check failed",
        )