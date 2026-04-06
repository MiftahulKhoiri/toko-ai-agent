"""main.py - Entry point utama sistem toko-ai-agent

Fitur:
- Login user
- Role admin / kasir
- Session user
- Menu berbasis role
"""

import sys
from typing import Optional

from startup.startup_tasks import run_startup_tasks

from core.user_manager import (
    login_user,
    create_default_admin,
    require_admin,
)

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

from export.export_excel import (
    export_laporan_harian,
    export_laporan_bulanan,
    export_laporan_stok,
)


# =========================================================
# SESSION
# =========================================================
CURRENT_ROLE: Optional[str] = None


# =========================================================
# INPUT UTIL
# =========================================================
def input_string(prompt: str) -> Optional[str]:
    try:
        value = input(prompt).strip()
        if not value:
            print("Input tidak boleh kosong")
            return None
        return value
    except Exception as exc:
        print(f"[ERROR] Input gagal: {exc}")
        return None


def input_float(prompt: str) -> Optional[float]:
    try:
        value = input(prompt).strip()
        if not value:
            print("Input kosong")
            return None
        number = float(value)
        if number < 0:
            print("Nilai tidak boleh negatif")
            return None
        return number
    except ValueError:
        print("Harus angka")
        return None
    except Exception as exc:
        print(f"[ERROR] Input gagal: {exc}")
        return None


# =========================================================
# LOGIN
# =========================================================
def login() -> bool:
    global CURRENT_ROLE
    try:
        print()
        print("===================================")
        print("        LOGIN SISTEM              ")
        print("===================================")
        username = input_string("Username : ")
        if username is None:
            return False
        password = input_string("Password : ")
        if password is None:
            return False
        role = login_user(username=username, password=password)
        if role:
            CURRENT_ROLE = role
            return True
        return False
    except Exception as exc:
        print(f"[ERROR] Login gagal: {exc}")
        return False


# =========================================================
# MENU
# =========================================================
def menu() -> None:
    print()
    print("======================================")
    print(f"        ROLE: {CURRENT_ROLE}          ")
    print("======================================")
    print("1. Tambah Barang (admin)")
    print("2. Audit Stok")
    print("3. Lihat Audit")
    print("4. Input Pendapatan")
    print("5. Input Biaya")
    print("6. Lihat Laba")
    print("7. Backup (admin)")
    print("8. Laporan Harian")
    print("9. Laporan Bulanan")
    print("10. Laporan Stok")
    print("11. Tanya AI")
    print("12. Export Harian")
    print("13. Export Bulanan")
    print("14. Export Stok")
    print("15. Logout")
    print("0. Keluar")
    print("======================================")


# =========================================================
# MAIN LOOP
# =========================================================
def main() -> None:
    global CURRENT_ROLE
    try:
        run_startup_tasks()
        create_default_admin()

        while True:
            if not CURRENT_ROLE:
                if not login():
                    continue

            menu()
            choice = input("Pilih menu : ").strip()

            # ADMIN ONLY
            if choice == "1":
                if not require_admin(CURRENT_ROLE):
                    continue
                nama = input_string("Nama barang : ")
                if nama is None:
                    continue
                satuan = input_string("Satuan : ")
                if satuan is None:
                    continue
                tambah_barang(nama=nama, satuan=satuan)

            elif choice == "2":
                nama = input_string("Nama barang : ")
                if nama is None:
                    continue
                masuk = input_float("Stok masuk : ")
                if masuk is None:
                    continue
                keluar = input_float("Stok keluar : ")
                if keluar is None:
                    continue
                catatan = input("Catatan : ")
                tambah_audit(
                    nama_barang=nama,
                    stok_masuk=masuk,
                    stok_keluar=keluar,
                    catatan=catatan,
                )

            elif choice == "3":
                lihat_audit_hari_ini()

            elif choice == "4":
                jumlah = input_float("Pendapatan : ")
                if jumlah is None:
                    continue
                tambah_pendapatan_harian(jumlah=jumlah)

            elif choice == "5":
                nama = input_string("Nama biaya : ")
                if nama is None:
                    continue
                jumlah = input_float("Jumlah biaya : ")
                if jumlah is None:
                    continue
                tambah_biaya(nama=nama, jumlah=jumlah)

            elif choice == "6":
                hitung_laba_harian()

            elif choice == "7":
                if not require_admin(CURRENT_ROLE):
                    continue
                backup_all()

            elif choice == "8":
                laporan_harian()

            elif choice == "9":
                laporan_bulanan()

            elif choice == "10":
                laporan_stok_hari_ini()

            elif choice == "11":
                pertanyaan = input_string("Tanya AI : ")
                if pertanyaan is None:
                    continue
                tanya_ai(pertanyaan=pertanyaan)

            elif choice == "12":
                export_laporan_harian()

            elif choice == "13":
                export_laporan_bulanan()

            elif choice == "14":
                export_laporan_stok()

            elif choice == "15":
                print("Logout")
                CURRENT_ROLE = None

            elif choice == "0":
                print("Keluar sistem")
                sys.exit(0)

            else:
                print("Menu tidak valid")

    except KeyboardInterrupt:
        print()
        print("Program dihentikan")
    except Exception as exc:
        print(f"[ERROR] Sistem crash: {exc}")


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    main()