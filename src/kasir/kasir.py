import datetime
import pandas as pd
import questionary
from tabulate import tabulate
from core.utils import (
    clear_screen,
    pause_screen,
    format_currency,
    fmt_date
)
from core.database import (
    load_orders,
    load_order_details,
    load_users
)
from auth.auth import (
    change_password,
    buka_shift,
    tutup_shift
)
from kasir.order_flow import run_direct_pos_order

def print_receipt(order_code):
    orders_df = load_orders()
    target_order = orders_df[orders_df['kode_pesanan'] == order_code]
    if target_order.empty:
        print(f"[ERROR] Transaksi dengan kode '{order_code}' tidak ditemukan.")
        return

    order_row = target_order.iloc[0]
    details_df = load_order_details()
    order_items = details_df[details_df['kode_pesanan'] == order_code]

    cashier_display = order_row['id_kasir'] if order_row['id_kasir'] else "Kasir"
    users_df = load_users()
    matched_cashier = users_df[users_df['id_user'] == order_row['id_kasir']]
    if not matched_cashier.empty:
        cashier_name = matched_cashier['nama'].values[0]
        cashier_display = f"{cashier_name} [{order_row['id_kasir']}]"

    def _safe_int(val, fallback=0):
        try:
            return int(float(str(val).strip()))
        except (ValueError, TypeError):
            return fallback

    total_val    = _safe_int(order_row['total_harga'])
    received_val = _safe_int(order_row['uang_diterima'], fallback=total_val)
    change_val   = _safe_int(order_row['kembalian'])

    w = 50
    print("\n" + "=" * w)
    print("KEDAI AYAM GEPREK KAMPUS".center(w))
    print("Jl. Kalimantan No. 12, Jember".center(w))
    print("=" * w)
    print(f"Kode Transaksi : {order_row['kode_pesanan']}")
    print(f"Pelanggan      : {order_row['nama_pelanggan']}")
    print(f"Tipe Layanan   : {order_row['tipe_layanan']}")
    print(f"Kasir          : {cashier_display}")
    print(f"Waktu          : {fmt_date(order_row['waktu'])}")
    print("-" * w)

    for _, item in order_items.iterrows():
        item_name  = str(item['nama_menu'])
        qty        = str(item['jumlah'])
        unit_price = _safe_int(item['harga_satuan'])
        subtotal   = _safe_int(item['subtotal'])
        dname = item_name if len(item_name) <= 23 else item_name[:22] + "."
        print(f"{dname:<23} {qty:>2}x {format_currency(unit_price):>10} {format_currency(subtotal):>11}")

    print("-" * w)
    print(f"{'Total Tagihan':<35} {format_currency(total_val):>14}")
    print(f"{'Metode Pembayaran':<35} {order_row['metode_pembayaran']:>14}")
    print(f"{'Uang Diterima':<35} {format_currency(received_val):>14}")
    print(f"{'Kembalian':<35} {format_currency(change_val):>14}")
    print("=" * w)
    print("Status : [DIBAYAR - LUNAS]".center(w))
    print("Terima kasih atas kunjungan Anda.".center(w))
    print("[ Powered by KANOPI POS ]".center(w))
    print("=" * w)

def direct_pos_order(user_session, shift_session):
    run_direct_pos_order(user_session, shift_session, print_receipt)

def view_today_transactions():
    while True:
        clear_screen()
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "[KASIR > TRANSAKSI HARI INI]".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        orders_df = load_orders()
        today_orders = orders_df[orders_df['waktu'].astype(str).str.startswith(today_date)]

        if today_orders.empty:
            print("\n[INFO] Belum ada transaksi pada hari ini.")
            pause_screen()
            return

        def _safe_int(val, fallback=0):
            try:
                return int(float(str(val).strip()))
            except (ValueError, TypeError):
                return fallback

        table_data = []
        for _, row in today_orders.iterrows():
            table_data.append([
                row['kode_pesanan'],
                row['nama_pelanggan'],
                row['tipe_layanan'],
                format_currency(_safe_int(row['total_harga'])),
                row['status'],
                row['metode_pembayaran'] if row['metode_pembayaran'] else "-",
                row['waktu'].split(" ")[-1] if " " in str(row['waktu']) else row['waktu']
            ])

        headers = ['Kode', 'Pelanggan', 'Tipe', 'Total', 'Status', 'Metode', 'Jam']
        colalign = ('center', 'left', 'center', 'right', 'center', 'center', 'center')
        print("\n" + tabulate(table_data, headers=headers, tablefmt='rounded_outline', colalign=colalign))
        print(f"\n  Total Transaksi: {len(today_orders)}")

        subaction = questionary.select(
            "Pilih opsi:",
            choices=[
                "1. Cetak Ulang Struk Transaksi",
                "0. Kembali ke Menu Kasir"
            ]
        ).ask()

        if subaction is None or subaction.startswith("0"):
            return

        if subaction.startswith("1"):
            choices = [
                f"{row['kode_pesanan']} - {row['nama_pelanggan']} ({row['tipe_layanan']}) - {format_currency(_safe_int(row['total_harga']))}"
                for _, row in today_orders.iterrows()
            ]
            choices.append("0. Batal")
            selected = questionary.select("Pilih transaksi untuk cetak ulang struk:", choices=choices).ask()
            if selected and not selected.startswith("0"):
                order_code = selected.split(" - ")[0].strip()
                clear_screen()
                print_receipt(order_code)
                pause_screen()

