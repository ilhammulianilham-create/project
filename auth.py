"""auth.py - Daftar akun dan login. Password disimpan sebagai hash PBKDF2 + garam."""
import getpass
import hashlib
import secrets

import storage
import utils as u

ITERASI = 100000
MAKS_PERCOBAAN = 3


def _hash(password, garam_hex):
    kunci = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(garam_hex), ITERASI
    )
    return kunci.hex()


def _muat_user():
    """Baca users.txt menjadi dict: username -> {garam, hash, nama}."""
    hasil = {}
    for baris in storage.baca_baris(storage.FILE_USER):
        bagian = baris.split(storage.PEMISAH)
        if len(bagian) == 4:
            username, garam, hash_pw, nama = bagian
            hasil[username] = {"garam": garam, "hash": hash_pw, "nama": nama}
    return hasil


def _simpan_user(users):
    baris = ["# username|garam|hash|nama_lengkap"]
    for username, d in users.items():
        baris.append(storage.PEMISAH.join([username, d["garam"], d["hash"], d["nama"]]))
    storage.tulis_baris(storage.FILE_USER, baris)


def _tambah_user(users, username, password, nama):
    garam = secrets.token_hex(16)
    users[username] = {"garam": garam, "hash": _hash(password, garam), "nama": nama}


def pastikan_admin():
    """Jika belum ada akun sama sekali, buat akun bawaan admin / admin123."""
    users = _muat_user()
    if not users:
        _tambah_user(users, "admin", "admin123", "Administrator")
        _simpan_user(users)


def _baca_password(prompt):
    return getpass.getpass(prompt)


def validasi_username(username):
    """Kembalikan pesan kesalahan, atau None jika username valid."""
    if len(username) < 4 or len(username) > 15:
        return "Username harus 4-15 karakter."
    if not username.isalnum():
        return "Username hanya boleh huruf dan angka (tanpa spasi/simbol)."
    return None


def validasi_password(password):
    """Kembalikan pesan kesalahan, atau None jika password cukup kuat."""
    if len(password) < 6:
        return "Password minimal 6 karakter."
    ada_huruf = False
    ada_angka = False
    for karakter in password:
        if karakter.isalpha():
            ada_huruf = True
        if karakter.isdigit():
            ada_angka = True
    if not ada_huruf or not ada_angka:
        return "Password harus mengandung huruf dan angka."
    return None


def daftar():
    u.judul("Daftar Akun Baru")
    users = _muat_user()
    while True:
        username = input("Username (4-15 huruf/angka, 0 = batal): ").strip().lower()
        if username == "0":
            return None
        pesan = validasi_username(username)
        if pesan:
            print("  !", pesan)
        elif username in users:
            print("  ! Username sudah dipakai.")
        else:
            break
    nama = u.bersihkan_nama(u.input_teks("Nama lengkap"))
    while True:
        password = _baca_password("Password (min. 6 karakter, huruf + angka): ")
        pesan = validasi_password(password)
        if pesan:
            print("  !", pesan)
            continue
        if password != _baca_password("Ulangi password: "):
            print("  ! Password tidak sama.")
            continue
        break
    _tambah_user(users, username, password, nama)
    _simpan_user(users)
    print("\nAkun '{}' berhasil dibuat. Silakan login.".format(username))
    return username


def login():
    """Minta login maksimal 3 kali. Mengembalikan dict pengguna, atau None."""
    u.judul("Login")
    users = _muat_user()
    for sisa in range(MAKS_PERCOBAAN, 0, -1):
        username = input("Username: ").strip().lower()
        password = _baca_password("Password: ")
        data = users.get(username)
        if data and secrets.compare_digest(data["hash"], _hash(password, data["garam"])):
            return {"username": username, "nama": data["nama"]}
        print("  ! Username atau password salah. Sisa percobaan: {}".format(sisa - 1))
    return None
