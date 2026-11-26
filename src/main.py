import sys
import questionary
from core.utils import clear_screen, pause_screen
from auth.auth import login
from admin.admin import menu_admin
from kasir.kasir import menu_kasir

def main_menu():
    while True:
        clear_screen()
        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "KANOPI - POS KEDAI KULINER".center(box_width) + "|")
        print("|" + "Sistem Kasir & Inventori Kedai UMKM".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        selected_option = questionary.select(
            "Silakan pilih opsi masuk:",
            choices=[
                "1. Masuk sebagai Kasir / Karyawan",
                "2. Masuk sebagai Pemilik Kedai (Admin)",
                "0. Keluar Aplikasi"
            ]
        ).ask()

        if selected_option is None or selected_option.startswith("0"):
            print("\n[INFO] Terima kasih telah menggunakan KANOPI POS Kedai. Sampai jumpa.")
            sys.exit()
        elif selected_option.startswith("1"):
            user_session = login()
            if user_session:
                user_role = user_session.get('role')
                if user_role == 'kasir':
                    print("\n[INFO] Akun ini adalah Kasir. Mengalihkan ke menu Kasir...")
                    pause_screen()
                    menu_kasir(user_session)
                else:
                    print("\n[ERROR] Role pengguna tidak valid.")
                    pause_screen()
        elif selected_option.startswith("2"):
            user_session = login()
            if user_session:
                user_role = user_session.get('role')
                if user_role == 'admin':
                    print("\n[INFO] Akun ini adalah Pemilik/Admin. Mengalihkan ke menu Admin...")
                    pause_screen()
                    menu_admin(user_session)
                else:
                    print("\n[ERROR] Role pengguna tidak valid.")
                    pause_screen()

if __name__ == "__main__":
    main_menu()
