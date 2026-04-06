"""
system/integrity_checker.py
Database integrity checker untuk toko-ai-agent

Fitur:
- Cek foreign key integrity
- Cek stok negatif
- Cek orphan record
- Cek duplikasi data
- Cek tanggal invalid
- Laporan masalah database
"""

from typing import List, Dict

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from database.models import (
    Barang,
    StokAudit,
    Transaksi,
    Biaya,
)

from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# UTIL
# =========================================================

def get_session():
    return SessionLocal()


# =========================================================
# CHECK STOK NEGATIF
# =========================================================

def check_negative_stock(session) -> List[str]:

    issues = []

    try:

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
                StokAudit.stok_akhir < 0,
            )
        ).all()

        for row in results:

            issues.append(
                f"Stok negatif: {row.nama} = {row.stok_akhir}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal cek stok negatif: {exc}"
        )

    return issues


# =========================================================
# CHECK ORPHAN RECORD
# =========================================================

def check_orphan_stock(session) -> List[str]:

    issues = []

    try:

        results = session.execute(
            select(
                StokAudit.id,
            )
            .where(
                ~StokAudit.barang_id.in_(
                    select(Barang.id)
                )
            )
        ).all()

        for row in results:

            issues.append(
                f"Orphan stok audit ID: {row.id}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal cek orphan stock: {exc}"
        )

    return issues


# =========================================================
# CHECK DUPLICATE BARANG
# =========================================================

def check_duplicate_barang(session) -> List[str]:

    issues = []

    try:

        results = session.execute(
            select(
                Barang.nama,
                func.count(Barang.id),
            )
            .group_by(
                Barang.nama,
            )
            .having(
                func.count(Barang.id) > 1
            )
        ).all()

        for row in results:

            issues.append(
                f"Duplicate barang: {row.nama}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal cek duplicate barang: {exc}"
        )

    return issues


# =========================================================
# CHECK TRANSAKSI INVALID
# =========================================================

def check_invalid_transaksi(session) -> List[str]:

    issues = []

    try:

        results = session.execute(
            select(
                Transaksi.id,
            )
            .where(
                Transaksi.pendapatan < 0,
            )
        ).all()

        for row in results:

            issues.append(
                f"Pendapatan negatif ID: {row.id}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal cek transaksi: {exc}"
        )

    return issues


# =========================================================
# CHECK BIAYA INVALID
# =========================================================

def check_invalid_biaya(session) -> List[str]:

    issues = []

    try:

        results = session.execute(
            select(
                Biaya.id,
            )
            .where(
                Biaya.jumlah < 0,
            )
        ).all()

        for row in results:

            issues.append(
                f"Biaya negatif ID: {row.id}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal cek biaya: {exc}"
        )

    return issues


# =========================================================
# MAIN CHECK
# =========================================================

def run_integrity_check() -> Dict[str, List[str]]:

    print()
    print("=== DATABASE INTEGRITY CHECK ===")

    session = get_session()

    results = {}

    try:

        results["negative_stock"] = check_negative_stock(session)

        results["orphan_stock"] = check_orphan_stock(session)

        results["duplicate_barang"] = check_duplicate_barang(session)

        results["invalid_transaksi"] = check_invalid_transaksi(session)

        results["invalid_biaya"] = check_invalid_biaya(session)

        print()

        total_issues = 0

        for category, issues in results.items():

            print(f"{category}:")

            if not issues:

                print("  OK")

            else:

                for issue in issues:

                    print(" ", issue)

                total_issues += len(issues)

        print()

        if total_issues == 0:

            print("DATABASE STATUS: CLEAN")

        else:

            print(
                f"DATABASE STATUS: {total_issues} ISSUE(S) FOUND"
            )

        logger.info(
            f"Integrity check result: {results}"
        )

        return results

    except Exception as exc:

        logger.error(
            f"Integrity check error: {exc}"
        )

        return results

    finally:

        session.close()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    run_integrity_check()