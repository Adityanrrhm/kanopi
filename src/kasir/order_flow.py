import datetime
import pandas as pd
import questionary
from tabulate import tabulate
from core.utils import (
    clear_screen,
    pause_screen,
    format_currency
)
from core.database import (
    load_menu,
    save_menu,
    load_orders,
    save_orders,
    load_order_details,
    save_order_details
)

def generate_order_code():
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    prefix = f"TRX-{today_str}-"
    orders_df = load_orders()
    if orders_df.empty or 'kode_pesanan' not in orders_df.columns:
        return f"{prefix}001"
    matching_codes = orders_df['kode_pesanan'].astype(str)
    today_codes = matching_codes[matching_codes.str.startswith(prefix)]
    if today_codes.empty:
        return f"{prefix}001"
    max_num = 0
    for code in today_codes:
        parts = code.split("-")
        if len(parts) >= 3 and parts[-1].isdigit():
            max_num = max(max_num, int(parts[-1]))
    return f"{prefix}{max_num + 1:03d}"

def select_menu_from_category(menu_df, category_filter=None):
    if category_filter:
        working_df = menu_df[menu_df['kategori'] == category_filter].copy()
    else:
        working_df = menu_df.copy()

    available = working_df[working_df['stok'] > 0]
    if available.empty:
        print("\n[INFO] Tidak ada menu yang tersedia di kategori ini.")
        pause_screen()
        return None

    choices = []
    for _, row in available.iterrows():
        choices.append(
            f"{row['id_menu']} - {row['nama_menu']} ({format_currency(row['harga'])}) [Stok: {row['stok']}]"
        )
    choices.append("0. Batal / Kembali")

    selected = questionary.select("Pilih menu yang dipesan:", choices=choices).ask()
    if selected is None or selected.startswith("0"):
        return None
    return selected.split(" - ")[0].strip()

def add_menu_item_to_cart(cart, action):
    if action.startswith("Tambah dari Semua"):
        category_filter = None
    else:
        category_filter = action.split("Tambah ")[1].split(" (")[0]

    menu_df_now = load_menu()
    selected_id = select_menu_from_category(menu_df_now, category_filter)
    if not selected_id:
        return

    matched_row = menu_df_now[menu_df_now['id_menu'] == selected_id].iloc[0]
    cart_item = next((i for i in cart if i['id_menu'] == selected_id), None)
    already_in_cart = cart_item['jumlah'] if cart_item else 0
    max_available = int(matched_row['stok']) - already_in_cart

    if max_available <= 0:
        print(f"\n[ERROR] Stok '{matched_row['nama_menu']}' sudah habis diambil ({matched_row['stok']} porsi).")
        pause_screen()
        return

    qty_input = questionary.text(
        f"Jumlah porsi '{matched_row['nama_menu']}' (Tersedia: {max_available}):"
    ).ask()

    if qty_input is None or not qty_input.strip():
        return
    if not qty_input.strip().isdigit() or int(qty_input.strip()) <= 0:
        print("\n[ERROR] Jumlah porsi harus berupa angka positif.")
        pause_screen()
        return

    qty_val = int(qty_input.strip())
    if qty_val > max_available:
        print(f"\n[ERROR] Melebihi stok tersisa ({max_available} porsi).")
        pause_screen()
        return

    if cart_item:
        cart_item['jumlah'] += qty_val
        cart_item['subtotal'] = cart_item['jumlah'] * cart_item['harga']
    else:
        cart.append({
            'id_menu': matched_row['id_menu'],
            'nama_menu': matched_row['nama_menu'],
            'harga': int(matched_row['harga']),
            'jumlah': qty_val,
            'subtotal': qty_val * int(matched_row['harga'])
        })
    print(f"\n[OK] {qty_val}x '{matched_row['nama_menu']}' dimasukkan ke keranjang.")
    pause_screen()

