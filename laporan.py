"""laporan.py - Laporan bulanan dan ringkasan per lahan, bisa diekspor ke .txt."""
import os
from datetime import date

import cari_urut as cu
import lahan as modul_lahan
import panen as modul_panen
import storage
import utils as u

LEBAR_BAR = 30


# ---------------------------------------------------------------- fungsi kunci sorting
def kunci_total_kg(rekap):
    return rekap[1]


def kunci_kg_lahan(ringkas):
    return ringkas[3]


def rekap_per_tanaman(daftar_panen):
    """Kembalikan list tuple (tanaman, total_kg, pendapatan, jumlah_panen), kg terbanyak dulu."""
    rekap = {}  # dict: tanaman -> [kg, rupiah, jumlah]
    for p in daftar_panen:
        nama = p["tanaman"]
        if nama not in rekap:
            rekap[nama] = [0.0, 0, 0]
        item = rekap[nama]
        item[0] += p["jumlah_kg"]
        item[1] += modul_panen.total_nilai(p)
        item[2] += 1
    tuple_rekap = []
    for nama, v in rekap.items():
        tuple_rekap.append((nama, v[0], v[1], v[2]))
    return cu.bubble_sort(tuple_rekap, kunci_total_kg, balik=True)


def grafik_bar(rekap):
    """Grafik batang teks untuk total kg tiap tanaman."""
    if not rekap:
        return []
    terbesar = 0
    for t in rekap:
        if t[1] > terbesar:
            terbesar = t[1]
    baris = []
    for nama, kg, _, _ in rekap:
        panjang = max(1, round(kg / terbesar * LEBAR_BAR))
        baris.append("  {} {} {} kg".format(
            u.potong(nama, 14).ljust(14), "#" * panjang, u.format_angka(kg)))
    return baris


def susun_laporan_bulanan(bulan, daftar_panen):
    """Susun laporan sebagai list baris teks (dipakai untuk tampil dan ekspor)."""
    data = []
    for p in daftar_panen:
        if p["tanggal"].startswith(bulan):
            data.append(p)
    garis = "=" * u.LEBAR
    baris = [garis, "LAPORAN PANEN BULAN {}".format(bulan).center(u.LEBAR),
             "Dibuat: {}".format(date.today().isoformat()).center(u.LEBAR), garis]
    if not data:
        baris.append("Tidak ada catatan panen pada bulan ini.")
        return baris
    rekap = rekap_per_tanaman(data)
    total_kg = 0
    total_rp = 0
    isi_tabel = []
    for nama, kg, rp, x in rekap:
        total_kg += kg
        total_rp += rp
        isi_tabel.append([nama, x, u.format_angka(kg), u.format_rupiah(rp)])
    baris.append("")
    baris += u.tabel_teks(
        ["Tanaman", "Panen (x)", "Total (kg)", "Pendapatan"],
        isi_tabel,
        rata_kanan=(1, 2, 3),
    )
    baris += ["", "Grafik total panen (kg):"] + grafik_bar(rekap)
    terbaik = rekap[0]
    baris += [
        "",
        "-" * u.LEBAR,
        "Jumlah catatan panen : {}".format(len(data)),
        "Total panen          : {} kg".format(u.format_angka(total_kg)),
        "Total pendapatan     : {}".format(u.format_rupiah(total_rp)),
        "Rata-rata per panen  : {} kg".format(u.format_angka(round(total_kg / len(data), 1))),
        "Tanaman terbaik      : {} ({} kg)".format(terbaik[0], u.format_angka(terbaik[1])),
        "-" * u.LEBAR,
    ]
    return baris


def susun_laporan_per_lahan(daftar_lahan, daftar_panen):
    garis = "=" * u.LEBAR
    baris = [garis, "RINGKASAN PANEN PER LAHAN".center(u.LEBAR), garis, ""]
    ringkas = []
    for l in daftar_lahan:
        jumlah_panen = 0
        kg = 0
        rp = 0
        for p in daftar_panen:
            if p["id_lahan"] == l["id"]:
                jumlah_panen += 1
                kg += p["jumlah_kg"]
                rp += modul_panen.total_nilai(p)
        per_m2 = kg / l["luas_m2"] if l["luas_m2"] else 0
        ringkas.append((l["nama"], l["tanaman"], jumlah_panen, kg, rp, per_m2))
    ringkas = cu.bubble_sort(ringkas, kunci_kg_lahan, balik=True)
    isi_tabel = []
    for n, t, x, kg, rp, pm in ringkas:
        isi_tabel.append([n, t, x, u.format_angka(kg), u.format_rupiah(rp),
                          u.dua_desimal(pm).replace(".", ",")])
    baris += u.tabel_teks(
        ["Lahan", "Tanaman", "Panen (x)", "Total (kg)", "Pendapatan", "kg/m2"],
        isi_tabel,
        rata_kanan=(2, 3, 4, 5),
    )
    return baris


def ekspor(nama_file, baris):
    os.makedirs(storage.FOLDER_LAPORAN, exist_ok=True)
    jalur = os.path.join(storage.FOLDER_LAPORAN, nama_file)
    f = open(jalur, "w", encoding="utf-8")
    f.write("\n".join(baris) + "\n")
    f.close()
    print("  Laporan disimpan di: laporan/{}".format(nama_file))


