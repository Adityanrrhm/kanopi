import questionary
from tabulate import tabulate
from core.utils import (
    clear_screen,
    pause_screen
)
from core.database import load_users
from auth.auth import (
    register_cashier,
    update_user_status,
    reset_user_password,
    get_password_input
)

def display_cashiers():
    clear_screen()
    users_df = load_users()
    cashiers_df = users_df[users_df['role'] == 'kasir']
    if cashiers_df.empty:
        print("\n[INFO] Belum ada akun kasir yang terdaftar.")
        pause_screen()
        return

    table_data = []
    for _, row in cashiers_df.iterrows():
        table_data.append([
            row['id_user'],
            row['username'],
            row['nama'],
            row['no_hp'],
            row['status']
        ])

    table_headers = ['ID Kasir', 'Username', 'Nama Lengkap', 'Nomor HP', 'Status']
    colalign = ('center', 'left', 'left', 'center', 'center')
    print("\n" + tabulate(table_data, headers=table_headers, tablefmt='rounded_outline', colalign=colalign))
    pause_screen()

def toggle_cashier_status():
    clear_screen()
    users_df = load_users()
    cashiers_df = users_df[users_df['role'] == 'kasir']
    if cashiers_df.empty:
        print("\n[INFO] Belum ada akun kasir yang terdaftar.")
        pause_screen()
        return

    choices = []
    for _, row in cashiers_df.iterrows():
        choices.append(f"{row['id_user']} - {row['username']} ({row['nama']}) [Status: {row['status']}]")
    choices.append("0. Batal / Kembali")

    selected = questionary.select(
        "Pilih akun kasir yang ingin diubah statusnya:",
        choices=choices
    ).ask()

    if selected is None or selected.startswith("0"):
        return

    selected_id = selected.split(" - ")[0].strip()
    selected_row = cashiers_df[cashiers_df['id_user'] == selected_id].iloc[0]
    current_status = selected_row['status']
    target_status = "nonaktif" if current_status == "aktif" else "aktif"

    confirmed = questionary.confirm(
        f"Ubah status akun '{selected_row['username']}' dari [{current_status}] menjadi [{target_status}]?"
    ).ask()

    if confirmed:
        update_user_status(selected_id, target_status)
        print(f"\n[OK] Status kasir '{selected_row['username']}' berhasil diubah menjadi [{target_status}].")
    else:
        print("[INFO] Perubahan status dibatalkan.")
    pause_screen()
    toggle_cashier_status()

def admin_reset_cashier_password():
    clear_screen()
    users_df = load_users()
    cashiers_df = users_df[users_df['role'] == 'kasir']
    if cashiers_df.empty:
        print("\n[INFO] Belum ada akun kasir yang terdaftar.")
        pause_screen()
        return

    choices = []
    for _, row in cashiers_df.iterrows():
        choices.append(f"{row['id_user']} - {row['username']} ({row['nama']})")
    choices.append("0. Batal / Kembali")

    selected = questionary.select(
        "Pilih kasir yang ingin direset passwordnya:",
        choices=choices
    ).ask()

    if selected is None or selected.startswith("0"):
        return

    selected_id = selected.split(" - ")[0].strip()
    selected_username = cashiers_df[cashiers_df['id_user'] == selected_id]['username'].values[0]

    while True:
        new_password = get_password_input(f"Masukkan password baru untuk kasir '{selected_username}': ")
        if not new_password:
            print("[INFO] Reset password dibatalkan.")
            pause_screen()
            return

        if not questionary.confirm(f"Konfirmasi reset password untuk kasir '{selected_username}'?", default=True).ask():
            print("[INFO] Reset password dibatalkan.")
            pause_screen()
            return

        success, message = reset_user_password(selected_id, new_password)
        if success:
            print(f"\n[OK] Password untuk kasir '{selected_username}' berhasil direset.")
            pause_screen()
            break
        else:
            print(f"[ERROR] {message}")

def manage_cashiers():
    while True:
        clear_screen()
        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "KELOLA AKUN KASIR".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        choice = questionary.select(
            "Pilih operasi akun kasir:",
            choices=[
                "1. Tampilkan Daftar Kasir",
                "2. Tambah Akun Kasir Baru",
                "3. Nonaktifkan / Aktifkan Akun Kasir",
                "4. Reset Password Kasir",
                "0. Kembali ke Menu Admin"
            ]
        ).ask()

        if choice is None or choice.startswith("0"):
            break
        elif choice.startswith("1"):
            display_cashiers()
        elif choice.startswith("2"):
            register_cashier()
        elif choice.startswith("3"):
            toggle_cashier_status()
        elif choice.startswith("4"):
            admin_reset_cashier_password()
