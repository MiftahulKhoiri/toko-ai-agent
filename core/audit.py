""" core/audit.py Modul audit stok harian untuk toko-ai-agent """

from datetime import datetime from sqlalchemy import select

from database.db import SessionLocal from database.models import Barang, StokAudit from config import TODAY, SATUAN_VALID

========================================================= UTIL ========================================================= 

def get_session(): return SessionLocal()

def get_tanggal(): return datetime.strptime(TODAY, "%Y-%m-%d").date()

========================================================= BARANG ========================================================= 

def tambah_barang(nama: str, satuan: str): """ Tambah barang baru """

if satuan not in SATUAN_VALID: print("Satuan tidak valid") return session = get_session() try: existing = session.execute( select(Barang).where( Barang.nama == nama ) ).scalar_one_or_none() if existing: print("Barang sudah ada") return barang = Barang( nama=nama, satuan=satuan ) session.add(barang) session.commit() print("Barang berhasil ditambahkan") finally: session.close() ========================================================= STOK TERAKHIR ========================================================= 

def get_stok_terakhir(barang_id: int):

session = get_session() try: result = session.execute( select(StokAudit) .where( StokAudit.barang_id == barang_id ) .order_by( StokAudit.tanggal.desc() ) ).scalars().first() if result: return result.stok_akhir return 0 finally: session.close() ========================================================= TAMBAH AUDIT ========================================================= 

def tambah_audit( nama_barang: str, stok_masuk: float, stok_keluar: float, catatan: str = "" ): """ Tambah audit stok harian """

session = get_session() try: barang = session.execute( select(Barang).where( Barang.nama == nama_barang ) ).scalar_one_or_none() if not barang: print("Barang tidak ditemukan") return stok_awal = get_stok_terakhir(barang.id) stok_akhir = ( stok_awal + stok_masuk - stok_keluar ) audit = StokAudit( barang_id=barang.id, tanggal=get_tanggal(), stok_awal=stok_awal, stok_masuk=stok_masuk, stok_keluar=stok_keluar, stok_akhir=stok_akhir, catatan=catatan ) session.add(audit) session.commit() print("Audit berhasil disimpan") print("Stok awal :", stok_awal) print("Stok akhir:", stok_akhir) finally: session.close() ========================================================= LIHAT AUDIT HARI INI ========================================================= 

def lihat_audit_hari_ini():

session = get_session() try: tanggal = get_tanggal() results = session.execute( select( Barang.nama, StokAudit.stok_awal, StokAudit.stok_masuk, StokAudit.stok_keluar, StokAudit.stok_akhir ) .join( Barang, Barang.id == StokAudit.barang_id ) .where( StokAudit.tanggal == tanggal ) ).all() print("Audit tanggal:", tanggal) print("-" * 40) if not results: print("Belum ada data") return for row in results: print( row.nama, "| awal:", row.stok_awal, "| masuk:", row.stok_masuk, "| keluar:", row.stok_keluar, "| akhir:", row.stok_akhir ) finally: session.close() ========================================================= TEST MANUAL ========================================================= 

if name == "main":

# contoh penggunaan tambah_barang("Bahan Salom", "kg") tambah_audit( nama_barang="Bahan Salom", stok_masuk=5, stok_keluar=2, catatan="Pembelian pagi" ) lihat_audit_hari_ini() 