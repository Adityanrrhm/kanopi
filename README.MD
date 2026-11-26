# KANOPI — Point of Sales & Inventori Kedai Kuliner (CLI)

KANOPI adalah aplikasi kasir (*Point of Sales*) dan pengendalian stok porsi berbasis antarmuka baris perintah interaktif (*Interactive CLI*). Dirancang khusus untuk operasional UMKM kuliner model *counter-service* (kedai ayam geprek, gerai kopi, mie cepat saji, dan camilan).

Aplikasi ini menggunakan **Python 3**, **Pandas**, **Questionary**, dan **Tabulate** dengan arsitektur prosedural modular tanpa ketergantungan pada server database eksternal (menggunakan tabel flat CSV lokal).

---

## Fitur Utama

### 1. Operasional Kasir (Meja Penjualan)
- **Siklus Shift & Anti-Salah Shift:**
  - Pilihan shift kerja: **Shift Pagi** (06:00 – 14:00) dan **Shift Siang** (14:00 – 22:00).
  - Peringatan cerdas (*time-aware warning*) jika kasir membuka shift di luar jam operasional normal.
  - Input kas modal awal laci dengan dialog konfirmasi ringkas.
- **Transaksi Cepat (Direct POS):**
  - Pemilihan menu berbasis kategori (*Makanan*, *Minuman*, atau *Semua Menu*) dilengkapi indikator sisa stok dapur.
  - Validasi stok porsi *real-time* saat item dimasukkan ke keranjang.
  - Pengubahan porsi dan pembatalan item keranjang yang aman dari *overselling* (batas maksimal porsi dibatasi langsung oleh stok riil).
  - Pilihan tipe konsumsi: **Dine In (Makan di Tempat)** atau **Take Away (Bungkus)**.
  - Input nama pelanggan fleksibel (opsional, default: "Pelanggan").
  - Pembayaran **TUNAI** (validasi uang mencukupi + hitung kembalian otomatis) atau **QRIS** (konfirmasi nominal masuk rekening).
  - Mutasi pengurangan stok otomatis di `menu.csv` saat pembayaran berhasil.
  - Pencetakan struk termal resmi kedai dengan lebar presisi 50 karakter.
- **Riwayat & Cetak Ulang Struk:** Memantau transaksi hari ini dan mencetak ulang nota pelanggan.
- **Pencarian Transaksi:** Pencarian cepat berdasarkan kode pesanan (`TRX-xxx`) atau nama pelanggan (*case-insensitive*).
- **Tutup Shift & Rekonsiliasi Kas (*Blind Cash Count*):**
  - Kasir menghitung uang fisik laci tanpa melihat rekap sistem terlebih dahulu (*blind count*).
  - Sistem mengalkulasi:
    - **Seharusnya di Laci** = Kas Awal + Penjualan Tunai
    - **Selisih Kas** = Fisik Laci - Seharusnya di Laci
  - Status selisih otomatis: `[BALANCE / PAS]`, `[LEBIH / SURPLUS]`, atau `[KURANG / TEKOR]`.
  - Rekap tersimpan permanen ke `database/rekap_shift.csv` (`RKP-xxx`) untuk audit pemilik kedai.

### 2. Panel Manajerial Pemilik Kedai (Admin)
- **Manajemen Katalog Menu (CRUD):**
  - Penambahan menu baru dengan auto-ID `MNU-xxx` dan validasi nama unik.
  - Pembaruan nama menu, kategori, harga satuan, dan penambahan stok porsi.
  - Penghapusan menu dengan dialog konfirmasi aman.
  - Pencarian menu interaktif (berdasarkan ID atau nama).
- **Tata Kelola Akun Kasir:**
  - Pendaftaran kasir baru (auto-ID `USR-xxx`) dengan validasi format username, nomor HP (10-13 digit diawali 0), dan password (min 6 karakter huruf+angka).
  - Pengubahan status akun (`aktif` / `nonaktif`) untuk memblokir login staf yang cuti atau berhenti.
  - Reset password kasir langsung dari dashboard admin.
- **Laporan & Rekapitulasi Kas:**
  - Melihat seluruh histori transaksi kedai dengan waktu berformat standar Indonesia (`DD-MM-YYYY HH:MM`).
  - Filter transaksi berdasarkan tanggal tertentu (`DD-MM-YYYY`) atau berdasarkan staf kasir spesifik.
  - Ringkasan omzet kedai: total transaksi lunas vs batal, total omzet, pendapatan tunai laci, dan pendapatan QRIS.
  - **Laporan Rekap Selisih Kas Shift Kasir:** Audit fisik laci per sesi kerja kasir, mendeteksi selisih uang dengan penanda `[!]`.

---

## Struktur Direktori Proyek

