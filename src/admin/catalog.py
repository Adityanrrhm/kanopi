import questionary
import pandas as pd
from tabulate import tabulate
from core.utils import (
    clear_screen,
    pause_screen,
    format_currency,
    generate_sequential_id
)
from core.database import (
    load_menu,
    save_menu
)

def select_menu_interactive(menu_df, prompt_label):
    if menu_df.empty:
        return None

    full_menu_df = menu_df.copy()

    while True:
        display_df = full_menu_df

        if len(full_menu_df) > 5:
            method = questionary.select(
                "Pilih metode penentuan menu:",
                choices=[
                    "1. Cari Menu (Ketik Nama / ID Menu)",
                    "2. Pilih dari Seluruh Daftar Menu",
                    "0. Batal / Kembali"
                ]
            ).ask()
            if method is None or method.startswith("0"):
                return None
            elif method.startswith("1"):
                keyword = questionary.text("Masukkan nama atau ID menu:").ask()
                if not keyword or not keyword.strip():
                    continue
                clean_kw = keyword.strip().lower()
                id_match   = full_menu_df['id_menu'].astype(str).str.lower().str.contains(clean_kw, na=False)
                name_match = full_menu_df['nama_menu'].astype(str).str.lower().str.contains(clean_kw, na=False)
                filtered = full_menu_df[id_match | name_match]
                if filtered.empty:
                    print(f"\n[INFO] Tidak ditemukan menu dengan kata kunci '{keyword}'.")
                    pause_screen()
                    continue
                display_df = filtered

        choices = []
        for _, row in display_df.iterrows():
            choices.append(f"{row['id_menu']} - {row['nama_menu']} ({format_currency(row['harga'])}) [Stok: {row['stok']}]")
        choices.append("0. Batal / Kembali")

        selected = questionary.select(prompt_label, choices=choices).ask()
        if selected is None or selected.startswith("0"):
            if len(full_menu_df) > 5:
                continue
            return None
        return selected.split(" - ")[0].strip()

def display_menu(menu_df=None):
    if menu_df is None:
        menu_df = load_menu()
    if menu_df.empty:
        print("\n[INFO] Katalog menu saat ini kosong.")
        pause_screen()
        return

    table_data = []
    for _, row in menu_df.iterrows():
        table_data.append([
            row['id_menu'],
            row['nama_menu'],
            row['kategori'],
            format_currency(row['harga']),
            row['stok']
        ])

    table_headers = ['ID Menu', 'Nama Menu', 'Kategori', 'Harga', 'Stok']
    colalign = ('center', 'left', 'center', 'right', 'right')
    print("\n" + tabulate(table_data, headers=table_headers, tablefmt='rounded_outline', colalign=colalign))
    pause_screen()

