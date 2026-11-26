import datetime
import pandas as pd
import questionary
from core.utils import (
    clear_screen,
    pause_screen,
    format_currency,
    fmt_date,
    generate_sequential_id
)
from core.database import (
    load_users,
    save_users,
    load_orders,
    load_rekap_shift,
    save_rekap_shift
)

SHIFT_HOURS = {
    "Pagi": ("06:00", "14:00"),
    "Siang": ("14:00", "22:00"),
}

def validate_password(password):
    if len(password) < 6:
        return False, "Password minimal harus 6 karakter."
    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    if not (has_letter and has_digit):
        return False, "Password harus mengandung kombinasi huruf dan angka."
    return True, "Password valid."

def validate_username(username):
    if len(username) < 3:
        return False, "Username minimal 3 karakter."
    if " " in username:
        return False, "Username tidak boleh mengandung spasi."
    clean_username = username.replace("_", "")
    if not clean_username.isalnum():
        return False, "Username hanya boleh huruf, angka, dan underscore (_)."
    return True, "Username valid."

def validate_phone_number(phone_number):
    if not phone_number.isdigit():
        return False, "Nomor telepon hanya boleh berisi angka."
    if not (10 <= len(phone_number) <= 13):
        return False, "Nomor telepon harus 10 sampai 13 digit."
    if not phone_number.startswith("0"):
        return False, "Nomor telepon harus diawali dengan angka 0."
    return True, "Nomor telepon valid."

def validate_nama_lengkap(nama_lengkap):
    if len(nama_lengkap) < 3:
        return False, "Nama lengkap minimal 3 karakter."
    if not all(char.isalpha() or char.isspace() for char in nama_lengkap):
        return False, "Nama lengkap hanya boleh huruf dan spasi."
    return True, "Nama lengkap valid."

def get_text_input(prompt):
    while True:
        value = questionary.text(prompt).ask()
        if value is None:
            return ""
        trimmed_value = value.strip()
        if trimmed_value:
            return trimmed_value
        print("[ERROR] Input tidak boleh kosong.")

def get_password_input(prompt):
    while True:
        value = questionary.text(prompt).ask()
        if value is None:
            return ""
        trimmed_value = value.strip()
        if trimmed_value:
            return trimmed_value
        print("[ERROR] Password tidak boleh kosong.")

def buka_shift(user_session):
    while True:
        clear_screen()
        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "BUKA SHIFT KASIR".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        normal_shift = "Pagi" if 6 <= current_hour < 14 else "Siang"

        shift_choice = questionary.select(
            "Pilih shift kerja kamu sekarang:",
            choices=["1. Pagi (06:00 - 14:00)", "2. Siang (14:00 - 22:00)", "0. Batal / Keluar"]
        ).ask()

        if shift_choice is None or shift_choice.startswith("0"):
            return None

        shift_name = "Pagi" if shift_choice.startswith("1") else "Siang"
        jam_masuk, jam_keluar = SHIFT_HOURS[shift_name]

        if shift_name != normal_shift:
            confirm_time = questionary.confirm(
                f"Jam saat ini {now.strftime('%H:%M')} (waktu normal Shift {normal_shift}). Tetap buka Shift {shift_name}?",
                default=False
            ).ask()
            if not confirm_time:
                continue

        print(f"\n  Shift     : {shift_name} ({jam_masuk} - {jam_keluar})")
        print(f"  Tanggal   : {fmt_date(today)}")
        print(f"  Jam Masuk : {now.strftime('%H:%M')}")

        while True:
            kas_input = questionary.text(
                "Hitung dan masukkan total uang tunai di laci kasir sekarang (Rp):"
            ).ask()
            if kas_input is None:
                return None
            kas_clean = kas_input.strip().replace(".", "").replace(",", "").replace(" ", "")
            if not kas_clean:
                print("[ERROR] Kas awal tidak boleh kosong.")
                continue
            if not kas_clean.isdigit():
                print("[ERROR] Masukkan angka yang valid (tanpa Rp atau titik).")
                continue
            kas_awal = int(kas_clean)
            break

        ready = questionary.confirm(
            f"Konfirmasi buka Shift {shift_name} dengan modal {format_currency(kas_awal)}?",
            default=True
        ).ask()
        if not ready:
            print("[INFO] Buka shift dibatalkan. Silakan pilih ulang.")
            pause_screen()
            continue

        shift_session = {
            'id_kasir': user_session['id_user'],
            'nama_kasir': user_session['nama'],
            'tanggal': today,
            'shift': shift_name,
            'jam_masuk': jam_masuk,
            'jam_keluar': jam_keluar,
            'kas_awal': kas_awal,
            'waktu_buka': now.strftime("%Y-%m-%d %H:%M"),
        }

        print(f"\n[OK] Shift '{shift_name}' berhasil dibuka.")
        pause_screen()
        return shift_session

