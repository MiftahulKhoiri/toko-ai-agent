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

# =========================================================
# INPUT PENDAPATAN
# =========================================================

@app.post("/transaksi/pendapatan")
def input_pendapatan(data: Dict) -> Dict:

    session = SessionLocal()

    try:

        jumlah = data.get("jumlah")

        if jumlah is None:

            raise HTTPException(
                status_code=400,
                detail="Jumlah wajib diisi",
            )

        if float(jumlah) < 0:

            raise HTTPException(
                status_code=400,
                detail="Jumlah tidak boleh negatif",
            )

        tanggal = get_today()

        existing = session.execute(
            select(Transaksi)
            .where(
                Transaksi.tanggal == tanggal
            )
        ).scalar_one_or_none()

        if existing:

            existing.pendapatan = float(jumlah)

            message = "Pendapatan diperbarui"

        else:

            transaksi = Transaksi(
                tanggal=tanggal,
                pendapatan=float(jumlah),
            )

            session.add(transaksi)

            message = "Pendapatan disimpan"

        session.commit()

        logger.info(
            f"Pendapatan berhasil: {jumlah}"
        )

        return {
            "status": "success",
            "message": message,
            "jumlah": float(jumlah),
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal simpan pendapatan: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()


# =========================================================
# INPUT BIAYA
# =========================================================

@app.post("/transaksi/biaya")
def input_biaya(data: Dict) -> Dict:

    session = SessionLocal()

    try:

        nama = data.get("nama")

        jumlah = data.get("jumlah")

        if not nama:

            raise HTTPException(
                status_code=400,
                detail="Nama biaya wajib diisi",
            )

        if jumlah is None:

            raise HTTPException(
                status_code=400,
                detail="Jumlah wajib diisi",
            )

        if float(jumlah) < 0:

            raise HTTPException(
                status_code=400,
                detail="Jumlah tidak boleh negatif",
            )

        tanggal = get_today()

        biaya = Biaya(
            tanggal=tanggal,
            nama=nama,
            jumlah=float(jumlah),
        )

        session.add(biaya)

        session.commit()

        logger.info(
            f"Biaya berhasil: {nama} {jumlah}"
        )

        return {
            "status": "success",
            "nama": nama,
            "jumlah": float(jumlah),
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal simpan biaya: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()

# =========================================================
# INPUT AUDIT STOK
# =========================================================

@app.post("/audit-stok")
def input_audit_stok(data: Dict) -> Dict:

    session = SessionLocal()

    try:

        nama_barang = data.get("nama_barang")
        stok_masuk = data.get("stok_masuk", 0)
        stok_keluar = data.get("stok_keluar", 0)
        catatan = data.get("catatan", "")

        # -------------------------------------------------
        # VALIDASI INPUT
        # -------------------------------------------------

        if not nama_barang:

            raise HTTPException(
                status_code=400,
                detail="Nama barang wajib diisi",
            )

        if float(stok_masuk) < 0:

            raise HTTPException(
                status_code=400,
                detail="Stok masuk tidak boleh negatif",
            )

        if float(stok_keluar) < 0:

            raise HTTPException(
                status_code=400,
                detail="Stok keluar tidak boleh negatif",
            )

        tanggal = get_today()

        # -------------------------------------------------
        # CEK BARANG
        # -------------------------------------------------

        barang = session.execute(
            select(Barang)
            .where(
                Barang.nama == nama_barang
            )
        ).scalar_one_or_none()

        if not barang:

            raise HTTPException(
                status_code=404,
                detail="Barang tidak ditemukan",
            )

        # -------------------------------------------------
        # AMBIL STOK TERAKHIR
        # -------------------------------------------------

        last_audit = session.execute(
            select(StokAudit)
            .where(
                StokAudit.barang_id == barang.id
            )
            .order_by(
                StokAudit.tanggal.desc()
            )
        ).scalars().first()

        stok_awal = (
            float(last_audit.stok_akhir)
            if last_audit
            else 0.0
        )

        stok_akhir = (
            stok_awal
            + float(stok_masuk)
            - float(stok_keluar)
        )

        # -------------------------------------------------
        # VALIDASI STOK
        # -------------------------------------------------

        if stok_akhir < 0:

            raise HTTPException(
                status_code=400,
                detail="Stok akhir tidak boleh negatif",
            )

        # -------------------------------------------------
        # SIMPAN AUDIT
        # -------------------------------------------------

        audit = StokAudit(
            barang_id=barang.id,
            tanggal=tanggal,
            stok_awal=stok_awal,
            stok_masuk=float(stok_masuk),
            stok_keluar=float(stok_keluar),
            stok_akhir=stok_akhir,
            catatan=catatan,
        )

        session.add(audit)

        session.commit()

        logger.info(
            f"Audit stok berhasil: {nama_barang}"
        )

        return {
            "status": "success",
            "nama_barang": nama_barang,
            "stok

# =========================================================
# TAMBAH BARANG
# =========================================================

@app.post("/barang")
def tambah_barang_api(data: Dict) -> Dict:

    session = SessionLocal()

    try:

        nama = data.get("nama")
        satuan = data.get("satuan")

        # -------------------------------------------------
        # VALIDASI INPUT
        # -------------------------------------------------

        if not nama:

            raise HTTPException(
                status_code=400,
                detail="Nama barang wajib diisi",
            )

        if not satuan:

            raise HTTPException(
                status_code=400,
                detail="Satuan wajib diisi",
            )

        satuan_valid = ["kg", "liter", "pcs"]

        if satuan not in satuan_valid:

            raise HTTPException(
                status_code=400,
                detail="Satuan harus kg, liter, atau pcs",
            )

        # -------------------------------------------------
        # CEK DUPLIKAT
        # -------------------------------------------------

        existing = session.execute(
            select(Barang)
            .where(
                Barang.nama == nama
            )
        ).scalar_one_or_none()

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Barang sudah ada",
            )

        # -------------------------------------------------
        # SIMPAN DATA
        # -------------------------------------------------

        barang = Barang(
            nama=nama,
            satuan=satuan,
        )

        session.add(barang)

        session.commit()

        logger.info(
            f"Barang berhasil dibuat: {nama}"
        )

        return {
            "status": "success",
            "nama": nama,
            "satuan": satuan,
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal tambah barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        session.rollback()

        logger.error(
            f"Unexpected error tambah barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()

# =========================================================
# LIST BARANG
# =========================================================

@app.get("/barang")
def list_barang() -> List[Dict]:

    session = SessionLocal()

    try:

        logger.info(
            "Request list barang"
        )

        results = session.execute(
            select(
                Barang.id,
                Barang.nama,
                Barang.satuan,
                Barang.created_at,
            )
            .order_by(
                Barang.nama.asc()
            )
        ).all()

        data: List[Dict] = []

        for row in results:

            data.append(
                {
                    "id": row.id,
                    "nama": row.nama,
                    "satuan": row.satuan,
                    "created_at": (
                        row.created_at.isoformat()
                        if row.created_at
                        else None
                    ),
                }
            )

        logger.info(
            f"Jumlah barang: {len(data)}"
        )

        return data

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal ambil list barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        logger.error(
            f"Unexpected error list barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()

