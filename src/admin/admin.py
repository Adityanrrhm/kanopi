import questionary
from core.utils import (
    clear_screen,
    pause_screen
)
from core.database import (
    load_menu,
    load_users,
    load_orders
)
from auth.auth import change_password
from admin.catalog import manage_menu_catalog
from admin.cashiers import manage_cashiers
from admin.reports import manage_reports

def menu_admin(user_session=None):
    admin_name = user_session['nama'] if user_session and user_session.get('nama') else "Admin"
    while True:
        clear_screen()
        menu_count   = len(load_menu())
        users_df     = load_users()
        cashier_count = len(users_df[users_df['role'] == 'kasir'])
        order_count  = len(load_orders())

        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "ADMIN / PEMILIK KEDAI".center(box_width) + "|")
        print("|" + f" Selamat Bertugas: {admin_name}".ljust(box_width) + "|")
        print("+" + "-" * box_width + "+")
        stats_str = f"Menu: {menu_count} | Kasir: {cashier_count} | Pesanan: {order_count}"
        print("|" + stats_str.center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        selected_menu = questionary.select(
            "Silakan pilih menu kelola:",
            choices=[
                "1. Kelola Katalog Menu (CRUD)",
                "2. Kelola Akun Kasir",
                "3. Laporan & Riwayat Penjualan",
                "4. Ganti Password Akun",
                "0. Logout (Kembali ke Menu Utama)"
            ]
        ).ask()

        if selected_menu is None or selected_menu.startswith("0"):
            confirmed = questionary.confirm("Konfirmasi logout dari sesi Admin?").ask()
            if confirmed:
                print("\n[INFO] Berhasil logout dari menu admin.")
                break
            continue
        elif selected_menu.startswith("1"):
            manage_menu_catalog()
        elif selected_menu.startswith("2"):
            manage_cashiers()
        elif selected_menu.startswith("3"):
            manage_reports()
        elif selected_menu.startswith("4"):
            if user_session:
                change_password(user_session)
            else:
                print("[ERROR] Sesi pengguna tidak ditemukan.")
                pause_screen()
