"""kondisi.py - Data sensor tanah (simulasi) dan pengingat jadwal panen.

Bacaan sensor disimulasikan dengan random dan disimpan di data/sensor.txt. Struktur
datanya sengaja dibuat sama seperti keluaran perangkat IoT sungguhan (id, tanggal,
kelembapan, suhu), sehingga nanti cukup diganti sumbernya.
"""
import random
from datetime import date

import cari_urut as cu
import lahan as modul_lahan
import storage
import utils as u

BATAS_KERING = 40.0   # % kelembapan di bawah ini = perlu disiram
BATAS_BASAH = 80.0    # % kelembapan di atas ini = terlalu basah
BATAS_PANAS = 35.0    # derajat C di atas ini = suhu tinggi


# ---------------------------------------------------------------- fungsi kunci sorting
def kunci_tanggal(sensor):
    return sensor["tanggal"]


def kunci_sisa_hari(pengingat):
    return pengingat[0]


# ---------------------------------------------------------------- data
def muat_sensor():
    return storage.baca_tabel(storage.FILE_SENSOR, storage.SKEMA_SENSOR)


def simpan_sensor(data):
    storage.tulis_tabel(storage.FILE_SENSOR, storage.SKEMA_SENSOR, data)


def lahan_aktif():
    """Daftar lahan yang berstatus Aktif."""
    hasil = []
    for l in modul_lahan.muat_lahan():
        if l["status"] == "Aktif":
            hasil.append(l)
    return hasil


def peringatan(kelembapan, suhu):
    """Kembalikan list pesan peringatan; list kosong berarti kondisi normal."""
    pesan = []
    if kelembapan < BATAS_KERING:
        pesan.append("PERLU DISIRAM")
    elif kelembapan > BATAS_BASAH:
        pesan.append("TERLALU BASAH")
    if suhu > BATAS_PANAS:
        pesan.append("SUHU TINGGI")
    return pesan


def bacaan_terbaru(data_sensor):
    """Dict id_lahan -> bacaan terbaru (tanggal terbesar; yang terakhir di file menang jika sama)."""
    terbaru = {}
    for s in data_sensor:
        lama = terbaru.get(s["id_lahan"])
        if lama is None or s["tanggal"] >= lama["tanggal"]:
            terbaru[s["id_lahan"]] = s
    return terbaru


# ---------------------------------------------------------------- tampilan
def lihat_kondisi():
    u.judul("Kondisi Lahan Terbaru")
    daftar_aktif = lahan_aktif()
    if not daftar_aktif:
        print("\n  (Tidak ada lahan aktif.)")
        return
    terbaru = bacaan_terbaru(muat_sensor())
    baris = []
    perlu = 0
    for l in daftar_aktif:
        s = terbaru.get(l["id"])
        if s is None:
            baris.append([l["id"], l["nama"], "-", "-", "-", "Belum ada data sensor"])
            continue
        status = ", ".join(peringatan(s["kelembapan"], s["suhu"])) or "Normal"
        if "DISIRAM" in status:
            perlu += 1
        baris.append([l["id"], l["nama"], s["tanggal"], u.satu_desimal(s["kelembapan"]) + "%",
                      u.satu_desimal(s["suhu"]) + " C", status])
    print()
    u.tabel(["ID", "Lahan", "Tanggal", "Lembap", "Suhu", "Status"], baris,
            rata_kanan=(0, 3, 4), maks_lebar=26)
    if perlu:
        print("\n  >> {} lahan perlu disiram.".format(perlu))


def riwayat_sensor():
    u.judul("Riwayat Sensor")
    daftar_lahan = modul_lahan.muat_lahan()
    modul_lahan.tampilkan(daftar_lahan)
    lahan = cu.cari_by_id(daftar_lahan, u.input_angka("\nID lahan", int, minimal=1))
    if lahan is None:
        print("  ! ID tidak ditemukan.")
        return
    milik = []
    for s in muat_sensor():
        if s["id_lahan"] == lahan["id"]:
            milik.append(s)
    if not milik:
        print("\n  (Belum ada data sensor untuk lahan ini.)")
        return
    milik = cu.bubble_sort(milik, kunci_tanggal, balik=True)
    baris = []
    total_lembap = 0
    for s in milik:
        status = ", ".join(peringatan(s["kelembapan"], s["suhu"])) or "Normal"
        baris.append([s["tanggal"], u.satu_desimal(s["kelembapan"]) + "%",
                      u.satu_desimal(s["suhu"]) + " C", status])
        total_lembap += s["kelembapan"]
    print("\n  Lahan: {}\n".format(lahan["nama"]))
    u.tabel(["Tanggal", "Lembap", "Suhu", "Status"], baris, rata_kanan=(1, 2))
    rata = total_lembap / len(milik)
    print("\n  Rata-rata kelembapan: {}% dari {} bacaan".format(u.satu_desimal(rata), len(milik)))


