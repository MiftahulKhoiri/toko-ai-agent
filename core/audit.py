"""core/audit.py - Modul audit stok harian untuk toko-ai-agent"""

from datetime import datetime
from sqlalchemy import select

from database.db import SessionLocal
from database.models import Barang, StokAudit
from config import TODAY, SATUAN_VALID


# ========================================================= UTIL =========================================================

def get_session():
    return SessionLocal()


def get_tanggal():
    return datetime.strptime(TODAY, "%Y-%m-%d").date()


# ========================================================= BARANG =========================================================

def tambah_barang(nama: str, satuan: str):
    """Tambah barang baru"""
    if satuan not in SATUAN_VALID:
        print("Satuan tidak valid")
        return

    session = get_session()
    try:
        existing = session.execute(
            select(Barang).where(Barang.nama == nama)
        ).scalar_one_or_none()
        if existing:
            print("Barang sudah ada")
            return

        barang = Barang(nama=nama, satuan=satuan)
        session.add(barang)
        session.commit()
        print("Barang berhasil ditambahkan")
    finally:
        session.close()


# ========================================================= STOK TERAKHIR =========================================================

def get_stok_terakhir(barang_id: int) -> float:
    """Ambil stok akhir terakhir dari suatu barang"""
    session = get_session()
    try:
        result = session.execute(
            select(StokAudit)
            .where(StokAudit.barang_id == barang_id)
            .order_by(StokAudit.tanggal.desc())
        ).scalars().first()
        return result.stok_akhir if result else 0.0
    finally:
        session.close()


# ========================================================= TAMBAH AUDIT =========================================================

def tambah_audit(nama_barang: str, stok_masuk: float, stok_keluar: float, catatan: str = ""):
    """Tambah audit stok harian"""
    session = get_session()
    try:
        barang = session.execute(
            select(Barang).where(Barang.nama == nama_barang)
        ).scalar_one_or_none()
        if not barang:
            print("Barang tidak ditemukan")
            return

        stok_awal = get_stok_terakhir(barang.id)
        stok_akhir = stok_awal + stok_masuk - stok_keluar

        if stok_akhir < 0:
            print(f"Error: Stok akhir negatif ({stok_akhir:.2f}). Tidak dapat menyimpan audit.")
            return

        audit = StokAudit(
            barang_id=barang.id,
            tanggal=get_tanggal(),
            stok_awal=stok_awal,
            stok_masuk=stok_masuk,
            stok_keluar=stok_keluar,
            stok_akhir=stok_akhir,
            catatan=catatan
        )
        session.add(audit)
        session.commit()
        print("Audit berhasil disimpan")
        print(f"Stok awal : {stok_awal:.2f}")
        print(f"Stok akhir: {stok_akhir:.2f}")
    finally:
        session.close()


# ========================================================= LIHAT AUDIT HARI INI =========================================================

def lihat_audit_hari_ini():
    """Tampilkan semua audit untuk hari ini"""
    session = get_session()
    try:
        tanggal = get_tanggal()
        results = session.execute(
            select(
                Barang.nama,
                StokAudit.stok_awal,
                StokAudit.stok_masuk,
                StokAudit.stok_keluar,
                StokAudit.stok_akhir
            )
            .join(Barang, Barang.id == StokAudit.barang_id)
            .where(StokAudit.tanggal == tanggal)
        ).all()

        print(f"Audit tanggal: {tanggal}")
        print("-" * 50)
        if not results:
            print("Belum ada data")
            return

        for row in results:
            print(
                f"{row.nama:15} | "
                f"awal: {row.stok_awal:6.2f} | "
                f"masuk: {row.stok_masuk:6.2f} | "
                f"keluar: {row.stok_keluar:6.2f} | "
                f"akhir: {row.stok_akhir:6.2f}"
            )
    finally:
        session.close()


# ========================================================= TEST MANUAL =========================================================

if __name__ == "__main__":
    # contoh penggunaan
    tambah_barang("Bahan Salom", "kg")
    tambah_audit(
        nama_barang="Bahan Salom",
        stok_masuk=5,
        stok_keluar=2,
        catatan="Pembelian pagi"
    )
    lihat_audit_hari_ini()