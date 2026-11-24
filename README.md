# TaniCatat (versi sesuai materi) - Manajemen Lahan dan Panen Petani

Aplikasi terminal (Python 3.8+, tanpa library tambahan, tanpa GUI, tanpa DBMS) untuk mencatat
lahan, hasil panen, kondisi tanah, dan jadwal panen. Data disimpan di file `.txt` pada folder `data/`.

Versi ini fiturnya **sama persis** dengan TaniCatat sebelumnya. Yang berubah hanya cara penulisan
kodenya: konstruksi di luar materi praktikum (lambda, comprehension, f-string, dan sejenisnya)
diganti dengan padanan yang ada di materi, supaya mudah dihafal dan dijelaskan.

## Cara menjalankan

```
cd tanicatat_materi
python main.py
```

Akun bawaan: **admin / admin123**. Akun baru bisa dibuat lewat menu *Daftar akun baru*.

## Struktur file

| File | Isi |
|---|---|
| `main.py` | Titik masuk, login, dashboard, menu utama |
| `auth.py` | Daftar akun dan login (hash PBKDF2 + garam) |
| `lahan.py` | CRUD lahan |
| `panen.py` | CRUD catatan panen |
| `laporan.py` | Laporan bulanan, ringkasan per lahan, ekspor `.txt` |
| `kondisi.py` | Data sensor tanah (simulasi) dan pengingat jadwal panen |
| `cari_urut.py` | Searching (linear, rentang, binary) dan sorting (insertion, bubble) manual |
| `storage.py` | Baca/tulis file data |
| `utils.py` | Input tervalidasi, format teks, tabel ASCII, cek angka dan tanggal |
| `data/*.txt` | `lahan.txt`, `panen.txt`, `sensor.txt`, `users.txt` |

## Perubahan dari versi pertama (untuk bahan hafalan)

| Sebelumnya | Sekarang | Contoh lokasi |
|---|---|---|
| `lambda l: l["id"]` | fungsi kecil `def kunci_id(lahan): return lahan["id"]` | `lahan.py`, `panen.py` |
| `[x for x in data if ...]` | `for` + `if` + `.append()` | `cari_urut.py`, semua modul |
| `sum(x for x in data)`, `max(...)`, `any(...)` | `for` dengan `+=` atau penanda `True/False` | `lahan.py`, `laporan.py` |
| `f"Halo {nama}"` | `"Halo {}".format(nama)` | semua modul |
| `try ... except ValueError` | pengecekan manual: `adalah_bulat`, `adalah_desimal`, `tanggal_valid` | `utils.py`, `storage.py` |
| `with open(...) as f` | `f = open(...)` lalu `f.close()` | `storage.py`, `laporan.py` |
| `merge_sort` (rekursi) | `bubble_sort` (dua `for` bersarang) | `cari_urut.py` |
| `dict.setdefault(...)` | `if nama not in dict:` lalu isi nilai awal | `laporan.py` |
| `list.extend(...)`, `sorted(...)`, `zip(...)`, `abs(...)` | `+=`, `.sort()`, indeks `range(len(...))`, `-sisa` | beberapa modul |
| `if __name__ == "__main__"` | langsung `main()` di akhir `main.py` | `main.py` |

Satu `try/except` masih ada di `main.py` agar Ctrl+C tidak memunculkan pesan error merah.
Itu tidak bisa diganti dengan pengecekan biasa. Boleh dihapus: hapus baris `try:` dan `except ...`
beserta isinya, lalu geser isi blok `try` ke kiri.

## Yang masih di luar enam materi (1-3, 5, 6, 8)

| Hal | Keterangan |
|---|---|
| `def`, `return`, parameter default (`balik=False`), argumen bernama (`minimal=1`) | Bagian materi Fungsi |
| Metode string (`.strip()`, `.split()`, `.join()`, `.title()`, `.ljust()`, `.isalpha()`, dst) | Bagian materi String |
| `open()`, `.write()`, `.close()` | Bagian materi file |
| Format angka `{:,}` dan `{:.1f}` | Hanya di `utils.py` (`format_angka`, `format_rupiah`, `satu_desimal`, `dua_desimal`) |
| `round()`, `max()`, `set()`, `list()` | Fungsi bawaan sederhana |
| Library `calendar`, `random`, `hashlib`, `secrets`, `getpass`, `os`, `datetime` | Library boleh dipakai menurut aturan tugas |

## Pemetaan ke syarat dosen

| Syarat | Lokasi penerapan |
|---|---|
| Penyimpanan di file | `storage.py`, folder `data/` |
| Create, Read, Update, Delete | `lahan.py` dan `panen.py` |
| Tipe data koleksi | list of dict (data), dict (rekap, nama lahan), set (jenis tanaman unik), tuple (hasil rekap, pengingat) |
| Fungsi | Semua fitur dipisah menjadi fungsi per modul |
| Searching | `cari_sebagian`, `filter_rentang`, `binary_search` di `cari_urut.py` |
| Sorting | `insertion_sort` (lahan, pengingat) dan `bubble_sort` (panen, laporan) di `cari_urut.py` |
| String | `bersihkan_nama`, validasi username/password, `.format()`, `tabel_teks`, `split`/`join`/`startswith` |
| Terminal, tanpa GUI/DBMS | Seluruhnya `input()` dan `print()` |