def edit_cart_item(cart):
    while True:
        edit_choices = [
            f"{idx}. {item['nama_menu']} ({item['jumlah']}x) = {format_currency(item['subtotal'])}"
            for idx, item in enumerate(cart, 1)
        ]
        edit_choices.append("0. Kembali")

        selected_edit = questionary.select("Pilih item yang ingin diubah:", choices=edit_choices).ask()
        if selected_edit is None or selected_edit.startswith("0"):
            return

        item_index = int(selected_edit.split(".")[0]) - 1
        target = cart[item_index]

        sub_action = questionary.select(
            f"Atur '{target['nama_menu']}':",
            choices=["Ubah Jumlah Porsi", "Hapus Item dari Keranjang", "0. Batal"]
        ).ask()

        if sub_action is None or sub_action.startswith("0"):
            return
        elif sub_action.startswith("Ubah"):
            menu_df_now = load_menu()
            matched = menu_df_now[menu_df_now['id_menu'] == target['id_menu']]
            max_stok = int(matched['stok'].iloc[0]) if not matched.empty else 0

            new_qty_input = questionary.text(
                f"Jumlah porsi baru '{target['nama_menu']}' (Maks: {max_stok}, 0 untuk hapus):"
            ).ask()
            if new_qty_input is None or not new_qty_input.strip().isdigit():
                print("\n[ERROR] Masukkan angka yang valid.")
                pause_screen()
                return
            new_qty = int(new_qty_input.strip())
            if new_qty > max_stok:
                print(f"\n[ERROR] Melebihi stok yang tersedia ({max_stok} porsi).")
                pause_screen()
                return
            if new_qty == 0:
                cart.pop(item_index)
                print(f"\n[OK] '{target['nama_menu']}' dihapus dari keranjang.")
            else:
                target['jumlah'] = new_qty
                target['subtotal'] = new_qty * target['harga']
                print(f"\n[OK] Porsi diubah menjadi {new_qty}x.")
            pause_screen()
        elif sub_action.startswith("Hapus"):
            cart.pop(item_index)
            print(f"\n[OK] '{target['nama_menu']}' dihapus dari keranjang.")
            pause_screen()

def process_checkout(cart, total_amount, user_session, shift_session, receipt_printer):
    clear_screen()
    print("\n+------------------------------------------+")
    print("|   [KASIR > PROSES PEMBAYARAN]            |")
    print("+------------------------------------------+")
    print(f"\n  Total Tagihan : {format_currency(total_amount)}")
    print("-" * 44)

    tipe_choice = questionary.select(
        "Pilih tipe layanan:",
        choices=["Dine In (Makan di Tempat)", "Take Away (Bungkus)", "0. Kembali ke Keranjang"]
    ).ask()

    if tipe_choice is None or tipe_choice.startswith("0"):
        return False

    tipe_layanan = "Dine In" if tipe_choice.startswith("Dine") else "Take Away"

    nama_input = questionary.text("Nama Pelanggan (opsional, kosongkan jika tidak ada):").ask()
    if nama_input is None:
        return False
    customer_name = nama_input.strip() if nama_input.strip() else "Pelanggan"

    pay_choice = questionary.select(
        "Pilih metode pembayaran:",
        choices=["Tunai (Cash)", "QRIS", "0. Kembali"]
    ).ask()

    if pay_choice is None or pay_choice.startswith("0"):
        return False

    if pay_choice.startswith("Tunai"):
        while True:
            cash_input = questionary.text(
                f"Masukkan nominal uang tunai (Minimal {format_currency(total_amount)}):"
            ).ask()
            if cash_input is None:
                return False
            cash_clean = cash_input.strip().replace(".", "").replace(",", "")
            if not cash_clean.isdigit():
                print("[ERROR] Masukkan nominal angka yang valid.")
                continue
            cash_received = int(cash_clean)
            if cash_received < total_amount:
                print(f"[ERROR] Uang kurang {format_currency(total_amount - cash_received)}.")
                continue
            break
        change = cash_received - total_amount
        payment_method = "TUNAI"
        amount_received = cash_received

        w = 44
        print("\n" + "-" * w)
        print(f"  Total Tagihan : {format_currency(total_amount):>24}")
        print(f"  Uang Diterima : {format_currency(cash_received):>24}")
        print(f"  Kembalian     : {format_currency(change):>24}")
        print("-" * w)
        if not questionary.confirm("Proses transaksi tunai ini?", default=True).ask():
            print("[INFO] Transaksi ditunda, kembali ke keranjang.")
            pause_screen()
            return False
    else:
        print(f"\n[INFO] Total tagihan QRIS : {format_currency(total_amount)}")
        print("[INFO] Silakan minta pembeli memindai kode QRIS di kasir.")
        confirmed = questionary.confirm("Konfirmasi dana QRIS telah masuk?").ask()
        if not confirmed:
            return False
        payment_method = "QRIS"
        amount_received = total_amount
        change = 0

    menu_df_live = load_menu()
    for item in cart:
        mask = menu_df_live['id_menu'] == item['id_menu']
        if mask.any():
            menu_df_live.loc[mask, 'stok'] -= item['jumlah']
    save_menu(menu_df_live)

    order_code = generate_order_code()
    cashier_id = user_session['id_user']
    shift_id = shift_session.get('shift', '') if shift_session else ''
    transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    orders_df = load_orders()
    new_order = {
        'kode_pesanan': order_code,
        'nama_pelanggan': customer_name,
        'tipe_layanan': tipe_layanan,
        'total_harga': str(total_amount),
        'status': 'DIBAYAR',
        'metode_pembayaran': payment_method,
        'uang_diterima': str(amount_received),
        'kembalian': str(change),
        'id_kasir': cashier_id,
        'shift': shift_id,
        'waktu': transaction_time
    }
    orders_df = pd.concat([orders_df, pd.DataFrame([new_order])], ignore_index=True)
    save_orders(orders_df)

    details_df = load_order_details()
    new_details = []
    for item in cart:
        new_details.append({
            'kode_pesanan': order_code,
            'id_menu': item['id_menu'],
            'nama_menu': item['nama_menu'],
            'harga_satuan': str(item['harga']),
            'jumlah': str(item['jumlah']),
            'subtotal': str(item['subtotal'])
        })
    details_df = pd.concat([details_df, pd.DataFrame(new_details)], ignore_index=True)
    save_order_details(details_df)

    clear_screen()
    print(f"\n[OK] Transaksi '{order_code}' berhasil diproses via {payment_method}.")
    if payment_method == "TUNAI" and change > 0:
        print(f"[OK] Kembalian : {format_currency(change)}")
    receipt_printer(order_code)
    pause_screen()
    return True

