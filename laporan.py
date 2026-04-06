"""laporan.py - Modul laporan untuk toko-ai-agent

Fungsi:
- Laporan harian
- Laporan bulanan
- Ringkasan pendapatan
- Ringkasan biaya
- Perhitungan laba
- Ringkasan audit stok
"""

from datetime import datetime, date
from typing import Tuple

from sqlalchemy import select, func, extract
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from database.models import (
    Transaksi,
    Biaya,
    Barang,
    StokAudit,
)

from config import TODAY


# =========================================================
# UTIL
# =========================================================

def get_session():
    """Membuat session database"""
    return SessionLocal()


def get_tanggal() -> date:
    """Ambil tanggal hari ini"""
    return datetime.strptime(TODAY, "%Y-%m-%d").date()


# =========================================================
# HITUNG TOTAL
# =========================================================

def hitung_total_harian() -> Tuple[float, float, float]:
    """Hitung total pendapatan, biaya, dan laba hari ini"""
    session = get_session()
    try:
        tanggal = get_tanggal()
        pendapatan = session.execute(
            select(func.sum(Transaksi.pendapatan))
            .where(Transaksi.tanggal == tanggal)
        ).scalar()
        biaya = session.execute(
            select(func.sum(Biaya.jumlah))
            .where(Biaya.tanggal == tanggal)
        ).scalar()
        total_pendapatan = float(pendapatan or 0)
        total_biaya = float(biaya or 0)
        laba = total_pendapatan - total_biaya
        return (total_pendapatan, total_biaya, laba)
    except SQLAlchemyError as exc:
        print(f"[ERROR] Gagal menghitung total harian: {exc}")
        return (0.0, 0.0, 0.0)
    finally:
        session.close()


# =========================================================
# LAPORAN HARIAN
# =========================================================

def laporan_harian() -> None:
    """Tampilkan laporan keuangan hari ini"""
    try:
        tanggal = get_tanggal()
        pendapatan, biaya, laba = hitung_total_harian()
        print()
        print("======================================")
        print("          LAPORAN HARIAN             ")
        print("======================================")
        print(f"Tanggal      : {tanggal}")
        print("--------------------------------------")
        print(f"Pendapatan   : Rp {pendapatan:,.0f}")
        print(f"Biaya        : Rp {biaya:,.0f}")
        print(f"Laba         : Rp {laba:,.0f}")
        print("======================================")
    except Exception as exc:
        print(f"[ERROR] Gagal menampilkan laporan harian: {exc}")


# =========================================================
# LAPORAN BULANAN
# =========================================================

def laporan_bulanan() -> None:
    """Tampilkan laporan keuangan bulan ini"""
    session = get_session()
    try:
        tanggal = get_tanggal()
        bulan = tanggal.month
        tahun = tanggal.year
        pendapatan = session.execute(
            select(func.sum(Transaksi.pendapatan))
            .where(
                extract("month", Transaksi.tanggal) == bulan,
                extract("year", Transaksi.tanggal) == tahun,
            )
        ).scalar()
        biaya = session.execute(
            select(func.sum(Biaya.jumlah))
            .where(
                extract("month", Biaya.tanggal) == bulan,
                extract("year", Biaya.tanggal) == tahun,
            )
        ).scalar()
        total_pendapatan = float(pendapatan or 0)
        total_biaya = float(biaya or 0)
        laba = total_pendapatan - total_biaya
        print()
        print("======================================")
        print("          LAPORAN BULANAN            ")
        print("======================================")
        print(f"Bulan        : {bulan}")
        print(f"Tahun        : {tahun}")
        print("--------------------------------------")
        print(f"Pendapatan   : Rp {total_pendapatan:,.0f}")
        print(f"Biaya        : Rp {total_biaya:,.0f}")
        print(f"Laba         : Rp {laba:,.0f}")
        print("======================================")
    except SQLAlchemyError as exc:
        print(f"[ERROR] Gagal mengambil laporan bulanan: {exc}")
    finally:
        session.close()


# =========================================================
# LAPORAN STOK
# =========================================================

def laporan_stok_hari_ini() -> None:
    """Tampilkan ringkasan stok hari ini"""
    session = get_session()
    try:
        tanggal = get_tanggal()
        results = session.execute(
            select(
                Barang.nama,
                StokAudit.stok_awal,
                StokAudit.stok_masuk,
                StokAudit.stok_keluar,
                StokAudit.stok_akhir,
            )
            .join(Barang, Barang.id == StokAudit.barang_id)
            .where(StokAudit.tanggal == tanggal)
        ).all()
        print()
        print("======================================")
        print("       LAPORAN STOK HARI INI         ")
        print("======================================")
        print(f"Tanggal      : {tanggal}")
        print("--------------------------------------")
        if not results:
            print("Belum ada data stok")
            return
        for row in results:
            print(
                f"{row.nama:15} | "
                f"awal: {row.stok_awal:6.2f} | "
                f"masuk: {row.stok_masuk:6.2f} | "
                f"keluar: {row.stok_keluar:6.2f} | "
                f"akhir: {row.stok_akhir:6.2f}"
            )
        print("======================================")
    except SQLAlchemyError as exc:
        print(f"[ERROR] Gagal mengambil laporan stok: {exc}")
    finally:
        session.close()


# =========================================================
# TEST MANUAL
# =========================================================

if __name__ == "__main__":
    print("TEST LAPORAN")
    laporan_harian()
    laporan_bulanan()
    laporan_stok_hari_ini()