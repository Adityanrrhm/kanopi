import sys
from auth.auth import register, login
from admin.service import menu_admin
from user.service import menu_user

def menu_utama():
    while True:
        print("\n" + "="*35)
        print("SELAMAT DATANG DI KANOPI")
        print("="*35)
        print(" 1. Login")
        print(" 2. Registrasi Akun Baru")
        print(" 3. Keluar Aplikasi")
        print("="*35)
        
        pilihan = input("Masukkan pilihan (1/2/3): ").strip()
        
        if pilihan == '1':
            role_person = login()
            
            if role_person == 'admin':
                menu_admin()
            elif role_person == 'user':
                menu_user()
                
        elif pilihan == '2':
            register()
            
        elif pilihan == '3':
            print("\nTerima kasih telah menggunakan Kanopi Food! Sampai jumpa.")
            sys.exit()
            
        else:
            print("\n[!] Pilihan tidak valid. Silakan masukkan angka 1, 2, atau 3.")

if __name__ == "__main__":
    menu_utama()