def run_direct_pos_order(user_session, shift_session, receipt_printer):
    cart = []

    while True:
        clear_screen()
        total_amount = sum(item['subtotal'] for item in cart)

        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "[KASIR > TRANSAKSI PENJUALAN BARU]".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        if not cart:
            print("\n[INFO] Keranjang pesanan masih kosong.")
        else:
            table_data = []
            for idx, item in enumerate(cart, 1):
                table_data.append([
                    idx,
                    item['nama_menu'],
                    format_currency(item['harga']),
                    f"{item['jumlah']}x",
                    format_currency(item['subtotal'])
                ])
            headers = ['No', 'Nama Menu', 'Harga', 'Porsi', 'Subtotal']
            colalign = ('center', 'left', 'right', 'center', 'right')
            print("\n" + tabulate(table_data, headers=headers, tablefmt='rounded_outline', colalign=colalign))
            print(f"\n  TOTAL SEMENTARA : {format_currency(total_amount)}")

        menu_df = load_menu()
        categories = sorted(list(menu_df['kategori'].dropna().unique()))

        cat_choices = []
        for cat in categories:
            available_count = len(menu_df[(menu_df['kategori'] == cat) & (menu_df['stok'] > 0)])
            cat_choices.append(f"Tambah {cat} ({available_count} tersedia)")
        cat_choices.append("Tambah dari Semua Menu")
        if cart:
            cat_choices.append("Ubah Porsi / Hapus Item")
            cat_choices.append("Lanjut ke Pembayaran")
        cat_choices.append("0. Batalkan Transaksi")

        action = questionary.select("Pilih aksi:", choices=cat_choices).ask()

        if action is None or action.startswith("0"):
            if cart:
                confirmed = questionary.confirm("Yakin ingin membatalkan transaksi ini? Keranjang akan dikosongkan.").ask()
                if confirmed:
                    print("\n[INFO] Transaksi dibatalkan.")
                    pause_screen()
                    return
                continue
            print("\n[INFO] Transaksi dibatalkan.")
            pause_screen()
            return
        elif action.startswith("Lanjut ke Pembayaran"):
            success = process_checkout(cart, total_amount, user_session, shift_session, receipt_printer)
            if success:
                return
        elif action.startswith("Ubah Porsi"):
            edit_cart_item(cart)
        else:
            add_menu_item_to_cart(cart, action)