def tutup_shift(shift_session):
    clear_screen()
    box_width = 46
    print("\n+" + "-" * box_width + "+")
    print("|" + "TUTUP SHIFT & REKONSILIASI KAS".center(box_width) + "|")
    print("+" + "-" * box_width + "+")

    now = datetime.datetime.now()
    today = shift_session['tanggal']
    kasir_id = shift_session['id_kasir']
    waktu_tutup = now.strftime("%Y-%m-%d %H:%M")

    orders_df = load_orders()
    shift_orders = orders_df[
        (orders_df['id_kasir'] == kasir_id) &
        (orders_df['waktu'].astype(str).str.startswith(today)) &
        (orders_df['shift'] == shift_session['shift']) &
        (orders_df['status'] == 'DIBAYAR')
    ].copy()

    total_tunai = 0
    total_qris = 0
    if not shift_orders.empty:
        shift_orders['total_harga'] = pd.to_numeric(shift_orders['total_harga'], errors='coerce').fillna(0).astype(int)
        total_tunai = int(shift_orders[shift_orders['metode_pembayaran'].str.upper() == 'TUNAI']['total_harga'].sum())
        total_qris  = int(shift_orders[shift_orders['metode_pembayaran'].str.upper() == 'QRIS']['total_harga'].sum())

    total_omzet = total_tunai + total_qris
    kas_awal = int(shift_session['kas_awal'])
    seharusnya_laci = kas_awal + total_tunai

    print(f"\n  Kasir        : {shift_session['nama_kasir']} [{kasir_id}]")
    print(f"  Shift        : {shift_session['shift']} ({shift_session['jam_masuk']} - {shift_session['jam_keluar']})")
    print(f"  Tanggal      : {fmt_date(today)}")
    print(f"  Waktu Buka   : {fmt_date(shift_session['waktu_buka'])}")
    print(f"  Waktu Tutup  : {fmt_date(waktu_tutup)}")
    print("-" * 44)
    print("[INFO] Hitung uang tunai fisik di laci sebelum melihat data sistem.")

    while True:
        fisik_input = questionary.text(
            "Masukkan total uang tunai fisik di laci sekarang (Rp):"
        ).ask()
        if fisik_input is None or not fisik_input.strip():
            print("[ERROR] Input fisik laci tidak boleh kosong.")
            continue
        fisik_clean = fisik_input.strip().replace(".", "").replace(",", "").replace(" ", "")
        if not fisik_clean.isdigit():
            print("[ERROR] Masukkan nominal angka bulat yang valid.")
            continue
        fisik_laci = int(fisik_clean)
        break

    selisih = fisik_laci - seharusnya_laci

    w = 48
    print("\n" + "=" * w)
    print("LEMBAR REKONSILIASI KAS LACI".center(w))
    print("=" * w)
    print(f"  Kas Modal Awal     : {format_currency(kas_awal):>23}")
    print(f"  Penjualan Tunai    : {format_currency(total_tunai):>23}")
    print(f"  Penjualan QRIS     : {format_currency(total_qris):>23}")
    print("-" * w)
    print(f"  Total Omzet Shift  : {format_currency(total_omzet):>23}")
    transaksi_str = f"{len(shift_orders)} transaksi"
    print(f"  Total Transaksi    : {transaksi_str:>23}")
    print("-" * w)
    print(f"  Seharusnya di Laci : {format_currency(seharusnya_laci):>23}")
    print(f"  Fisik di Laci      : {format_currency(fisik_laci):>23}")
    print("-" * w)

    if selisih == 0:
        selisih_label = "Rp 0 [BALANCE / PAS]"
    elif selisih > 0:
        selisih_label = f"+{format_currency(selisih)} [LEBIH]"
    else:
        selisih_label = f"-{format_currency(abs(selisih))} [KURANG]"
    print(f"  STATUS SELISIH     : {selisih_label:>23}")
    print("=" * w)

    rekap_df = load_rekap_shift()
    rekap_id = generate_sequential_id(rekap_df, 'id_rekap', 'RKP')
    new_rekap = {
        'id_rekap': rekap_id,
        'id_kasir': kasir_id,
        'nama_kasir': shift_session['nama_kasir'],
        'tanggal': today,
        'shift': shift_session['shift'],
        'kas_awal': str(kas_awal),
        'total_tunai': str(total_tunai),
        'total_qris': str(total_qris),
        'seharusnya_laci': str(seharusnya_laci),
        'fisik_laci': str(fisik_laci),
        'selisih': str(selisih),
        'waktu_buka': shift_session['waktu_buka'],
        'waktu_tutup': waktu_tutup,
    }
    rekap_df = pd.concat([rekap_df, pd.DataFrame([new_rekap])], ignore_index=True)
    save_rekap_shift(rekap_df)

    print(f"\n[OK] Rekap shift '{rekap_id}' berhasil disimpan.")
    pause_screen()

