"""panen.py - CRUD catatan panen + searching/sorting."""
import cari_urut as cu
import lahan as modul_lahan
import storage
import utils as u

HEADER = ["ID", "Tanggal", "Lahan", "Tanaman", "Jumlah (kg)", "Harga/kg", "Total", "Catatan"]


# ---------------------------------------------------------------- fungsi kunci sorting
def kunci_tanggal(panen):
    return panen["tanggal"]


def kunci_jumlah(panen):
    return panen["jumlah_kg"]


def kunci_tanaman(panen):
    return panen["tanaman"].lower()


# ---------------------------------------------------------------- data
def muat_panen():
    return storage.baca_tabel(storage.FILE_PANEN, storage.SKEMA_PANEN)


def simpan_panen(data):
    storage.tulis_tabel(storage.FILE_PANEN, storage.SKEMA_PANEN, data)


def total_nilai(panen):
    return panen["jumlah_kg"] * panen["harga_per_kg"]


def tampilkan(data, daftar_lahan):
    if not data:
        print("\n  (Tidak ada catatan panen.)")
        return
    nama_lahan = {}  # dict: id -> nama
    for l in daftar_lahan:
        nama_lahan[l["id"]] = l["nama"]
    baris = []
    kg = 0
    nilai = 0
    for p in data:
        baris.append([
            p["id"], p["tanggal"], nama_lahan.get(p["id_lahan"], "(dihapus)"), p["tanaman"],
            u.format_angka(p["jumlah_kg"]), u.format_rupiah(p["harga_per_kg"]),
            u.format_rupiah(total_nilai(p)), p["catatan"],
        ])
        kg += p["jumlah_kg"]
        nilai += total_nilai(p)
    print()
    u.tabel(HEADER, baris, rata_kanan=(0, 4, 5, 6))
    print("\n  {} catatan | {} kg | {}".format(len(data), u.format_angka(kg), u.format_rupiah(nilai)))


def _pilih_lahan(daftar_lahan):
    """Minta ID lahan sampai valid. Mengembalikan dict lahan."""
    while True:
        id_lahan = u.input_angka("ID lahan", int, minimal=1)
        lahan = cu.cari_by_id(daftar_lahan, id_lahan)
        if lahan:
            return lahan
        print("  ! ID lahan tidak ditemukan.")


def _tanggal_panen(lahan, lama=None):
    """Tanggal panen tidak boleh sebelum tanggal tanam."""
    while True:
        tanggal = u.input_tanggal("Tanggal panen", lama=lama)
        if tanggal >= lahan["tanggal_tanam"]:
            return tanggal
        print("  ! Tanggal panen tidak boleh sebelum tanggal tanam ({}).".format(lahan["tanggal_tanam"]))


# ---------------------------------------------------------------- CREATE
def tambah_panen():
    u.judul("Catat Panen")
    daftar_lahan = modul_lahan.muat_lahan()
    if not daftar_lahan:
        print("\n  Belum ada lahan. Tambahkan lahan terlebih dahulu.")
        return
    modul_lahan.tampilkan(daftar_lahan)
    print()
    lahan = _pilih_lahan(daftar_lahan)
    data = muat_panen()
    catatan = {
        "id": storage.id_berikutnya(data),
        "id_lahan": lahan["id"],
        "tanaman": lahan["tanaman"],
        "tanggal": _tanggal_panen(lahan),
        "jumlah_kg": u.input_angka("Jumlah panen (kg)", float, minimal=0.1),
        "harga_per_kg": u.input_angka("Harga jual per kg (Rp)", int, minimal=0),
        "catatan": u.input_teks("Catatan (boleh kosong)", boleh_kosong=True),
    }
    data.append(catatan)
    simpan_panen(data)
    print("\n  Panen tersimpan (ID {}), nilai {}.".format(
        catatan["id"], u.format_rupiah(total_nilai(catatan))))


# ---------------------------------------------------------------- READ
def lihat_panen():
    u.judul("Riwayat Panen")
    data = muat_panen()
    if not data:
        print("\n  (Belum ada catatan panen.)")
        return
    pilihan = u.input_pilihan(
        "Urutkan berdasarkan",
        ["Tanggal terbaru", "Tanggal terlama", "Jumlah terbanyak", "Jumlah tersedikit",
         "Nilai tertinggi", "Tanaman A-Z"],
    )
    if pilihan == "Tanggal terbaru":
        hasil = cu.bubble_sort(data, kunci_tanggal, balik=True)
    elif pilihan == "Tanggal terlama":
        hasil = cu.bubble_sort(data, kunci_tanggal)
    elif pilihan == "Jumlah terbanyak":
        hasil = cu.bubble_sort(data, kunci_jumlah, balik=True)
    elif pilihan == "Jumlah tersedikit":
        hasil = cu.bubble_sort(data, kunci_jumlah)
    elif pilihan == "Nilai tertinggi":
        hasil = cu.bubble_sort(data, total_nilai, balik=True)
    else:
        hasil = cu.bubble_sort(data, kunci_tanaman)
    tampilkan(hasil, modul_lahan.muat_lahan())


