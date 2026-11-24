"""cari_urut.py - Algoritma searching dan sorting yang ditulis manual (Anggota 2).

Sorting  : insertion sort dan bubble sort (tidak mengubah list asli).
Searching: linear search (pencocokan sebagian), filter rentang, dan binary search.

Catatan: data dari file (storage.baca_tabel) berupa teks semua, termasuk id.
Karena itu id dibandingkan sebagai angka lewat ambil_id(), bukan sebagai teks
(kalau sebagai teks, "10" akan dianggap lebih kecil dari "2").
"""


# ---------------------------------------------------------------- sorting
def _harus_geser(kiri, nilai, balik):
    if balik:
        return kiri < nilai
    return kiri > nilai


def insertion_sort(data, kunci, balik=False):
    """Urutkan dengan insertion sort.

    kunci : fungsi yang mengambil nilai pembanding dari satu elemen.
    balik : True = menurun (besar ke kecil).
    """
    hasil = list(data)
    for i in range(1, len(hasil)):
        sekarang = hasil[i]
        nilai = kunci(sekarang)
        j = i - 1
        while j >= 0 and _harus_geser(kunci(hasil[j]), nilai, balik):
            hasil[j + 1] = hasil[j]
            j -= 1
        hasil[j + 1] = sekarang
    return hasil


def bubble_sort(data, kunci, balik=False):
    """Urutkan dengan bubble sort: bandingkan dua elemen bersebelahan, tukar jika urutannya salah."""
    hasil = list(data)
    n = len(hasil)
    for i in range(n - 1):
        ada_tukar = False
        for j in range(n - 1 - i):
            kiri = kunci(hasil[j])
            kanan = kunci(hasil[j + 1])
            if balik:
                salah_urut = kiri < kanan
            else:
                salah_urut = kiri > kanan
            if salah_urut:
                sementara = hasil[j]
                hasil[j] = hasil[j + 1]
                hasil[j + 1] = sementara
                ada_tukar = True
        if not ada_tukar:
            break
    return hasil


# ---------------------------------------------------------------- searching
def cari_sebagian(data, kolom, kata):
    """Linear search: semua elemen yang kolomnya mengandung 'kata' (tanpa beda huruf)."""
    kata = kata.strip().lower()
    hasil = []
    for item in data:
        if kata in str(item[kolom]).lower():
            hasil.append(item)
    return hasil


def filter_rentang(data, kolom, awal, akhir):
    """Semua elemen yang nilai kolomnya di antara awal dan akhir (inklusif).

    Tanggal ISO (YYYY-MM-DD) bisa dibandingkan langsung sebagai teks.
    """
    hasil = []
    for item in data:
        if item[kolom] >= awal and item[kolom] <= akhir:
            hasil.append(item)
    return hasil


def binary_search(data_terurut, nilai, kunci):
    """Binary search. 'data_terurut' harus sudah naik menurut 'kunci'.

    Mengembalikan indeks elemen, atau -1 jika tidak ditemukan.
    """
    bawah = 0
    atas = len(data_terurut) - 1
    while bawah <= atas:
        tengah = (bawah + atas) // 2
        sekarang = kunci(data_terurut[tengah])
        if sekarang == nilai:
            return tengah
        if sekarang < nilai:
            bawah = tengah + 1
        else:
            atas = tengah - 1
    return -1


def ambil_id(item):
    """Fungsi kunci: nilai 'id' satu elemen sebagai angka (id yang bukan angka dianggap 0)."""
    teks = str(item["id"]).strip()
    if teks.isdigit():
        return int(teks)
    return 0


def cari_by_id(data, id_dicari):
    """Cari satu elemen berdasarkan 'id' memakai bubble sort + binary search.

    id_dicari boleh berupa teks atau angka. Mengembalikan elemennya, atau None.
    """
    teks = str(id_dicari).strip()
    if not teks.isdigit():
        return None
    terurut = bubble_sort(data, ambil_id)
    posisi = binary_search(terurut, int(teks), ambil_id)
    if posisi != -1:
        return terurut[posisi]
    return None
