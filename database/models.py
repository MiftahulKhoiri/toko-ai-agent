"""database/models.py - Schema tabel database toko-ai-agent"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Text,
)
from datetime import datetime

from .db import Base


# =========================================================
# TABEL BARANG
# =========================================================
class Barang(Base):
    __tablename__ = "barang"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, unique=True, nullable=False)
    satuan = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# =========================================================
# TABEL AUDIT STOK
# =========================================================
class StokAudit(Base):
    __tablename__ = "stok_audit"

    id = Column(Integer, primary_key=True, index=True)
    barang_id = Column(Integer, nullable=False)
    tanggal = Column(Date, nullable=False)
    stok_awal = Column(Float, default=0)
    stok_masuk = Column(Float, default=0)
    stok_keluar = Column(Float, default=0)
    stok_akhir = Column(Float, default=0)
    catatan = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


# =========================================================
# TABEL TRANSAKSI (Pendapatan)
# =========================================================
class Transaksi(Base):
    __tablename__ = "transaksi"

    id = Column(Integer, primary_key=True, index=True)
    tanggal = Column(Date, nullable=False)
    pendapatan = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# =========================================================
# TABEL BIAYA
# =========================================================
class Biaya(Base):
    __tablename__ = "biaya"

    id = Column(Integer, primary_key=True, index=True)
    tanggal = Column(Date, nullable=False)
    nama = Column(String, nullable=False)
    jumlah = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# =========================================================
# TABEL BACKUP LOG
# =========================================================
class BackupLog(Base):
    __tablename__ = "backup_log"

    id = Column(Integer, primary_key=True, index=True)
    waktu = Column(DateTime, default=datetime.now)
    file_backup = Column(String)
    status = Column(String)
    catatan = Column(Text)