```text
kanopi/
├── database/                     # Tempat penyimpanan basis data lokal flat CSV
│   ├── users.csv                 # Data akun staf kasir dan pemilik kedai
│   ├── menu.csv                  # Katalog hidangan, kategori, harga, dan stok
│   ├── riwayat_pesanan.csv       # Header transaksi penjualan kedai
│   ├── detail_pesanan.csv        # Snapshot rincian item tiap transaksi
│   └── rekap_shift.csv           # Rekonsiliasi kas shift kasir (RKP-xxx)
│
├── src/                          # Kode sumber aplikasi (arsitektur prosedural)
│   ├── core/                     # Infrastruktur utilitas & I/O CSV terpusat
│   │   ├── database.py           # Path konfigurasi, skema kolom, fungsi load/save
│   │   └── utils.py              # format_currency, fmt_date, parse_date, ID generator
│   ├── auth/
│   │   └── auth.py               # Autentikasi, buka/tutup shift, manajemen password
│   ├── kasir/
│   │   ├── kasir.py              # Dashboard harian kasir, print_receipt, search
│   │   └── order_flow.py         # Logika keranjang belanja Direct POS & checkout
│   ├── admin/
│   │   ├── admin.py              # Router dashboard utama admin
│   │   ├── catalog.py            # CRUD katalog hidangan & persediaan porsi
│   │   ├── cashiers.py           # Tata kelola staf kasir & status akun
│   │   └── reports.py            # Laporan omzet, filter transaksi, rekap shift
│   └── main.py                   # Titik masuk utama aplikasi (Entry Point)
│
├── kanopi_documentation.html     # Dokumentasi teknis lengkap & panduan arsitektur
├── requirement.txt               # Dependensi pustaka eksternal Python
└── README.md                     # Ringkasan informasi repositori
```

---

## Skema Basis Data CSV

| Berkas CSV | Entitas & Keterangan Kolom | Kunci Primer (PK) |
| :--- | :--- | :--- |
| `database/users.csv` | `id_user`, `username`, `password`, `role`, `nama`, `no_hp`, `status` | `id_user` (`USR-xxx`) |
| `database/menu.csv` | `id_menu`, `nama_menu`, `kategori`, `harga`, `stok` | `id_menu` (`MNU-xxx`) |
| `database/riwayat_pesanan.csv` | `kode_pesanan`, `nama_pelanggan`, `tipe_layanan`, `total_harga`, `status`, `metode_pembayaran`, `uang_diterima`, `kembalian`, `id_kasir`, `shift`, `waktu` | `kode_pesanan` (`TRX-YYYYMMDD-xxx`) |
| `database/detail_pesanan.csv` | `kode_pesanan`, `id_menu`, `nama_menu`, `harga_satuan`, `jumlah`, `subtotal` | Relasi FK ke `kode_pesanan` & `id_menu` |
| `database/rekap_shift.csv` | `id_rekap`, `id_kasir`, `nama_kasir`, `tanggal`, `shift`, `kas_awal`, `total_tunai`, `total_qris`, `seharusnya_laci`, `fisik_laci`, `selisih`, `waktu_buka`, `waktu_tutup` | `id_rekap` (`RKP-xxx`) |

---

## Panduan Menjalankan Sistem

### 1. Prasyarat Lingkungan
- Python versi **3.8** atau lebih baru.

### 2. Kloning & Pemasangan

```bash
# 1. Kloning repositori
git clone https://github.com/Adityanrrhm/kanopi.git
cd kanopi

# 2. Siapkan virtual environment (opsional namun disarankan)
python -m venv venv

# Aktifkan di Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Atau di Linux / macOS:
source venv/bin/activate

# 3. Pasang dependensi pustaka
pip install -r requirement.txt

# 4. Jalankan aplikasi
python src/main.py
```

### 3. Pustaka Eksternal (`requirement.txt`)
- `pandas`: Manipulasi dan pembacaan tabel data CSV.
- `questionary`: Navigasi menu terminal berbasis kursor panah keyboard.
- `tabulate`: Penyajian tabel berbingkai rapi (`rounded_outline`) dengan perataan kolom presisi.

---

## Kredensial Bawaan (*Default Seed Data*)

Jika berkas `database/users.csv` belum ada, sistem akan membuat data awal berikut secara otomatis:

| Peran Pengguna | Username | Password | Keterangan |
| :--- | :--- | :--- | :--- |
| **Admin / Pemilik Kedai** | `aditya` | `a000000` | Akses penuh manajemen menu, staf, laporan omzet, & audit shift. |
| **Kasir** | `aditkasir` | `ak000000` | Akses operasional buka/tutup shift, transaksi POS, & cetak struk. |

---

## Dokumentasi Lengkap
Dokumentasi teknis menyeluruh, kamus data, diagram vektor alur sistem (SVG), dan format tampilan terminal dapat diakses pada berkas:
- **[kanopi_documentation.html](kanopi_documentation.html)**
