import os
import pandas as pd

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CORE_DIR)
BASE_DIR = os.path.dirname(SRC_DIR)
DATABASE_DIR = os.path.join(BASE_DIR, "database")

USERS_PATH = os.path.join(DATABASE_DIR, "users.csv")
MENU_PATH = os.path.join(DATABASE_DIR, "menu.csv")
ORDERS_PATH = os.path.join(DATABASE_DIR, "riwayat_pesanan.csv")
ORDER_DETAILS_PATH = os.path.join(DATABASE_DIR, "detail_pesanan.csv")
REKAP_SHIFT_PATH = os.path.join(DATABASE_DIR, "rekap_shift.csv")

MENU_COLUMNS = ['id_menu', 'nama_menu', 'kategori', 'harga', 'stok']
USERS_COLUMNS = ['id_user', 'username', 'password', 'role', 'nama', 'no_hp', 'status']
ORDERS_COLUMNS = [
    'kode_pesanan', 'nama_pelanggan', 'tipe_layanan', 'total_harga',
    'status', 'metode_pembayaran', 'uang_diterima', 'kembalian',
    'id_kasir', 'shift', 'waktu'
]
ORDER_DETAILS_COLUMNS = ['kode_pesanan', 'id_menu', 'nama_menu', 'harga_satuan', 'jumlah', 'subtotal']
REKAP_SHIFT_COLUMNS = [
    'id_rekap', 'id_kasir', 'nama_kasir', 'tanggal', 'shift',
    'kas_awal', 'total_tunai', 'total_qris', 'seharusnya_laci',
    'fisik_laci', 'selisih', 'waktu_buka', 'waktu_tutup'
]

def load_menu():
    if not os.path.exists(MENU_PATH):
        default_menu = pd.DataFrame([
            {'id_menu': 'MNU-001', 'nama_menu': 'Nasi Ayam Geprek Sambal Bawang', 'kategori': 'Makanan', 'harga': 13000, 'stok': 30},
            {'id_menu': 'MNU-002', 'nama_menu': 'Nasi Ayam Bakar Madu', 'kategori': 'Makanan', 'harga': 15000, 'stok': 25},
            {'id_menu': 'MNU-003', 'nama_menu': 'Nasi Telur Dadar Krispi', 'kategori': 'Makanan', 'harga': 9000,  'stok': 35},
            {'id_menu': 'MNU-004', 'nama_menu': 'Tahu Tempe Goreng', 'kategori': 'Makanan', 'harga': 3000,  'stok': 50},
            {'id_menu': 'MNU-005', 'nama_menu': 'Es Teh Manis', 'kategori': 'Minuman', 'harga': 3000,  'stok': 60},
            {'id_menu': 'MNU-006', 'nama_menu': 'Es Jeruk Peras', 'kategori': 'Minuman', 'harga': 4000,  'stok': 40},
        ])
        default_menu.to_csv(MENU_PATH, index=False)
        return default_menu
    menu_df = pd.read_csv(MENU_PATH)
    for col in MENU_COLUMNS:
        if col not in menu_df.columns:
            menu_df[col] = ""
    menu_df['harga'] = pd.to_numeric(menu_df['harga'], errors='coerce').fillna(0).astype(int)
    menu_df['stok']  = pd.to_numeric(menu_df['stok'],  errors='coerce').fillna(0).astype(int)
    return menu_df

def save_menu(menu_df):
    menu_df.to_csv(MENU_PATH, index=False)

def load_users():
    if not os.path.exists(USERS_PATH):
        default_users = pd.DataFrame([
            {'id_user': 'USR-001', 'username': 'aditya',    'password': 'admin000000', 'role': 'admin', 'nama': 'Aditya Admin', 'no_hp': '081234567890', 'status': 'aktif'},
            {'id_user': 'USR-002', 'username': 'aditkasir', 'password': 'kasir000000', 'role': 'kasir', 'nama': 'Adit Kasir',   'no_hp': '081234567892', 'status': 'aktif'},
        ])
        default_users.to_csv(USERS_PATH, index=False)
        return default_users
    users_df = pd.read_csv(USERS_PATH, dtype=str)
    for col in USERS_COLUMNS:
        if col not in users_df.columns:
            users_df[col] = ""
    return users_df.fillna("")

def save_users(users_df):
    users_df.to_csv(USERS_PATH, index=False)

def load_orders():
    if not os.path.exists(ORDERS_PATH):
        empty_df = pd.DataFrame(columns=ORDERS_COLUMNS)
        empty_df.to_csv(ORDERS_PATH, index=False)
        return empty_df
    orders_df = pd.read_csv(ORDERS_PATH, dtype=str)
    for col in ORDERS_COLUMNS:
        if col not in orders_df.columns:
            orders_df[col] = ""
    return orders_df.fillna("")

def save_orders(orders_df):
    orders_df.to_csv(ORDERS_PATH, index=False)

def load_order_details():
    if not os.path.exists(ORDER_DETAILS_PATH):
        empty_df = pd.DataFrame(columns=ORDER_DETAILS_COLUMNS)
        empty_df.to_csv(ORDER_DETAILS_PATH, index=False)
        return empty_df
    details_df = pd.read_csv(ORDER_DETAILS_PATH, dtype=str)
    for col in ORDER_DETAILS_COLUMNS:
        if col not in details_df.columns:
            details_df[col] = ""
    return details_df.fillna("")

def save_order_details(details_df):
    details_df.to_csv(ORDER_DETAILS_PATH, index=False)

def load_rekap_shift():
    if not os.path.exists(REKAP_SHIFT_PATH):
        empty_df = pd.DataFrame(columns=REKAP_SHIFT_COLUMNS)
        empty_df.to_csv(REKAP_SHIFT_PATH, index=False)
        return empty_df
    rekap_df = pd.read_csv(REKAP_SHIFT_PATH, dtype=str)
    for col in REKAP_SHIFT_COLUMNS:
        if col not in rekap_df.columns:
            rekap_df[col] = ""
    return rekap_df.fillna("")

def save_rekap_shift(rekap_df):
    rekap_df.to_csv(REKAP_SHIFT_PATH, index=False)

