"""lahan.py - CRUD data lahan (Create, Read, Update, Delete) + searching/sorting."""
from datetime import timedelta

import cari_urut as cu
import storage
import utils as u

STATUS = ["Aktif", "Istirahat"]
HEADER = ["ID", "Nama Lahan", "Lokasi", "Luas (m2)", "Tanaman", "Tanam", "Est. Panen", "Status"]


# ---------------------------------------------------------------- fungsi kunci sorting
def kunci_id(lahan):
    return lahan["id"]


def kunci_nama(lahan):
    return lahan["nama"].lower()


def kunci_luas(lahan):
    return lahan["luas_m2"]


def kunci_tanggal_tanam(lahan):
    return lahan["tanggal_tanam"]


# ---------------------------------------------------------------- data
def muat_lahan():
    return storage.baca_tabel(storage.FILE_LAHAN, storage.SKEMA_LAHAN)


def simpan_lahan(data):
    storage.tulis_tabel(storage.FILE_LAHAN, storage.SKEMA_LAHAN, data)


def perkiraan_panen(lahan):
    """Tanggal perkiraan panen = tanggal tanam + umur panen. None jika data rusak."""
    if not u.tanggal_valid(lahan["tanggal_tanam"]):
        return None
    tanam = u.parse_tanggal(lahan["tanggal_tanam"])
    return tanam + timedelta(days=lahan["umur_panen_hari"])


def _baris(lahan):
    est = perkiraan_panen(lahan)
    return [
        lahan["id"], lahan["nama"], lahan["lokasi"], u.format_angka(lahan["luas_m2"]),
        lahan["tanaman"], lahan["tanggal_tanam"], est.isoformat() if est else "-",
        lahan["status"],
    ]


def tampilkan(data):
    if not data:
        print("\n  (Tidak ada data lahan.)")
        return
    baris = []
    total_luas = 0
    for l in data:
        baris.append(_baris(l))
        total_luas += l["luas_m2"]
    print()
    u.tabel(HEADER, baris, rata_kanan=(0, 3))
    print("\n  {} lahan, total luas {} m2".format(len(data), u.format_angka(total_luas)))


# ---------------------------------------------------------------- CREATE
def tambah_lahan():
    u.judul("Tambah Lahan")
    data = muat_lahan()
    while True:
        nama = u.bersihkan_nama(u.input_teks("Nama lahan"))
        sudah_ada = False
        for l in data:
            if l["nama"].lower() == nama.lower():
                sudah_ada = True
        if sudah_ada:
            print("  ! Nama lahan sudah ada, gunakan nama lain.")
        else:
            break
    lahan = {
        "id": storage.id_berikutnya(data),
        "nama": nama,
        "lokasi": u.bersihkan_nama(u.input_teks("Lokasi (dusun/blok)")),
        "luas_m2": u.input_angka("Luas (m2)", float, minimal=1),
        "tanaman": u.bersihkan_nama(u.input_teks("Jenis tanaman")),
        "tanggal_tanam": u.input_tanggal("Tanggal tanam"),
        "umur_panen_hari": u.input_angka("Umur panen (hari)", int, minimal=1, maksimal=1000),
        "status": u.input_pilihan("Status", STATUS),
    }
    data.append(lahan)
    simpan_lahan(data)
    print("\n  Lahan '{}' tersimpan dengan ID {}.".format(nama, lahan["id"]))


# ---------------------------------------------------------------- READ
def lihat_lahan():
    u.judul("Daftar Lahan")
    data = muat_lahan()
    if not data:
        print("\n  (Belum ada data lahan.)")
        return
    pilihan = u.input_pilihan(
        "Urutkan berdasarkan",
        ["ID", "Nama A-Z", "Luas terbesar", "Luas terkecil", "Tanam terbaru"],
    )
    if pilihan == "ID":
        hasil = cu.insertion_sort(data, kunci_id)
    elif pilihan == "Nama A-Z":
        hasil = cu.insertion_sort(data, kunci_nama)
    elif pilihan == "Luas terbesar":
        hasil = cu.insertion_sort(data, kunci_luas, balik=True)
    elif pilihan == "Luas terkecil":
        hasil = cu.insertion_sort(data, kunci_luas)
    else:
        hasil = cu.insertion_sort(data, kunci_tanggal_tanam, balik=True)
    tampilkan(hasil)
    jenis = set()  # set: jenis tanaman unik
    for l in data:
        jenis.add(l["tanaman"])
    daftar_jenis = list(jenis)
    daftar_jenis.sort()
    print("  Jenis tanaman: {}".format(", ".join(daftar_jenis)))


# ---------------------------------------------------------------- SEARCH
def cari_lahan_interaktif():
    u.judul("Cari Lahan")
    data = muat_lahan()
    if not data:
        print("\n  (Belum ada data lahan.)")
        return
    pilihan = u.input_pilihan("Cari berdasarkan", ["Nama", "Tanaman", "Lokasi", "ID (binary search)"])
    if pilihan == "ID (binary search)":
        id_cari = u.input_angka("ID lahan", int, minimal=1)
        ketemu = cu.cari_by_id(data, id_cari)
        if ketemu:
            tampilkan([ketemu])
        else:
            tampilkan([])
        return
    kolom = {"Nama": "nama", "Tanaman": "tanaman", "Lokasi": "lokasi"}[pilihan]
    kata = u.input_teks("Kata kunci")
    tampilkan(cu.cari_sebagian(data, kolom, kata))


