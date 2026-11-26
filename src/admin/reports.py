import pandas as pd
import questionary
from tabulate import tabulate
from core.utils import (
    clear_screen,
    pause_screen,
    format_currency,
    fmt_date,
    parse_date_input
)
from core.database import (
    load_orders,
    load_users,
    load_rekap_shift
)

def view_all_transactions():
    clear_screen()
    orders_df = load_orders()
    if orders_df.empty:
        print("\n[INFO] Belum ada riwayat transaksi.")
        pause_screen()
        return

    table_data = []
    for _, row in orders_df.iterrows():
        try:
            total_val = int(float(str(row['total_harga']).strip()))
        except (ValueError, TypeError):
            total_val = 0
        table_data.append([
            row['kode_pesanan'],
            row['nama_pelanggan'] if row['nama_pelanggan'] else "-",
            row['tipe_layanan'],
            format_currency(total_val),
            row['status'],
            row['metode_pembayaran'] if row['metode_pembayaran'] else "-",
            fmt_date(row['waktu'])
        ])

    table_headers = ['Kode Pesanan', 'Pelanggan', 'Tipe Layanan', 'Total', 'Status', 'Metode', 'Waktu']
    colalign = ('center', 'left', 'center', 'right', 'center', 'center', 'center')
    print("\n" + tabulate(table_data, headers=table_headers, tablefmt='rounded_outline', colalign=colalign))
    pause_screen()

def filter_transactions():
    while True:
        clear_screen()
        orders_df = load_orders()
        if orders_df.empty:
            print("\n[INFO] Belum ada riwayat transaksi.")
            pause_screen()
            return

        filter_choice = questionary.select(
            "Pilih jenis filter:",
            choices=[
                "1. Berdasarkan Tanggal",
                "2. Berdasarkan Kasir",
                "0. Batal / Kembali"
            ]
        ).ask()

        if filter_choice is None or filter_choice.startswith("0"):
            return

        filtered_df = None

        if filter_choice.startswith("1"):
            while True:
                date_input = questionary.text("Masukkan tanggal (format: DD-MM-YYYY):").ask()
                if date_input is None or not date_input.strip():
                    break
                iso_date = parse_date_input(date_input.strip())
                if not iso_date:
                    print("[ERROR] Format tanggal tidak valid. Gunakan DD-MM-YYYY.")
                    continue
                filtered_df = orders_df[orders_df['waktu'].astype(str).str.startswith(iso_date)]
                break

        elif filter_choice.startswith("2"):
            users_df = load_users()
            kasirs_df = users_df[users_df['role'] == 'kasir']
            if kasirs_df.empty:
                print("[INFO] Belum ada akun kasir terdaftar.")
                pause_screen()
                continue
            kasir_choices = [
                f"{row['id_user']} - {row['username']} ({row['nama']})"
                for _, row in kasirs_df.iterrows()
            ]
            kasir_choices.append("0. Batal / Kembali")
            selected_kasir = questionary.select("Pilih kasir:", choices=kasir_choices).ask()
            if selected_kasir is None or selected_kasir.startswith("0"):
                continue
            selected_kasir_id = selected_kasir.split(" - ")[0].strip()
            filtered_df = orders_df[orders_df['id_kasir'] == selected_kasir_id]

        if filtered_df is None:
            continue

        if filtered_df.empty:
            print("\n[INFO] Tidak ada transaksi yang cocok dengan filter tersebut.")
        else:
            table_data = []
            for _, row in filtered_df.iterrows():
                try:
                    total_val = int(float(str(row['total_harga']).strip()))
                except (ValueError, TypeError):
                    total_val = 0
                table_data.append([
                    row['kode_pesanan'],
                    row['nama_pelanggan'] if row['nama_pelanggan'] else "-",
                    row['tipe_layanan'],
                    format_currency(total_val),
                    row['status'],
                    row['metode_pembayaran'] if row['metode_pembayaran'] else "-",
                    fmt_date(row['waktu'])
                ])
            table_headers = ['Kode Pesanan', 'Pelanggan', 'Tipe Layanan', 'Total', 'Status', 'Metode', 'Waktu']
            colalign = ('center', 'left', 'center', 'right', 'center', 'center', 'center')
            print(f"\n[OK] Ditemukan {len(filtered_df)} transaksi:")
            print(tabulate(table_data, headers=table_headers, tablefmt='rounded_outline', colalign=colalign))

        pause_screen()
        filter_transactions()