def register_cashier():
    clear_screen()
    w = 46
    print("\n" + "=" * w)
    print("TAMBAH AKUN KASIR BARU".center(w))
    print("=" * w)

    users_df = load_users()

    while True:
        username = get_text_input("Masukkan username kasir: ")
        if not username:
            print("[INFO] Pendaftaran kasir dibatalkan.")
            return None
        is_valid, error_message = validate_username(username)
        if not is_valid:
            print(f"[ERROR] {error_message}")
            continue
        existing_usernames = users_df['username'].str.lower().values if not users_df.empty else []
        if username.lower() in existing_usernames:
            print(f"[ERROR] Username '{username}' sudah digunakan.")
            continue
        break

    while True:
        full_name = get_text_input("Masukkan nama lengkap kasir: ")
        if not full_name:
            print("[INFO] Pendaftaran kasir dibatalkan.")
            return None
        is_valid, error_message = validate_nama_lengkap(full_name)
        if not is_valid:
            print(f"[ERROR] {error_message}")
            continue
        break

    while True:
        phone_number = get_text_input("Masukkan nomor HP (08xxx): ")
        if not phone_number:
            print("[INFO] Pendaftaran kasir dibatalkan.")
            return None
        is_valid, error_message = validate_phone_number(phone_number)
        if not is_valid:
            print(f"[ERROR] {error_message}")
            continue
        break

    while True:
        password = get_password_input("Masukkan password kasir: ")
        if not password:
            print("[INFO] Pendaftaran kasir dibatalkan.")
            return None
        is_valid, error_message = validate_password(password)
        if not is_valid:
            print(f"[ERROR] {error_message}")
            continue
        break

    confirm = questionary.confirm(f"Konfirmasi daftarkan kasir '{username}' ({full_name})?", default=True).ask()
    if not confirm:
        print("[INFO] Pendaftaran kasir dibatalkan.")
        pause_screen()
        return None

    new_user_id = generate_sequential_id(users_df, 'id_user', 'USR')
    new_user_row = pd.DataFrame([{
        'id_user': new_user_id,
        'username': username,
        'password': password,
        'role': 'kasir',
        'nama': full_name,
        'no_hp': phone_number,
        'status': 'aktif'
    }])

    users_df = pd.concat([users_df, new_user_row], ignore_index=True)
    save_users(users_df)

    print(f"\n[OK] Akun kasir '{username}' berhasil terdaftar dengan ID [{new_user_id}].")
    pause_screen()
    return new_user_id