def add_menu():
    clear_screen()
    box_width = 46
    print("\n+" + "-" * box_width + "+")
    print("|" + "TAMBAH MENU BARU".center(box_width) + "|")
    print("+" + "-" * box_width + "+")

    menu_df = load_menu()

    while True:
        menu_name = questionary.text("Masukkan nama menu:").ask()
        if not menu_name:
            print("[INFO] Penambahan menu dibatalkan.")
            pause_screen()
            return
        clean_name = menu_name.strip()
        if not clean_name:
            print("[ERROR] Nama menu tidak boleh kosong.")
            continue
        existing_names = menu_df['nama_menu'].astype(str).str.lower().values if not menu_df.empty else []
        if clean_name.lower() in existing_names:
            print(f"[ERROR] Menu '{clean_name}' sudah ada di katalog.")
            continue
        break

    category_choice = questionary.select(
        "Pilih kategori menu:",
        choices=["1. Makanan", "2. Minuman", "0. Batal"]
    ).ask()

    if category_choice is None or category_choice.startswith("0"):
        print("[INFO] Penambahan menu dibatalkan.")
        pause_screen()
        return

    category = "Makanan" if category_choice.startswith("1") else "Minuman"

    while True:
        price_input = questionary.text("Masukkan harga satuan (Rp):").ask()
        if not price_input:
            print("[INFO] Penambahan menu dibatalkan.")
            pause_screen()
            return
        if not price_input.isdigit() or int(price_input) <= 0:
            print("[ERROR] Harga harus berupa angka bulat positif lebih dari 0.")
            continue
        price = int(price_input)
        break

    while True:
        stock_input = questionary.text("Masukkan jumlah stok awal:").ask()
        if not stock_input:
            print("[INFO] Penambahan menu dibatalkan.")
            pause_screen()
            return
        if not stock_input.isdigit() or int(stock_input) < 0:
            print("[ERROR] Stok harus berupa angka bulat minimal 0.")
            continue
        stock = int(stock_input)
        break

    if not questionary.confirm(f"Konfirmasi tambah menu '{clean_name}' ({category}) Rp {price:,} [Stok: {stock}]?", default=True).ask():
        print("[INFO] Penambahan menu dibatalkan.")
        pause_screen()
        return

    new_menu_id = generate_sequential_id(menu_df, 'id_menu', 'MNU')
    new_menu_row = pd.DataFrame([{
        'id_menu': new_menu_id,
        'nama_menu': clean_name,
        'kategori': category,
        'harga': price,
        'stok': stock
    }])

    menu_df = pd.concat([menu_df, new_menu_row], ignore_index=True)
    save_menu(menu_df)

    print(f"\n[OK] Menu '{clean_name}' [{new_menu_id}] berhasil ditambahkan.")
    pause_screen()

def search_menu():
    clear_screen()
    box_width = 46
    print("\n+" + "-" * box_width + "+")
    print("|" + "CARI MENU".center(box_width) + "|")
    print("+" + "-" * box_width + "+")

    menu_df = load_menu()
    if menu_df.empty:
        print("[INFO] Katalog menu kosong.")
        pause_screen()
        return

    keyword = questionary.text("Masukkan kata kunci pencarian (nama / ID):").ask()
    if keyword is None or not keyword.strip():
        print("[INFO] Pencarian dibatalkan.")
        pause_screen()
        return

    clean_keyword = keyword.strip().lower()
    id_matched   = menu_df['id_menu'].astype(str).str.lower().str.contains(clean_keyword, na=False)
    name_matched = menu_df['nama_menu'].astype(str).str.lower().str.contains(clean_keyword, na=False)
    matched_menu = menu_df[id_matched | name_matched]

    if matched_menu.empty:
        print(f"\n[INFO] Tidak ditemukan menu dengan kata kunci '{keyword}'.")
        pause_screen()
    else:
        print(f"\n[OK] Ditemukan {len(matched_menu)} menu:")
        display_menu(matched_menu)