def sales_summary():
    clear_screen()
    orders_df = load_orders()

    paid_orders = orders_df[orders_df['status'] == 'DIBAYAR']
    cancelled_orders = orders_df[orders_df['status'] == 'BATAL']

    if paid_orders.empty:
        print("\n[INFO] Belum ada transaksi yang berstatus DIBAYAR.")
        pause_screen()
        return

    paid_orders = paid_orders.copy()
    paid_orders['total_harga'] = pd.to_numeric(paid_orders['total_harga'], errors='coerce').fillna(0)

    total_revenue = paid_orders['total_harga'].sum()
    total_transactions = len(paid_orders)

    cash_orders = paid_orders[paid_orders['metode_pembayaran'].str.upper() == 'TUNAI']
    qris_orders = paid_orders[paid_orders['metode_pembayaran'].str.upper() == 'QRIS']
    total_cash = cash_orders['total_harga'].sum()
    total_qris = qris_orders['total_harga'].sum()

    w = 48
    print("\n" + "=" * w)
    print("RINGKASAN REKAP PENJUALAN".center(w))
    print("=" * w)
    print(f"  Total Transaksi Berhasil : {str(total_transactions) + ' transaksi':>19}")
    print(f"  Transaksi Dibatalkan     : {str(len(cancelled_orders)) + ' transaksi':>19}")
    print("-" * w)
    print(f"  Total Omzet              : {format_currency(total_revenue):>19}")
    print(f"  Pendapatan Tunai (Laci)  : {format_currency(total_cash):>19}")
    print(f"  Pendapatan QRIS          : {format_currency(total_qris):>19}")
    print("=" * w)
    pause_screen()

def view_shift_selisih_report():
    clear_screen()
    box_width = 46
    print("\n+" + "-" * box_width + "+")
    print("|" + "REKAP SELISIH KAS SHIFT".center(box_width) + "|")
    print("+" + "-" * box_width + "+")

    rekap_df = load_rekap_shift()
    if rekap_df.empty:
        print("\n[INFO] Belum ada data rekap shift kasir.")
        pause_screen()
        return

    table_data = []
    for _, row in rekap_df.iterrows():
        selisih_raw = row.get('selisih', '0')
        selisih_val = int(selisih_raw) if str(selisih_raw).lstrip('-').isdigit() else 0
        
        if selisih_val == 0:
            selisih_str = "Rp 0 [PAS]"
        elif selisih_val > 0:
            selisih_str = f"[!] +{format_currency(selisih_val)} [LEBIH]"
        else:
            selisih_str = f"[!] -{format_currency(abs(selisih_val))} [KURANG]"

        kas_awal_val = int(row.get('kas_awal', 0)) if str(row.get('kas_awal', '')).isdigit() else 0
        total_tunai_val = int(row.get('total_tunai', 0)) if str(row.get('total_tunai', '')).isdigit() else 0
        total_qris_val = int(row.get('total_qris', 0)) if str(row.get('total_qris', '')).isdigit() else 0
        seharusnya_val = int(row.get('seharusnya_laci', 0)) if str(row.get('seharusnya_laci', '')).isdigit() else 0
        fisik_val = int(row.get('fisik_laci', 0)) if str(row.get('fisik_laci', '')).isdigit() else 0

        table_data.append([
            row.get('id_rekap', ''),
            row.get('nama_kasir', ''),
            fmt_date(row.get('tanggal', '')),
            row.get('shift', ''),
            format_currency(kas_awal_val),
            format_currency(total_tunai_val),
            format_currency(total_qris_val),
            format_currency(seharusnya_val),
            format_currency(fisik_val),
            selisih_str,
            fmt_date(row.get('waktu_tutup', ''))
        ])

    table_headers = [
        'ID Rekap', 'Kasir', 'Tanggal', 'Shift',
        'Kas Awal', 'Total Tunai', 'Total QRIS',
        'Seharusnya', 'Fisik Laci', 'Selisih Kas', 'Waktu Tutup'
    ]
    colalign = (
        'center', 'left', 'center', 'center',
        'right', 'right', 'right',
        'right', 'right', 'center', 'center'
    )
    print("\n" + tabulate(table_data, headers=table_headers, tablefmt='rounded_outline', colalign=colalign))
    print("\n[INFO] Tanda [!] menandakan adanya selisih uang fisik laci (kurang/lebih).")
    pause_screen()

def manage_reports():
    while True:
        clear_screen()
        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "LAPORAN & RIWAYAT PENJUALAN".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        choice = questionary.select(
            "Pilih menu laporan:",
            choices=[
                "1. Lihat Semua Riwayat Transaksi",
                "2. Filter Riwayat Transaksi",
                "3. Ringkasan Rekap Penjualan",
                "4. Rekap Selisih Kas Shift Kasir",
                "0. Kembali ke Menu Admin"
            ]
        ).ask()

        if choice is None or choice.startswith("0"):
            break
        elif choice.startswith("1"):
            view_all_transactions()
        elif choice.startswith("2"):
            filter_transactions()
        elif choice.startswith("3"):
            sales_summary()
        elif choice.startswith("4"):
            view_shift_selisih_report()