def _tawarkan_ekspor(nama_file, baris):
    if u.konfirmasi("\nEkspor laporan ke file .txt?"):
        ekspor(nama_file, baris)


def laporan_bulanan():
    u.judul("Laporan Bulanan")
    while True:
        bulan = input("Bulan (YYYY-MM, '.' = bulan ini): ").strip()
        if bulan == ".":
            bulan = date.today().strftime("%Y-%m")
        if u.tanggal_valid(bulan + "-01"):
            break
        print("  ! Format salah. Contoh: 2026-10")
    baris = susun_laporan_bulanan(bulan, modul_panen.muat_panen())
    print()
    for b in baris:
        print(b)
    _tawarkan_ekspor("laporan_{}.txt".format(bulan), baris)


def laporan_per_lahan():
    u.judul("Ringkasan per Lahan")
    daftar_lahan = modul_lahan.muat_lahan()
    if not daftar_lahan:
        print("\n  (Belum ada data lahan.)")
        return
    baris = susun_laporan_per_lahan(daftar_lahan, modul_panen.muat_panen())
    print()
    for b in baris:
        print(b)
    _tawarkan_ekspor("ringkasan_per_lahan.txt", baris)



# ---------------------------------------------------------------- fitur laporan tambahan dari versi awal
def laporan_rentang():
    """Laporan panen untuk rentang tanggal tertentu."""
    u.judul("Laporan Rentang Tanggal")
    while True:
        awal = u.input_tanggal("Dari tanggal")
        akhir = u.input_tanggal("Sampai tanggal")
        if awal <= akhir:
            break
        print("  ! Tanggal awal tidak boleh setelah tanggal akhir.")
    data = cu.filter_rentang(modul_panen.muat_panen(), "tanggal", awal, akhir)
    data = cu.insertion_sort(data, lambda x: x["tanggal"])
    baris = ["=" * u.LEBAR, "LAPORAN PANEN {} s.d. {}".format(awal, akhir).center(u.LEBAR), "=" * u.LEBAR]
    total_kg = sum(x["jumlah_kg"] for x in data)
    total_rp = sum(modul_panen.total_nilai(x) for x in data)
    if not data:
        baris.append("Tidak ada catatan panen pada rentang tanggal ini.")
    else:
        baris += ["", "Tanggal | Tanaman | Jumlah (kg) | Nilai"]
        for x in data:
            baris.append("{} | {} | {} | {}".format(x["tanggal"], x["tanaman"],
                u.format_angka(x["jumlah_kg"]), u.format_rupiah(modul_panen.total_nilai(x))))
        baris += ["", "Jumlah catatan: {}".format(len(data)),
                  "Total panen: {} kg".format(u.format_angka(total_kg)),
                  "Total pendapatan: {}".format(u.format_rupiah(total_rp))]
    for teks in baris:
        print(teks)
    _tawarkan_ekspor("laporan_{}_sd_{}.txt".format(awal, akhir), baris)

def daftar_terurut():
    """Menampilkan seluruh catatan panen berdasarkan kolom dan arah pilihan."""
    u.judul("Daftar Panen Terurut")
    data = modul_panen.muat_panen()
    if not data:
        print("\n  (Belum ada catatan panen.)")
        return
    kolom = u.input_pilihan("Urutkan berdasarkan", ["Tanggal", "Jumlah (kg)", "Nilai (Rp)"])
    arah = u.input_pilihan("Arah urutan", ["Naik (kecil ke besar)", "Turun (besar ke kecil)"])
    if kolom == "Tanggal":
        kunci = lambda x: x["tanggal"]
    elif kolom == "Jumlah (kg)":
        kunci = lambda x: x["jumlah_kg"]
    else:
        kunci = modul_panen.total_nilai
    hasil = cu.insertion_sort(data, kunci, balik=arah.startswith("Turun"))
    modul_panen.tampilkan(hasil, modul_lahan.muat_lahan())

def cari_panen_lengkap():
    """Pencarian catatan berdasarkan tanaman atau nama lahan."""
    u.judul("Cari Catatan Panen")
    data = modul_panen.muat_panen()
    pilihan = u.input_pilihan("Cari berdasarkan", ["Jenis tanaman", "Nama lahan"])
    kata = u.input_teks("Kata kunci")
    if pilihan == "Jenis tanaman":
        hasil = cu.cari_sebagian(data, "tanaman", kata)
    else:
        nama = {l["id"]: l["nama"] for l in modul_lahan.muat_lahan()}
        hasil = [x for x in data if kata.lower() in nama.get(x["id_lahan"], "").lower()]
    if not hasil:
        print("\n  (Tidak ada catatan yang cocok.)")
    else:
        modul_panen.tampilkan(hasil, modul_lahan.muat_lahan())

def menu_laporan():
    aksi = {"1": laporan_bulanan, "2": laporan_per_lahan, "3": laporan_rentang,
            "4": daftar_terurut, "5": cari_panen_lengkap}
    while True:
        pilihan = u.menu("Laporan", ["Laporan panen bulanan", "Ringkasan per lahan", "Laporan rentang tanggal",
             "Daftar panen terurut", "Cari catatan panen"])
        if pilihan == "0":
            return
        if pilihan in aksi:
            aksi[pilihan]()
            u.jeda()
        else:
            print("  ! Menu tidak tersedia.")
