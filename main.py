"""main.py - Entry point utama sistem toko-ai-agent

Fungsi:
- Menu CLI utama
- Audit stok
- Pembukuan
- Laporan
- Backup
- AI agent
"""

import sys
from typing import Optional

from core.audit import (
    tambah_barang,
    tambah_audit,
    lihat_audit_hari_ini,
)

from core.pembukuan import (
    tambah_pendapatan_harian,
    tambah_biaya,
    hitung_laba_harian,
)

from backup.auto_backup import backup_all

from laporan import (
    laporan_harian,
    laporan_bulanan,
    laporan_stok_hari_ini,
)

from ai.agent import tanya_ai


# =========================================================
# UTIL INPUT
# =========================================================

def input_float(prompt: str) -> Optional[float]:
    """Input float dengan validasi"""
    try:
        value = input(prompt).strip()
        if not value:
            print("Input tidak boleh kosong")
            return None
        number = float(value)
        if number < 0:
            print("Nilai tidak boleh negatif")
            return None
        return number
    except ValueError:
        print("Input harus berupa angka")
        return None
    except Exception as exc:
        print(f"[ERROR] Gagal membaca input: {exc}")
        return None


def input_string(prompt: str) -> Optional[str]:
    """Input string dengan validasi"""
    try:
        value = input(prompt).strip()
        if not value:
            print("Input tidak boleh kosong")
            return None
        return value
    except Exception as exc:
        print(f"[ERROR] Gagal membaca input: {exc}")
        return None


# =========================================================
# MENU
# =========================================================

def menu() -> None:
    print()
    print("======================================")
    print("       SISTEM TOKO AI AGENT          ")
    print("======================================")
    print("1. Tambah Barang")
    print("2. Audit Stok Hari Ini")
    print("3. Lihat Audit Hari Ini")
    print("4. Input Pendapatan Harian")
    print("5. Input Biaya")
    print("6. Lihat Laba Hari Ini")
    print("7. Backup Sekarang")
    print("8. Laporan Harian")
    print("9. Laporan Bulanan")
    print("10. Laporan Stok Hari Ini")
    print("11. Tanya AI")
    print("0. Keluar")
    print("======================================")


# =========================================================
# HANDLER
# =========================================================

def handle_tambah_barang():
    try:
        nama = input_string("Nama barang : ")
        if nama is None:
            return
        satuan = input_string("Satuan (kg/liter/pcs) : ")
        if satuan is None:
            return
        tambah_barang(nama=nama, satuan=satuan)
    except Exception as exc:
        print(f"[ERROR] Gagal menambah barang: {exc}")


def handle_audit():
    try:
        nama = input_string("Nama barang : ")
        if nama is None:
            return
        masuk = input_float("Stok masuk : ")
        if masuk is None:
            return
        keluar = input_float("Stok keluar : ")
        if keluar is None:
            return
        catatan = input("Catatan (opsional) : ")
        tambah_audit(
            nama_barang=nama,
            stok_masuk=masuk,
            stok_keluar=keluar,
            catatan=catatan,
        )
    except Exception as exc:
        print(f"[ERROR] Gagal input audit: {exc}")


def handle_pendapatan():
    try:
        jumlah = input_float("Pendapatan hari ini : ")
        if jumlah is None:
            return
        tambah_pendapatan_harian(jumlah=jumlah)
    except Exception as exc:
        print(f"[ERROR] Gagal input pendapatan: {exc}")


def handle_biaya():
    try:
        nama = input_string("Nama biaya : ")
        if nama is None:
            return
        jumlah = input_float("Jumlah biaya : ")
        if jumlah is None:
            return
        tambah_biaya(nama=nama, jumlah=jumlah)
    except Exception as exc:
        print(f"[ERROR] Gagal input biaya: {exc}")


def handle_backup():
    try:
        backup_all()
    except Exception as exc:
        print(f"[ERROR] Backup gagal: {exc}")


def handle_tanya_ai():
    try:
        pertanyaan = input_string("Tanya AI : ")
        if pertanyaan is None:
            return
        tanya_ai(pertanyaan=pertanyaan)
    except Exception as exc:
        print(f"[ERROR] Gagal menjalankan AI: {exc}")


# =========================================================
# MAIN LOOP
# =========================================================

def main():
    try:
        while True:
            menu()
            choice = input("Pilih menu : ").strip()
            if choice == "1":
                handle_tambah_barang()
            elif choice == "2":
                handle_audit()
            elif choice == "3":
                lihat_audit_hari_ini()
            elif choice == "4":
                handle_pendapatan()
            elif choice == "5":
                handle_biaya()
            elif choice == "6":
                hitung_laba_harian()
            elif choice == "7":
                handle_backup()
            elif choice == "8":
                laporan_harian()
            elif choice == "9":
                laporan_bulanan()
            elif choice == "10":
                laporan_stok_hari_ini()
            elif choice == "11":
                handle_tanya_ai()
            elif choice == "0":
                print("Keluar dari sistem")
                sys.exit(0)
            else:
                print("Menu tidak valid")
    except KeyboardInterrupt:
        print()
        print("Program dihentikan user")
    except Exception as exc:
        print(f"[ERROR] Sistem crash: {exc}")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()