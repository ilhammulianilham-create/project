"""storage.py - Baca/tulis data ke file teks (.txt) berpemisah '|'.

Format tiap baris data:  kolom1|kolom2|kolom3
Baris yang diawali '#' adalah header/komentar dan dilewati saat membaca.
"""
import os

import utils as u

FOLDER_PROYEK = os.path.dirname(os.path.abspath(__file__))
FOLDER_DATA = os.path.join(FOLDER_PROYEK, "data")
FOLDER_LAPORAN = os.path.join(FOLDER_PROYEK, "laporan")
PEMISAH = "|"

FILE_LAHAN = "lahan.txt"
FILE_PANEN = "panen.txt"
FILE_SENSOR = "sensor.txt"
FILE_USER = "users.txt"

# Skema = daftar (nama_kolom, tipe_data); urutannya sama dengan urutan di file.
SKEMA_LAHAN = [
    ("id", int), ("nama", str), ("lokasi", str), ("luas_m2", float),
    ("tanaman", str), ("tanggal_tanam", str), ("umur_panen_hari", int),
    ("status", str),
]
SKEMA_PANEN = [
    ("id", int), ("id_lahan", int), ("tanaman", str), ("tanggal", str),
    ("jumlah_kg", float), ("harga_per_kg", int), ("catatan", str),
]
SKEMA_SENSOR = [
    ("id_lahan", int), ("tanggal", str), ("kelembapan", float), ("suhu", float),
]


def _jalur(nama, folder):
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, nama)


def _tulis_aman(jalur, baris):
    """Tulis ke file sementara lalu ganti, agar file asli tidak rusak jika gagal."""
    sementara = jalur + ".tmp"
    f = open(sementara, "w", encoding="utf-8")
    f.write("\n".join(baris) + "\n")
    f.close()
    os.replace(sementara, jalur)


def baca_baris(nama, folder=FOLDER_DATA):
    """Baca baris data (tanpa baris kosong dan komentar)."""
    jalur = _jalur(nama, folder)
    if not os.path.exists(jalur):
        return []
    hasil = []
    f = open(jalur, "r", encoding="utf-8")
    for baris in f:
        baris = baris.strip()
        if baris and not baris.startswith("#"):
            hasil.append(baris)
    f.close()
    return hasil


def tulis_baris(nama, baris, folder=FOLDER_DATA):
    _tulis_aman(_jalur(nama, folder), baris)


def nilai_cocok(isi, tipe):
    """True jika teks 'isi' bisa diubah ke 'tipe' (int atau float; str selalu cocok)."""
    if tipe is int:
        return u.adalah_bulat(isi.strip())
    if tipe is float:
        return u.adalah_desimal(isi.strip())
    return True


def baca_tabel(nama, skema):
    """Baca file berpemisah '|' menjadi list of dict sesuai skema."""
    hasil = []
    nomor = 0
    for baris in baca_baris(nama):
        nomor += 1
        bagian = baris.split(PEMISAH)
        if len(bagian) != len(skema):
            print("  ! {}: baris data ke-{} dilewati (jumlah kolom salah).".format(nama, nomor))
            continue
        semua_cocok = True
        for i in range(len(skema)):
            if not nilai_cocok(bagian[i], skema[i][1]):
                semua_cocok = False
        if not semua_cocok:
            print("  ! {}: baris data ke-{} dilewati (tipe data salah).".format(nama, nomor))
            continue
        item = {}
        for i in range(len(skema)):
            kolom = skema[i][0]
            tipe = skema[i][1]
            item[kolom] = tipe(bagian[i])
        hasil.append(item)
    return hasil


def tulis_tabel(nama, skema, data):
    """Simpan list of dict ke file berpemisah '|' dengan baris header."""
    nama_kolom = []
    for kolom, tipe in skema:
        nama_kolom.append(kolom)
    baris = ["# " + PEMISAH.join(nama_kolom)]
    for item in data:
        nilai = []
        for kolom, tipe in skema:
            nilai.append(str(item[kolom]))
        baris.append(PEMISAH.join(nilai))
    tulis_baris(nama, baris)


def id_berikutnya(data):
    terbesar = 0
    for item in data:
        if item["id"] > terbesar:
            terbesar = item["id"]
    return terbesar + 1
