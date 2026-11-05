# Kanopi - food Ordering System (CLI)

**Kanopi** adalah aplikasi pemesanan makanan berbasis _Command Line Interface_ (CLI) yang dibangun menggunakan bahasa pemrograman Python dan pustaka **Pandas**. Aplikasi ini menerapkan _Role-Based Access Control_ (RBAC) untuk membedakan fitur antara Admin/Pengelola dan User/Pelanggan.

---

## Fitur Utama

### auth System

- **Registrasi Akun:** Pendaftaran akun baru dengan validasi username ganda dan pembuatan ID otomatis (`USR-001`, `USR-002`, dst.).
- **Login System:** Autentikasi pengguna berdasarkan data yang tersimpan di database CSV.

### Menu Admin (Kasir / Pengelola)

- **Manajemen Menu (CRUD):** Menambah, melihat, memperbarui (harga/stok), dan menghapus data menu makanan/minuman.
- **Laporan Transaksi:** Memantau riwayat pemesanan yang masuk.

### Menu User (Pelanggan)

- **Katalog Menu:** Melihat daftar makanan/minuman yang tersedia beserta harganya.
- **Pencarian Menu:** Mencari menu berdasarkan kata kunci (nama makanan/kategori).
- **Pemesanan Otomatis:** Melakukan pemesanan dengan kalkulasi total harga otomatis dan pengurangan stok secara _real-time_.

---

## 📁 Struktur Proyek

```text
kanopi/
│
├── database/
│   ├── users.csv             # Data akun (ID, Username, Password, Role)
│   ├── menu.csv              # Data katalog makanan & minuman
│   └── riwayat_pesanan.csv   # Data transaksi pelanggan
│
├── src/
│   ├── admin/
│   │   └── service.py        # Logika & fitur khusus Admin (CRUD Menu)
│   ├── auth/
│   │   └── auth.py           # Logika Login & Registrasi (Pandas)
│   ├── user/
│   │   └── service.py        # Logika & fitur khusus User (Pemesanan & Pencarian)
│   └── main.py               # Titik masuk utama program (Routing & Navigasi)
│
├── .gitignore                # Menyaring file cache & venv
├── README.md                 # Dokumentasi proyek
└── requirements.txt          # Daftar pustaka Python yang dibutuhkan



## How to Start

* **Kloning atau Unduh Repository
git clone https://github.com/Adityanrrhm/kanopi.git
cd kanopi

* **Aktivasi venv

- Windows
python -m venv venv
venv\Scripts\activate

-Mac or Linux
python3 -m venv venv
source venv/bin/activate


* **Install Dependensi
pip install -r requirements.txt


* **Run code
python src/main.py
```
