"""
system/auto_repair.py
Auto repair database ringan untuk toko-ai-agent

Fitur:
- Hapus orphan record
- Perbaiki stok negatif
- Normalisasi data invalid
- Logging setiap perubahan
- Aman untuk production
"""

from typing import Dict, List

from sqlalchemy import select
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
# FIX STOK NEGATIF
# =========================================================

def fix_negative_stock(session) -> List[str]:

    actions = []

    try:

        results = session.execute(
            select(StokAudit)
            .where(StokAudit.stok_akhir < 0)
        ).scalars().all()

        for record in results:

            logger.warning(
                f"Memperbaiki stok negatif ID={record.id}"
            )

            record.stok_akhir = 0

            actions.append(
                f"Fixed stok negatif ID={record.id}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal memperbaiki stok negatif: {exc}"
        )

    return actions


# =========================================================
# REMOVE ORPHAN STOCK
# =========================================================

def remove_orphan_stock(session) -> List[str]:

    actions = []

    try:

        valid_ids = session.execute(
            select(Barang.id)
        ).scalars().all()

        results = session.execute(
            select(StokAudit)
            .where(~StokAudit.barang_id.in_(valid_ids))
        ).scalars().all()

        for record in results:

            logger.warning(
                f"Menghapus orphan stok ID={record.id}"
            )

            session.delete(record)

            actions.append(
                f"Deleted orphan stok ID={record.id}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal hapus orphan stok: {exc}"
        )

    return actions


# =========================================================
# FIX TRANSAKSI NEGATIF
# =========================================================

def fix_negative_transaksi(session) -> List[str]:

    actions = []

    try:

        results = session.execute(
            select(Transaksi)
            .where(Transaksi.pendapatan < 0)
        ).scalars().all()

        for record in results:

            logger.warning(
                f"Memperbaiki transaksi negatif ID={record.id}"
            )

            record.pendapatan = 0

            actions.append(
                f"Fixed transaksi negatif ID={record.id}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal memperbaiki transaksi: {exc}"
        )

    return actions


# =========================================================
# FIX BIAYA NEGATIF
# =========================================================

def fix_negative_biaya(session) -> List[str]:

    actions = []

    try:

        results = session.execute(
            select(Biaya)
            .where(Biaya.jumlah < 0)
        ).scalars().all()

        for record in results:

            logger.warning(
                f"Memperbaiki biaya negatif ID={record.id}"
            )

            record.jumlah = 0

            actions.append(
                f"Fixed biaya negatif ID={record.id}"
            )

    except SQLAlchemyError as exc:

        logger.error(
            f"Gagal memperbaiki biaya: {exc}"
        )

    return actions


# =========================================================
# MAIN REPAIR
# =========================================================

def run_auto_repair() -> Dict[str, List[str]]:

    print()
    print("=== AUTO REPAIR DATABASE ===")

    session = get_session()

    results = {}

    try:

        results["fix_negative_stock"] = fix_negative_stock(session)

        results["remove_orphan_stock"] = remove_orphan_stock(session)

        results["fix_negative_transaksi"] = fix_negative_transaksi(session)

        results["fix_negative_biaya"] = fix_negative_biaya(session)

        session.commit()

        print()

        total_actions = 0

        for category, actions in results.items():

            print(f"{category}:")

            if not actions:

                print("  Tidak ada perubahan")

            else:

                for action in actions:

                    print(" ", action)

                total_actions += len(actions)

        print()

        if total_actions == 0:

            print("DATABASE STATUS: TIDAK PERLU PERBAIKAN")

        else:

            print(
                f"DATABASE STATUS: {total_actions} PERBAIKAN DILAKUKAN"
            )

        logger.info(
            f"Auto repair result: {results}"
        )

        return results

    except Exception as exc:

        session.rollback()

        logger.error(
            f"Auto repair error: {exc}"
        )

        return results

    finally:

        session.close()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    run_auto_repair()