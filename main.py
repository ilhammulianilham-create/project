"""main.py - Titik masuk program TaniCatat. Jalankan:  python main.py"""
from datetime import date

import auth
import kondisi
import laporan
import lahan
import panen
import utils as u


def dashboard(pengguna):
    data_lahan = lahan.muat_lahan()
    bulan_ini = date.today().strftime("%Y-%m")
    kg = 0
    rupiah = 0
    for p in panen.muat_panen():
        if p["tanggal"].startswith(bulan_ini):
            kg += p["jumlah_kg"]
            rupiah += panen.total_nilai(p)
    aktif = 0
    for l in data_lahan:
        if l["status"] == "Aktif":
            aktif += 1

    u.judul("TaniCatat - Manajemen Lahan dan Panen")
    print("  Selamat datang, {}!   ({})".format(pengguna["nama"], date.today().isoformat()))
    u.garis("-")
    print("  Lahan terdaftar : {} ({} aktif)".format(len(data_lahan), aktif))
    print("  Panen {}  : {} kg | {}".format(bulan_ini, u.format_angka(kg), u.format_rupiah(rupiah)))
    pengingat = kondisi.pengingat_mendesak()
    if pengingat:
        print("\n  PENGINGAT PANEN:")
        for teks in pengingat:
            print("   * {}".format(teks))


def menu_utama(pengguna):
    aksi = {
        "1": lahan.menu_lahan, "2": panen.menu_panen,
        "3": laporan.menu_laporan, "4": kondisi.menu_kondisi,
    }
    daftar_menu = ["Kelola lahan", "Catatan panen", "Laporan", "Kondisi lahan dan pengingat"]
    while True:
        dashboard(pengguna)
        print()
        for nomor in range(len(daftar_menu)):
            print("  {}. {}".format(nomor + 1, daftar_menu[nomor]))
        print("  0. Logout dan keluar")
        u.garis("-")
        pilihan = input("Pilih menu: ").strip()
        if pilihan == "0":
            print("\nSampai jumpa! Data sudah tersimpan di folder data/.")
            return
        if pilihan in aksi:
            aksi[pilihan]()
        else:
            print("  ! Menu tidak tersedia.")


def layar_awal():
    """Menu login/daftar. Mengembalikan dict pengguna, atau None jika keluar."""
    while True:
        pilihan = u.menu("Selamat Datang di TaniCatat", ["Login", "Daftar akun baru"],
                         label_nol="Keluar")
        if pilihan == "0":
            return None
        if pilihan == "1":
            pengguna = auth.login()
            if pengguna:
                return pengguna
            print("\n  Terlalu banyak percobaan gagal.")
        elif pilihan == "2":
            auth.daftar()
        else:
            print("  ! Menu tidak tersedia.")


def main():
    auth.pastikan_admin()
    # Satu-satunya try/except: supaya Ctrl+C tidak memunculkan pesan error merah.
    # Boleh dihapus; cukup tulis isi blok try-nya saja.
    try:
        pengguna = layar_awal()
        if pengguna:
            menu_utama(pengguna)
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram dihentikan. Data yang sudah disimpan tidak hilang.")


main()