# ---------------------------------------------------------------- SEARCH
def cari_panen():
    u.judul("Cari Panen")
    data = muat_panen()
    if not data:
        print("\n  (Belum ada catatan panen.)")
        return
    pilihan = u.input_pilihan("Cari berdasarkan", ["Tanaman", "Rentang tanggal", "Catatan"])
    if pilihan == "Rentang tanggal":
        while True:
            awal = u.input_tanggal("Dari tanggal")
            akhir = u.input_tanggal("Sampai tanggal")
            if awal <= akhir:
                break
            print("  ! Tanggal awal harus sebelum atau sama dengan tanggal akhir.")
        hasil = cu.filter_rentang(data, "tanggal", awal, akhir)
    else:
        kolom = "tanaman" if pilihan == "Tanaman" else "catatan"
        hasil = cu.cari_sebagian(data, kolom, u.input_teks("Kata kunci"))
    tampilkan(cu.bubble_sort(hasil, kunci_tanggal), modul_lahan.muat_lahan())


# ---------------------------------------------------------------- UPDATE
def ubah_panen():
    u.judul("Ubah Catatan Panen")
    data = muat_panen()
    if not data:
        print("\n  (Belum ada catatan panen.)")
        return
    daftar_lahan = modul_lahan.muat_lahan()
    tampilkan(cu.bubble_sort(data, kunci_tanggal, balik=True), daftar_lahan)
    catatan = cu.cari_by_id(data, u.input_angka("\nID panen yang diubah", int, minimal=1))
    if catatan is None:
        print("  ! ID tidak ditemukan.")
        return
    lahan = cu.cari_by_id(daftar_lahan, catatan["id_lahan"])
    print("\n  Tekan Enter untuk mempertahankan nilai lama.")
    if lahan:
        catatan["tanggal"] = _tanggal_panen(lahan, lama=catatan["tanggal"])
    else:
        catatan["tanggal"] = u.input_tanggal("Tanggal panen", lama=catatan["tanggal"])
    catatan["jumlah_kg"] = u.input_angka("Jumlah panen (kg)", float, minimal=0.1, lama=catatan["jumlah_kg"])
    catatan["harga_per_kg"] = u.input_angka("Harga per kg (Rp)", int, minimal=0, lama=catatan["harga_per_kg"])
    catatan["catatan"] = u.input_teks("Catatan", lama=catatan["catatan"], boleh_kosong=True)
    simpan_panen(data)
    print("\n  Catatan panen berhasil diperbarui.")


# ---------------------------------------------------------------- DELETE
def hapus_panen():
    u.judul("Hapus Catatan Panen")
    data = muat_panen()
    if not data:
        print("\n  (Belum ada catatan panen.)")
        return
    tampilkan(cu.bubble_sort(data, kunci_tanggal, balik=True), modul_lahan.muat_lahan())
    catatan = cu.cari_by_id(data, u.input_angka("\nID panen yang dihapus", int, minimal=1))
    if catatan is None:
        print("  ! ID tidak ditemukan.")
        return
    if u.konfirmasi("  Hapus panen {} tanggal {}?".format(catatan["tanaman"], catatan["tanggal"])):
        sisa = []
        for p in data:
            if p["id"] != catatan["id"]:
                sisa.append(p)
        simpan_panen(sisa)
        print("  Catatan panen dihapus.")
    else:
        print("  Dibatalkan.")


# ---------------------------------------------------------------- menu
def menu_panen():
    aksi = {
        "1": tambah_panen, "2": lihat_panen, "3": cari_panen,
        "4": ubah_panen, "5": hapus_panen,
    }
    while True:
        pilihan = u.menu(
            "Catatan Panen",
            ["Catat panen baru", "Lihat riwayat panen", "Cari panen", "Ubah catatan", "Hapus catatan"],
        )
        if pilihan == "0":
            return
        if pilihan in aksi:
            aksi[pilihan]()
            u.jeda()
        else:
            print("  ! Menu tidak tersedia.")
