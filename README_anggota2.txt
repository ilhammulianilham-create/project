FILE ANGGOTA 2
cari_urut.py      insertion sort, bubble sort, linear search, filter rentang, binary search
laporan.py        laporan bulanan, ringkasan per lahan, laporan rentang tanggal,
                  daftar panen terurut, cari catatan panen, ekspor ke laporan/*.txt
kondisi.py        sensor tanah (simulasi), riwayat sensor, pengingat jadwal panen
menu_anggota2.py  menu untuk mencoba file di atas tanpa login
data/sensor.txt   data contoh bacaan sensor

CARA MENCOBA SENDIRI
1. Taruh semua file ini di folder yang sama dengan file Anggota 1 (storage.py, lahan.py,
   panen.py, folder data/) dan utils.py milik Anggota 3.
2. Jalankan: python menu_anggota2.py

YANG DIPAKAI DARI ANGGOTA 1 (jangan ubah nama/bentuknya tanpa memberi tahu)
lahan.muat_lahan(), lahan.perkiraan_panen(lahan)
panen.muat_panen(), panen.total_nilai(list_panen)
storage.baca_tabel(), storage.tulis_tabel(), storage.tulis_baris()
Semua nilai dari file berupa TEKS (id, luas, jumlah_kg, dst). Karena itu angka diubah
dengan utils.ke_angka(), dan id dibandingkan sebagai angka lewat cari_urut.ambil_id().

YANG DIPAKAI DARI ANGGOTA 3
utils.py: judul, menu, tabel, tabel_teks, format_angka, format_rupiah, satu_desimal,
dua_desimal, potong, konfirmasi, jeda, ke_angka, tanggal_valid, parse_tanggal,
input_angka, input_tanggal, input_teks, input_pilihan

SKEMA DATA SENSOR
id_lahan | tanggal | kelembapan | suhu
Batas: kelembapan < 40 = PERLU DISIRAM, > 80 = TERLALU BASAH, suhu > 35 = SUHU TINGGI.

ATURAN PENGINGAT PANEN
Perkiraan panen = tanggal tanam + 90 hari (lahan.perkiraan_panen).
Lahan yang sudah punya catatan panen tidak ditampilkan lagi.