def update_menu():
    while True:
        clear_screen()
        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "UBAH DATA & STOK MENU".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        menu_df = load_menu()
        if menu_df.empty:
            print("[INFO] Katalog menu kosong.")
            pause_screen()
            return

        selected_id = select_menu_interactive(menu_df, "Pilih menu yang ingin diubah:")
        if not selected_id:
            print("[INFO] Pembaruan menu dibatalkan.")
            pause_screen()
            return

        menu_index = menu_df['id_menu'] == selected_id

        while True:
            current_name  = menu_df.loc[menu_index, 'nama_menu'].values[0]
            current_cat   = menu_df.loc[menu_index, 'kategori'].values[0]
            current_price = menu_df.loc[menu_index, 'harga'].values[0]
            current_stock = menu_df.loc[menu_index, 'stok'].values[0]

            edit_option = questionary.select(
                f"Menu Terpilih: {current_name} [{selected_id}] - Bagian yang diubah:",
                choices=[
                    f"1. Nama Menu (Saat ini: {current_name})",
                    f"2. Kategori (Saat ini: {current_cat})",
                    f"3. Harga Satuan (Saat ini: {format_currency(current_price)})",
                    f"4. Jumlah Stok (Saat ini: {current_stock})",
                    "0. Selesai / Kembali"
                ]
            ).ask()

            if edit_option is None or edit_option.startswith("0"):
                break
            elif edit_option.startswith("1"):
                new_name = questionary.text(f"Masukkan nama baru (lama: {current_name}):").ask()
                if new_name and new_name.strip():
                    menu_df.loc[menu_index, 'nama_menu'] = new_name.strip()
                    save_menu(menu_df)
                    print("[OK] Nama menu berhasil diubah.")
                    pause_screen()
            elif edit_option.startswith("2"):
                new_cat_choice = questionary.select(
                    "Pilih kategori baru:",
                    choices=["1. Makanan", "2. Minuman"]
                ).ask()
                if new_cat_choice:
                    new_category = "Makanan" if new_cat_choice.startswith("1") else "Minuman"
                    menu_df.loc[menu_index, 'kategori'] = new_category
                    save_menu(menu_df)
                    print("[OK] Kategori berhasil diubah.")
                    pause_screen()
            elif edit_option.startswith("3"):
                new_price_input = questionary.text(f"Masukkan harga baru (lama: {current_price}):").ask()
                if new_price_input and new_price_input.isdigit() and int(new_price_input) > 0:
                    menu_df.loc[menu_index, 'harga'] = int(new_price_input)
                    save_menu(menu_df)
                    print("[OK] Harga berhasil diubah.")
                    pause_screen()
                else:
                    print("[ERROR] Harga tidak valid.")
                    pause_screen()
            elif edit_option.startswith("4"):
                new_stock_input = questionary.text(f"Masukkan stok baru (lama: {current_stock}):").ask()
                if new_stock_input and new_stock_input.isdigit() and int(new_stock_input) >= 0:
                    menu_df.loc[menu_index, 'stok'] = int(new_stock_input)
                    save_menu(menu_df)
                    print("[OK] Stok berhasil diubah.")
                    pause_screen()
                else:
                    print("[ERROR] Stok tidak valid.")
                    pause_screen()

def delete_menu():
    while True:
        clear_screen()
        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "HAPUS MENU".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        menu_df = load_menu()
        if menu_df.empty:
            print("[INFO] Katalog menu kosong.")
            pause_screen()
            return

        selected_id = select_menu_interactive(menu_df, "Pilih menu yang ingin dihapus:")
        if not selected_id:
            print("[INFO] Penghapusan menu dibatalkan.")
            pause_screen()
            return

        target_name = menu_df.loc[menu_df['id_menu'] == selected_id, 'nama_menu'].values[0]

        confirmed = questionary.confirm(f"Apakah Anda yakin ingin menghapus '{target_name}' [{selected_id}]?").ask()
        if confirmed:
            menu_df = menu_df[menu_df['id_menu'] != selected_id]
            save_menu(menu_df)
            print(f"\n[OK] Menu '{target_name}' [{selected_id}] berhasil dihapus dari katalog.")
        else:
            print("[INFO] Penghapusan menu dibatalkan.")
        pause_screen()

def manage_menu_catalog():
    while True:
        clear_screen()
        box_width = 46
        print("\n+" + "-" * box_width + "+")
        print("|" + "KELOLA KATALOG MENU".center(box_width) + "|")
        print("+" + "-" * box_width + "+")

        action_choice = questionary.select(
            "Pilih operasi katalog menu:",
            choices=[
                "1. Tampilkan Semua Menu",
                "2. Tambah Menu Baru",
                "3. Cari Menu (Nama / ID)",
                "4. Ubah Data & Stok Menu",
                "5. Hapus Menu",
                "0. Kembali ke Menu Admin"
            ]
        ).ask()

        if action_choice is None or action_choice.startswith("0"):
            break
        elif action_choice.startswith("1"):
            display_menu()
        elif action_choice.startswith("2"):
            add_menu()
        elif action_choice.startswith("3"):
            search_menu()
        elif action_choice.startswith("4"):
            update_menu()
        elif action_choice.startswith("5"):
            delete_menu()