def search_transactions():
    clear_screen()
    box_width = 46
    print("\n+" + "-" * box_width + "+")
    print("|" + "[KASIR > CARI TRANSAKSI]".center(box_width) + "|")
    print("+" + "-" * box_width + "+")

    orders_df = load_orders()
    if orders_df.empty:
        print("\n[INFO] Belum ada data transaksi di sistem.")
        pause_screen()
        return

    keyword = questionary.text("Masukkan kode transaksi / nama pelanggan:").ask()
    if keyword is None or not keyword.strip():
        return

    clean_kw   = keyword.strip().lower()
    code_match = orders_df['kode_pesanan'].astype(str).str.lower().str.contains(clean_kw, na=False)
    name_match = orders_df['nama_pelanggan'].astype(str).str.lower().str.contains(clean_kw, na=False)
    matched    = orders_df[code_match | name_match]

    if matched.empty:
        print(f"\n[INFO] Tidak ditemukan transaksi dengan kata kunci '{keyword}'.")
    else:
        def _safe_int(val, fallback=0):
            try:
                return int(float(str(val).strip()))
            except (ValueError, TypeError):
                return fallback

        table_data = []
        for _, row in matched.iterrows():
            table_data.append([
                row['kode_pesanan'],
                row['nama_pelanggan'],
                row['tipe_layanan'],
                format_currency(_safe_int(row['total_harga'])),
                row['status'],
                row['metode_pembayaran'] if row['metode_pembayaran'] else "-",
                fmt_date(row['waktu'])
            ])
        headers = ['Kode', 'Pelanggan', 'Tipe', 'Total', 'Status', 'Metode', 'Waktu']
        colalign = ('center', 'left', 'center', 'right', 'center', 'center', 'center')
        print(f"\n[OK] Ditemukan {len(matched)} transaksi:")
        print(tabulate(table_data, headers=headers, tablefmt='rounded_outline', colalign=colalign))

    pause_screen()

def menu_kasir(user_session=None):
    shift_session = buka_shift(user_session)
    if shift_session is None:
        return

    cashier_name = user_session.get('nama', 'Kasir')
    cashier_id   = user_session.get('id_user', '-')

    while True:
        clear_screen()
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        orders_df = load_orders()
        today_orders = orders_df[
            (orders_df['id_kasir'] == cashier_id) &
            (orders_df['waktu'].astype(str).str.startswith(today_date)) &
            (orders_df['status'] == 'DIBAYAR')
        ]
        today_count = len(today_orders)
        total_omzet = int(pd.to_numeric(today_orders['total_harga'], errors='coerce').fillna(0).sum()) if not today_orders.empty else 0

        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "SISTEM KASIR KEDAI KANOPI".center(box_width) + "|")
        print("|" + f" Kasir  : {cashier_name} [{cashier_id}]".ljust(box_width) + "|")
        print("|" + f" Shift  : {shift_session['shift']}".ljust(box_width) + "|")
        print("+" + "-" * box_width + "+")
        stats_str = f"Transaksi: {today_count} | Omzet: {format_currency(total_omzet)}"
        print("|" + stats_str.center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        selected = questionary.select(
            "Silakan pilih aksi kasir:",
            choices=[
                "1. Transaksi Penjualan Baru",
                "2. Riwayat Transaksi Hari Ini",
                "0. Tutup Shift & Logout"
            ]
        ).ask()

        if selected is None or selected.startswith("0"):
            confirmed = questionary.confirm("Konfirmasi tutup shift dan logout dari sesi Kasir?").ask()
            if confirmed:
                tutup_shift(shift_session)
                print("\n[INFO] Berhasil logout dari menu kasir.")
                break
            continue
        elif selected.startswith("1"):
            direct_pos_order(user_session, shift_session)
        elif selected.startswith("2"):
            view_today_transactions()
