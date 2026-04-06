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
from api.auth import login_user_api

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

# =========================================================
# EDIT BARANG
# =========================================================

@app.put("/barang/{barang_id}")
def edit_barang(
    barang_id: int,
    data: Dict,
) -> Dict:

    session = SessionLocal()

    try:

        logger.info(
            f"Request edit barang ID={barang_id}"
        )

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
        # CEK BARANG
        # -------------------------------------------------

        barang = session.execute(
            select(Barang)
            .where(
                Barang.id == barang_id
            )
        ).scalar_one_or_none()

        if not barang:

            raise HTTPException(
                status_code=404,
                detail="Barang tidak ditemukan",
            )

        # -------------------------------------------------
        # CEK DUPLIKAT NAMA
        # -------------------------------------------------

        existing = session.execute(
            select(Barang)
            .where(
                Barang.nama == nama,
                Barang.id != barang_id,
            )
        ).scalar_one_or_none()

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Nama barang sudah digunakan",
            )

        # -------------------------------------------------
        # UPDATE DATA
        # -------------------------------------------------

        barang.nama = nama
        barang.satuan = satuan

        session.commit()

        logger.info(
            f"Barang berhasil diupdate ID={barang_id}"
        )

        return {
            "status": "success",
            "id": barang_id,
            "nama": nama,
            "satuan": satuan,
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal update barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        session.rollback()

        logger.error(
            f"Unexpected error edit barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()

# =========================================================
# HAPUS BARANG
# =========================================================

@app.delete("/barang/{barang_id}")
def delete_barang(
    barang_id: int,
) -> Dict:

    session = SessionLocal()

    try:

        logger.info(
            f"Request hapus barang ID={barang_id}"
        )

        # -------------------------------------------------
        # CEK BARANG
        # -------------------------------------------------

        barang = session.execute(
            select(Barang)
            .where(
                Barang.id == barang_id
            )
        ).scalar_one_or_none()

        if not barang:

            raise HTTPException(
                status_code=404,
                detail="Barang tidak ditemukan",
            )

        # -------------------------------------------------
        # CEK RELASI STOK
        # -------------------------------------------------

        stok_exists = session.execute(
            select(StokAudit.id)
            .where(
                StokAudit.barang_id == barang_id
            )
            .limit(1)
        ).scalar_one_or_none()

        if stok_exists:

            raise HTTPException(
                status_code=409,
                detail="Barang tidak bisa dihapus karena masih memiliki riwayat stok",
            )

        # -------------------------------------------------
        # HAPUS DATA
        # -------------------------------------------------

        nama_barang = barang.nama

        session.delete(barang)

        session.commit()

        logger.info(
            f"Barang berhasil dihapus ID={barang_id}"
        )

        return {
            "status": "success",
            "id": barang_id,
            "nama": nama_barang,
            "message": "Barang berhasil dihapus",
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal hapus barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        session.rollback()

        logger.error(
            f"Unexpected error delete barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()

# =========================================================
# DATA CHART 7 HARI TERAKHIR
# =========================================================

from datetime import timedelta


@app.get("/laporan/chart")
def get_chart_data() -> Dict:

    session = SessionLocal()

    try:

        logger.info(
            "Request chart data 7 hari"
        )

        today = get_today()

        start_date = today - timedelta(
            days=6
        )

        # -------------------------------------------------
        # QUERY DATA
        # -------------------------------------------------

        results = session.execute(
            select(
                Transaksi.tanggal,
                func.sum(
                    Transaksi.pendapatan
                ),
                func.sum(
                    Biaya.jumlah
                ),
            )
            .outerjoin(
                Biaya,
                Biaya.tanggal == Transaksi.tanggal,
            )
            .where(
                Transaksi.tanggal >= start_date
            )
            .group_by(
                Transaksi.tanggal
            )
            .order_by(
                Transaksi.tanggal
            )
        ).all()

        labels = []
        pendapatan_data = []
        biaya_data = []
        laba_data = []

        for row in results:

            tanggal = row[0]

            pendapatan = float(
                row[1] or 0
            )

            biaya = float(
                row[2] or 0
            )

            laba = pendapatan - biaya

            labels.append(
                tanggal.strftime(
                    "%d-%m"
                )
            )

            pendapatan_data.append(
                pendapatan
            )

            biaya_data.append(
                biaya
            )

            laba_data.append(
                laba
            )

        return {
            "labels": labels,
            "pendapatan": pendapatan_data,
            "biaya": biaya_data,
            "laba": laba_data,
        }

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal ambil chart data: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    finally:

        session.close()

# =========================================================
# LAPORAN BERDASARKAN RENTANG TANGGAL
# =========================================================

from datetime import datetime


@app.get("/laporan/range")
def get_laporan_range(
    start: str,
    end: str,
) -> Dict:

    session = SessionLocal()

    try:

        logger.info(
            f"Request laporan range: {start} - {end}"
        )

        # -------------------------------------------------
        # VALIDASI FORMAT TANGGAL
        # -------------------------------------------------

        try:

            start_date = datetime.strptime(
                start,
                "%Y-%m-%d",
            ).date()

            end_date = datetime.strptime(
                end,
                "%Y-%m-%d",
            ).date()

        except ValueError:

            raise HTTPException(
                status_code=400,
                detail="Format tanggal harus YYYY-MM-DD",
            )

        if end_date < start_date:

            raise HTTPException(
                status_code=400,
                detail="Tanggal akhir tidak boleh sebelum tanggal awal",
            )

        # -------------------------------------------------
        # QUERY PENDAPATAN
        # -------------------------------------------------

        pendapatan = session.execute(
            select(
                func.sum(
                    Transaksi.pendapatan
                )
            )
            .where(
                Transaksi.tanggal >= start_date,
                Transaksi.tanggal <= end_date,
            )
        ).scalar()

        # -------------------------------------------------
        # QUERY BIAYA
        # -------------------------------------------------

        biaya = session.execute(
            select(
                func.sum(
                    Biaya.jumlah
                )
            )
            .where(
                Biaya.tanggal >= start_date,
                Biaya.tanggal <= end_date,
            )
        ).scalar()

        total_pendapatan = float(
            pendapatan or 0
        )

        total_biaya = float(
            biaya or 0
        )

        laba = (
            total_pendapatan
            - total_biaya
        )

        return {
            "start": str(start_date),
            "end": str(end_date),
            "pendapatan": total_pendapatan,
            "biaya": total_biaya,
            "laba": laba,
        }

    except HTTPException:

        session.rollback()

        raise

    except SQLAlchemyError as exc:

        session.rollback()

        logger.error(
            f"Gagal laporan range: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        session.rollback()

        logger.error(
            f"Unexpected error laporan range: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()

# =========================================================
# SEARCH BARANG
# =========================================================

@app.get("/barang/search")
def search_barang(
    q: str,
    limit: int = 20,
) -> List[Dict]:

    session = SessionLocal()

    try:

        logger.info(
            f"Search barang: {q}"
        )

        # -------------------------------------------------
        # VALIDASI INPUT
        # -------------------------------------------------

        if not q:

            raise HTTPException(
                status_code=400,
                detail="Query tidak boleh kosong",
            )

        if limit <= 0:

            limit = 20

        if limit > 100:

            limit = 100

        # -------------------------------------------------
        # QUERY SEARCH
        # -------------------------------------------------

        results = session.execute(
            select(
                Barang.id,
                Barang.nama,
                Barang.satuan,
            )
            .where(
                Barang.nama.ilike(
                    f"%{q}%"
                )
            )
            .order_by(
                Barang.nama.asc()
            )
            .limit(limit)
        ).all()

        data: List[Dict] = []

        for row in results:

            data.append(
                {
                    "id": row.id,
                    "nama": row.nama,
                    "satuan": row.satuan,
                }
            )

        logger.info(
            f"Hasil search: {len(data)} barang"
        )

        return data

    except HTTPException:

        raise

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal search barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        logger.error(
            f"Unexpected error search barang: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()

# =========================================================
# LIST BARANG DENGAN PAGINATION
# =========================================================

@app.get("/barang/paginated")
def list_barang_paginated(
    page: int = 1,
    page_size: int = 20,
) -> Dict:

    session = SessionLocal()

    try:

        logger.info(
            f"List barang page={page} size={page_size}"
        )

        # -------------------------------------------------
        # VALIDASI INPUT
        # -------------------------------------------------

        if page <= 0:

            page = 1

        if page_size <= 0:

            page_size = 20

        if page_size > 100:

            page_size = 100

        offset = (
            (page - 1)
            * page_size
        )

        # -------------------------------------------------
        # TOTAL DATA
        # -------------------------------------------------

        total_items = session.execute(
            select(
                func.count(
                    Barang.id
                )
            )
        ).scalar()

        total_items = int(
            total_items or 0
        )

        # -------------------------------------------------
        # QUERY DATA
        # -------------------------------------------------

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
            .offset(offset)
            .limit(page_size)
        ).all()

        data = []

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

        total_pages = (
            (total_items + page_size - 1)
            // page_size
        )

        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "data": data,
        }

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal list barang paginated: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Database error",
        )

    except Exception as exc:

        logger.error(
            f"Unexpected error pagination: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

    finally:

        session.close()

# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def login(
    data: Dict,
):

    username = data.get(
        "username"
    )

    password = data.get(
        "password"
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

    return login_user_api(
        username,
        password,
    )


