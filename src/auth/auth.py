import os
import pandas as pd


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PATH_USERS = os.path.join(BASE_DIR, "database", "users.csv")

# Function buat register
def register():
    print("\n" + "="*35)
    print("      REGISTRASI AKUN BARU      ")
    print("="*35)
    
    username = input("Masukkan username baru : ").strip()
    password = input("Masukkan password      : ").strip()
    
    print("\nPilih Role Akun:")
    print("1. Admin (Kasir / Pemilik)")
    print("2. User (Customer / Pelanggan)")
    pilihan = input("Pilih role (1/2): ").strip()
    
    if pilihan == '1':
        role = 'admin'
    elif pilihan == '2':
        role = 'user'
    else:
        print("\n[!] Pilihan role tidak valid. Registrasi dibatalkan.")
        return

    if not os.path.exists(PATH_USERS):
        df_users = pd.DataFrame(columns=['id_user', 'username', 'password', 'role'])
    else:
        df_users = pd.read_csv(PATH_USERS)

    if not df_users.empty and username.lower() in df_users['username'].str.lower().values:
        print(f"\n[!] Gagal: Username '{username}' sudah digunakan! Silakan gunakan username lain.")
        return

    if df_users.empty:
        new_id = "USR-001"
    else:
        last_id_num = len(df_users) + 1
        new_id = f"USR-{last_id_num:03d}"

    data_baru = pd.DataFrame({
        'id_user': [new_id],
        'username': [username],
        'password': [password],
        'role': [role]
    })

    df_users = pd.concat([df_users, data_baru], ignore_index=True)
    df_users.to_csv(PATH_USERS, index=False)

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n[v] Berhasil! Akun '{username}' terdaftar dengan ID [{new_id}] sebagai '{role}'.")




# Function buat login
def login():
    print("\n=== LOGIN KANOPI FOOD ===")
    username = input("Masukkan username: ").strip()
    password = input("Masukkan password: ").strip()

    print(username)
    print(password)
    
    if not os.path.exists(PATH_USERS):
        print("[!] Belum ada data pengguna sama sekali. Silakan registrasi terlebih dahulu.")
        return None
        
    df_users = pd.read_csv(PATH_USERS)
    df_users['username'] = df_users['username'].astype(str).str.strip()
    df_users['password'] = df_users['password'].astype(str).str.strip()

    user_cocok = df_users[
        (df_users['username'].str.lower() == username.lower()) & 
        (df_users['password'] == password.lower())
    ]

    print(user_cocok)
    
    if not user_cocok.empty:
        role_user = user_cocok['role'].values[0]
        
        print(f"\n[v] Login berhasil! Selamat datang, {username}.")
        return role_user
    else:
        print("\n[!] Login gagal. Username atau password salah.")
        return None