# ---------------------------------------------------------------- UPDATE
def ubah_lahan():
    u.judul("Ubah Lahan")
    data = muat_lahan()
    if not data:
        print("\n  (Belum ada data lahan.)")
        return
    tampilkan(data)
    lahan = cu.cari_by_id(data, u.input_angka("\nID lahan yang diubah", int, minimal=1))
    if lahan is None:
        print("  ! ID tidak ditemukan.")
        return
    print("\n  Tekan Enter untuk mempertahankan nilai lama.")
    lahan["nama"] = u.bersihkan_nama(u.input_teks("Nama lahan", lama=lahan["nama"]))
    lahan["lokasi"] = u.bersihkan_nama(u.input_teks("Lokasi", lama=lahan["lokasi"]))
    lahan["luas_m2"] = u.input_angka("Luas (m2)", float, minimal=1, lama=lahan["luas_m2"])
    lahan["tanaman"] = u.bersihkan_nama(u.input_teks("Jenis tanaman", lama=lahan["tanaman"]))
    lahan["tanggal_tanam"] = u.input_tanggal("Tanggal tanam", lama=lahan["tanggal_tanam"])
    lahan["umur_panen_hari"] = u.input_angka(
        "Umur panen (hari)", int, minimal=1, maksimal=1000, lama=lahan["umur_panen_hari"]
    )
    lahan["status"] = u.input_pilihan("Status", STATUS, lama=lahan["status"])
    simpan_lahan(data)  # 'lahan' adalah elemen di dalam 'data', jadi perubahan ikut tersimpan
    print("\n  Data lahan berhasil diperbarui.")


# ---------------------------------------------------------------- DELETE
def hapus_lahan():
    u.judul("Hapus Lahan")
    data = muat_lahan()
    if not data:
        print("\n  (Belum ada data lahan.)")
        return
    tampilkan(data)
    lahan = cu.cari_by_id(data, u.input_angka("\nID lahan yang dihapus", int, minimal=1))
    if lahan is None:
        print("  ! ID tidak ditemukan.")
        return
    panen = storage.baca_tabel(storage.FILE_PANEN, storage.SKEMA_PANEN)
    sensor = storage.baca_tabel(storage.FILE_SENSOR, storage.SKEMA_SENSOR)

    panen_sisa = []  # catatan panen milik lahan lain
    for p in panen:
        if p["id_lahan"] != lahan["id"]:
            panen_sisa.append(p)
    sensor_sisa = []  # data sensor milik lahan lain
    for s in sensor:
        if s["id_lahan"] != lahan["id"]:
            sensor_sisa.append(s)
    n_panen = len(panen) - len(panen_sisa)
    n_sensor = len(sensor) - len(sensor_sisa)

    print("\n  Lahan '{}' punya {} catatan panen dan {} data sensor.".format(
        lahan["nama"], n_panen, n_sensor))
    if not u.konfirmasi("  Hapus lahan beserta seluruh catatannya?"):
        print("  Dibatalkan.")
        return
    lahan_sisa = []
    for l in data:
        if l["id"] != lahan["id"]:
            lahan_sisa.append(l)
    simpan_lahan(lahan_sisa)
    storage.tulis_tabel(storage.FILE_PANEN, storage.SKEMA_PANEN, panen_sisa)
    storage.tulis_tabel(storage.FILE_SENSOR, storage.SKEMA_SENSOR, sensor_sisa)
    print("  Lahan dan catatan terkait telah dihapus.")


# ---------------------------------------------------------------- menu
def menu_lahan():
    aksi = {
    "1": tambah_lahan,
    "2": lihat_lahan,
    "3": cari_lahan_interaktif,
    "4": ubah_lahan,
    "5": hapus_lahan,
}
    while True:
        pilihan = u.menu(
            "Kelola Lahan",
            ["Tambah lahan", "Lihat daftar lahan", "Cari lahan", "Ubah lahan", "Hapus lahan"],
        )
        if pilihan == "0":
            return
        if pilihan in aksi:
            aksi[pilihan]()
            u.jeda()
        else:
            print("  ! Menu tidak tersedia.")


# ---------------------------------------------------------------- kompatibilitas API versi awal
def cari_lahan(kata_kunci):
    """Pencarian lahan versi API lama; kini mencakup ID, nama, tanaman, dan lokasi."""
    kata = str(kata_kunci).lower().strip()
    return [x for x in muat_lahan() if kata in str(x["id"]).lower()
            or kata in x["nama"].lower() or kata in x["tanaman"].lower()
            or kata in x["lokasi"].lower()]

def tambah_lahan_lama(nama, lokasi, luas, tanaman, tanggal_tanam):
    """Adapter agar pemanggil lama tetap dapat menambah lahan tanpa input interaktif."""
    from datetime import datetime
    data = muat_lahan()
    nama, lokasi, tanaman = nama.strip(), lokasi.strip(), tanaman.strip()
    try:
        luas = float(luas)
        datetime.strptime(tanggal_tanam, "%Y-%m-%d")
        if not nama or not lokasi or not tanaman or luas <= 0:
            return False, "Data lahan tidak valid."
    except (TypeError, ValueError):
        return False, "Luas atau tanggal tidak valid."
    if any(x["nama"].lower() == nama.lower() for x in data):
        return False, "Nama lahan sudah ada."
    data.append({"id": storage.id_berikutnya(data), "nama": nama, "lokasi": lokasi,
                 "luas_m2": luas, "tanaman": tanaman, "tanggal_tanam": tanggal_tanam,
                 "umur_panen_hari": 90, "status": "Aktif"})
    simpan_lahan(data)
    return True, "Data lahan berhasil ditambahkan."
