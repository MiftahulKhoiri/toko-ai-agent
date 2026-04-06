"""core/pembukuan.py - Modul pembukuan harian untuk toko-ai-agent
Menangani pendapatan, biaya, dan perhitungan laba
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from database.models import Transaksi, Biaya
from config import TODAY


# =========================================================
# UTIL
# =========================================================

def get_session():
    """Membuat session database"""
    return SessionLocal()


def get_tanggal() -> date:
    """Ambil tanggal hari ini dari config"""
    return datetime.strptime(TODAY, "%Y-%m-%d").date()


def validasi_jumlah(jumlah: float) -> bool:
    """Validasi jumlah uang"""
    if jumlah is None:
        print("Error: Jumlah tidak boleh kosong")
        return False
    if jumlah < 0:
        print("Error: Jumlah tidak boleh negatif")
        return False
    return True


# =========================================================
# PENDAPATAN
# =========================================================

def tambah_pendapatan_harian(jumlah: float) -> None:
    """Tambah atau update pendapatan harian. Hanya 1 data per hari"""
    if not validasi_jumlah(jumlah):
        return

    session = get_session()
    try:
        tanggal = get_tanggal()
        existing = session.execute(
            select(Transaksi).where(Transaksi.tanggal == tanggal)
        ).scalar_one_or_none()

        if existing:
            existing.pendapatan = jumlah
            print("Pendapatan hari ini diperbarui")
        else:
            transaksi = Transaksi(tanggal=tanggal, pendapatan=jumlah)
            session.add(transaksi)
            print("Pendapatan hari ini disimpan")

        session.commit()
        print(f"Tanggal     : {tanggal}")
        print(f"Pendapatan  : Rp {jumlah:,.0f}")
    except SQLAlchemyError as exc:
        session.rollback()
        print(f"[ERROR] Gagal menyimpan pendapatan: {exc}")
    finally:
        session.close()


# =========================================================
# BIAYA
# =========================================================

def tambah_biaya(nama: str, jumlah: float) -> None:
    """Tambah biaya harian. Contoh: Gas, Listrik, Bahan, dll"""
    if not nama:
        print("Error: Nama biaya tidak boleh kosong")
        return
    if not validasi_jumlah(jumlah):
        return

    session = get_session()
    try:
        tanggal = get_tanggal()
        biaya = Biaya(tanggal=tanggal, nama=nama, jumlah=jumlah)
        session.add(biaya)
        session.commit()
        print("Biaya berhasil disimpan")
        print(f"Tanggal : {tanggal}")
        print(f"Nama    : {nama}")
        print(f"Jumlah  : Rp {jumlah:,.0f}")
    except SQLAlchemyError as exc:
        session.rollback()
        print(f"[ERROR] Gagal menyimpan biaya: {exc}")
    finally:
        session.close()


# =========================================================
# TOTAL PENDAPATAN
# =========================================================

def total_pendapatan_harian() -> float:
    """Hitung total pendapatan hari ini"""
    session = get_session()
    try:
        tanggal = get_tanggal()
        total = session.execute(
            select(func.sum(Transaksi.pendapatan)).where(Transaksi.tanggal == tanggal)
        ).scalar()
        return float(total or 0)
    except SQLAlchemyError as exc:
        print(f"[ERROR] Gagal mengambil pendapatan: {exc}")
        return 0.0
    finally:
        session.close()


# =========================================================
# TOTAL BIAYA
# =========================================================

def total_biaya_harian() -> float:
    """Hitung total biaya hari ini"""
    session = get_session()
    try:
        tanggal = get_tanggal()
        total = session.execute(
            select(func.sum(Biaya.jumlah)).where(Biaya.tanggal == tanggal)
        ).scalar()
        return float(total or 0)
    except SQLAlchemyError as exc:
        print(f"[ERROR] Gagal mengambil biaya: {exc}")
        return 0.0
    finally:
        session.close()


# =========================================================
# HITUNG LABA
# =========================================================

def hitung_laba_harian() -> float:
    """Hitung laba hari ini. Laba = Pendapatan - Biaya"""
    try:
        pendapatan = total_pendapatan_harian()
        biaya = total_biaya_harian()
        laba = pendapatan - biaya
        print("Ringkasan Keuangan Hari Ini")
        print("-" * 40)
        print(f"Pendapatan : Rp {pendapatan:,.0f}")
        print(f"Biaya      : Rp {biaya:,.0f}")
        print(f"Laba       : Rp {laba:,.0f}")
        return laba
    except Exception as exc:
        print(f"[ERROR] Gagal menghitung laba: {exc}")
        return 0.0


# =========================================================
# LIHAT BIAYA HARI INI
# =========================================================

def lihat_biaya_hari_ini() -> None:
    """Tampilkan daftar biaya hari ini"""
    session = get_session()
    try:
        tanggal = get_tanggal()
        results = session.execute(
            select(Biaya.nama, Biaya.jumlah).where(Biaya.tanggal == tanggal)
        ).all()

        print(f"Biaya tanggal: {tanggal}")
        print("-" * 40)
        if not results:
            print("Belum ada biaya")
            return

        total = 0.0
        for row in results:
            print(f"{row.nama:15} | Rp {row.jumlah:,.0f}")
            total += row.jumlah
        print("-" * 40)
        print(f"Total Biaya : Rp {total:,.0f}")
    except SQLAlchemyError as exc:
        print(f"[ERROR] Gagal mengambil data biaya: {exc}")
    finally:
        session.close()


# =========================================================
# TEST MANUAL
# =========================================================

if __name__ == "__main__":
    print("TEST PEMBUKUAN")
    tambah_pendapatan_harian(450000)
    tambah_biaya("Gas", 50000)
    tambah_biaya("Listrik", 30000)
    hitung_laba_harian()