# ---------------------------------------------------------------- input data
def simulasi_bacaan():
    u.judul("Simulasi Bacaan Sensor")
    daftar_aktif = lahan_aktif()
    if not daftar_aktif:
        print("\n  (Tidak ada lahan aktif.)")
        return
    data = muat_sensor()
    hari_ini = date.today().isoformat()
    for l in daftar_aktif:
        data.append({
            "id_lahan": l["id"], "tanggal": hari_ini,
            "kelembapan": round(random.uniform(20, 90), 1),
            "suhu": round(random.uniform(24, 38), 1),
        })
    simpan_sensor(data)
    print("\n  {} bacaan sensor baru dibuat untuk {}.".format(len(daftar_aktif), hari_ini))
    lihat_kondisi()


def input_manual():
    u.judul("Input Bacaan Manual")
    daftar_lahan = modul_lahan.muat_lahan()
    modul_lahan.tampilkan(daftar_lahan)
    lahan = cu.cari_by_id(daftar_lahan, u.input_angka("\nID lahan", int, minimal=1))
    if lahan is None:
        print("  ! ID tidak ditemukan.")
        return
    data = muat_sensor()
    bacaan = {
        "id_lahan": lahan["id"],
        "tanggal": u.input_tanggal("Tanggal"),
        "kelembapan": u.input_angka("Kelembapan tanah (%)", float, minimal=0, maksimal=100),
        "suhu": u.input_angka("Suhu tanah (C)", float, minimal=-10, maksimal=70),
    }
    data.append(bacaan)
    simpan_sensor(data)
    status = ", ".join(peringatan(bacaan["kelembapan"], bacaan["suhu"])) or "Normal"
    print("\n  Bacaan tersimpan. Status: {}".format(status))


# ---------------------------------------------------------------- pengingat
def hitung_pengingat():
    """List tuple (sisa_hari, lahan) untuk lahan aktif, urut dari yang paling mendesak."""
    hasil = []
    for l in modul_lahan.muat_lahan():
        est = modul_lahan.perkiraan_panen(l)
        if l["status"] == "Aktif" and est:
            hasil.append(((est - date.today()).days, l))
    return cu.insertion_sort(hasil, kunci_sisa_hari)


def teks_sisa(sisa):
    if sisa < 0:
        return "TERLAMBAT {} hari".format(-sisa)
    if sisa == 0:
        return "PANEN HARI INI"
    if sisa <= 7:
        return "Segera ({} hari lagi)".format(sisa)
    return "{} hari lagi".format(sisa)


def pengingat_mendesak(batas_hari=7):
    """Baris teks pengingat untuk dashboard (hanya yang sudah/hampir waktunya panen)."""
    hasil = []
    for sisa, l in hitung_pengingat():
        if sisa <= batas_hari:
            hasil.append("{} ({}): {}".format(l["nama"], l["tanaman"], teks_sisa(sisa)))
    return hasil


def lihat_pengingat():
    u.judul("Pengingat Jadwal Panen")
    data = hitung_pengingat()
    if not data:
        print("\n  (Tidak ada lahan aktif.)")
        return
    baris = []
    for sisa, l in data:
        baris.append([l["id"], l["nama"], l["tanaman"],
                      modul_lahan.perkiraan_panen(l).isoformat(), teks_sisa(sisa)])
    print("\n  Hari ini: {}\n".format(date.today().isoformat()))
    u.tabel(["ID", "Lahan", "Tanaman", "Est. Panen", "Keterangan"], baris, rata_kanan=(0,),
            maks_lebar=26)



# ---------------------------------------------------------------- fitur tambahan dari versi awal
def teks_status(sensor):
    """Menghasilkan status sensor dalam bentuk teks."""
    pesan = peringatan(float(sensor["kelembapan"]), float(sensor["suhu"]))
    return ", ".join(pesan) if pesan else "Normal"

def lahan_perlu_disiram():
    """Mengembalikan lahan aktif dengan bacaan terbaru yang perlu disiram."""
    terbaru = bacaan_terbaru(muat_sensor())
    hasil = []
    for l in lahan_aktif():
        sensor = terbaru.get(l["id"])
        if sensor and "DISIRAM" in teks_status(sensor):
            hasil.append(l)
    return hasil

# ---------------------------------------------------------------- menu
def menu_kondisi():
    aksi = {
        "1": lihat_kondisi, "2": riwayat_sensor, "3": simulasi_bacaan,
        "4": input_manual, "5": lihat_pengingat,
    }
    while True:
        pilihan = u.menu(
            "Kondisi Lahan dan Pengingat",
            ["Kondisi lahan terbaru", "Riwayat sensor per lahan", "Simulasi bacaan sensor",
             "Input bacaan sensor manual", "Pengingat jadwal panen"],
        )
        if pilihan == "0":
            return
        if pilihan in aksi:
            aksi[pilihan]()
            u.jeda()
        else:
            print("  ! Menu tidak tersedia.")