def login():
    clear_screen()
    w = 46
    print("\n" + "=" * w)
    print("LOGIN STAF KANOPI".center(w))
    print("=" * w)

    users_df = load_users()
    if users_df.empty:
        print("[ERROR] Belum ada data pengguna sama sekali.")
        pause_screen()
        return None

    username = get_text_input("Masukkan username: ")
    if not username:
        return None

    password = get_password_input("Masukkan password: ")
    if not password:
        return None

    username_match = users_df['username'].str.lower() == username.lower()
    password_match = users_df['password'] == password
    matched_user = users_df[username_match & password_match]

    if matched_user.empty:
        print("\n[ERROR] Login gagal. Username atau password salah.")
        pause_screen()
        return None

    account_status = str(matched_user['status'].values[0]).strip().lower()
    if account_status == 'nonaktif':
        print("\n[ERROR] Akun ini berstatus nonaktif. Silakan hubungi admin.")
        pause_screen()
        return None

    user_session = {
        'id_user': str(matched_user['id_user'].values[0]),
        'username': str(matched_user['username'].values[0]),
        'nama': str(matched_user['nama'].values[0]),
        'role': str(matched_user['role'].values[0]),
        'no_hp': str(matched_user['no_hp'].values[0]),
        'status': account_status
    }

    print(f"\n[OK] Login Berhasil. Memvalidasi hak akses...")
    pause_screen()
    # display_name = user_session['nama'] if user_session['nama'] else user_session['username']
    # print(f"\n[OK] Login berhasil. Selamat bertugas, {display_name} ({user_session['role']}).")
    return user_session

def change_password(user_session):
    users_df = load_users()
    user_index = users_df['id_user'] == user_session['id_user']

    current_password = str(users_df.loc[user_index, 'password'].values[0])
    old_password = get_password_input("Masukkan password lama: ")
    if old_password != current_password:
        print("[ERROR] Password lama tidak cocok.")
        pause_screen()
        return False

    while True:
        new_password = get_password_input("Masukkan password baru: ")
        if not new_password:
            print("[INFO] Pengubahan password dibatalkan.")
            pause_screen()
            return False
        is_valid, error_message = validate_password(new_password)
        if not is_valid:
            print(f"[ERROR] {error_message}")
            continue
        break

    if not questionary.confirm("Konfirmasi simpan password baru?", default=True).ask():
        print("[INFO] Pengubahan password dibatalkan.")
        pause_screen()
        return False

    users_df.loc[user_index, 'password'] = new_password
    save_users(users_df)
    print("[OK] Password berhasil diperbarui.")
    pause_screen()
    return True

def update_user_status(user_id, new_status):
    users_df = load_users()
    user_index = users_df['id_user'] == user_id
    if not user_index.any():
        return False
    users_df.loc[user_index, 'status'] = new_status
    save_users(users_df)
    return True

def reset_user_password(user_id, new_password):
    is_valid, error_message = validate_password(new_password)
    if not is_valid:
        return False, error_message
    users_df = load_users()
    user_index = users_df['id_user'] == user_id
    if not user_index.any():
        return False, "Pengguna tidak ditemukan."
    users_df.loc[user_index, 'password'] = new_password
    save_users(users_df)
    return True, "Password berhasil direset."
