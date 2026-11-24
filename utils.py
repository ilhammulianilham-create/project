"""utils.py - Fungsi bantu: input tervalidasi, format teks, dan tampilan tabel."""
import calendar
from datetime import date

LEBAR = 72
ANGKA = "0123456789"


#tampilan
def garis(karakter="=", panjang=LEBAR):
    print(karakter * panjang)


def judul(teks):
    print()
    garis("=")
    print(teks.upper().center(LEBAR))
    garis("=")


def menu(nama_menu, opsi, label_nol="Kembali"):
    """Cetak menu bernomor, kembalikan pilihan pengguna (string)."""
    judul(nama_menu)
    for nomor in range(len(opsi)):
        print("  {}. {}".format(nomor + 1, opsi[nomor]))
    print("  0. {}".format(label_nol))
    garis("-")
    return input("Pilih menu: ").strip()


def jeda():
    input("\nTekan Enter untuk melanjutkan...")


#string
def bersihkan_nama(teks):
    """'  kebun   cabai ' -> 'Kebun Cabai'."""
    return " ".join(teks.strip().split()).title()


def format_angka(angka):
    """Format gaya Indonesia: 1250.5 -> '1.250,5', 300.0 -> '300'."""
    bulat = round(angka)
    selisih = angka - bulat
    if selisih > -0.000001 and selisih < 0.000001:
        return "{:,}".format(int(bulat)).replace(",", ".")
    teks = "{:,.1f}".format(angka)
    return teks.replace(",", "_").replace(".", ",").replace("_", ".")


def format_rupiah(angka):
    return "Rp" + "{:,}".format(int(round(angka))).replace(",", ".")


def satu_desimal(angka):
    """35.04 -> '35.0'."""
    return "{:.1f}".format(angka)


def dua_desimal(angka):
    """0.2345 -> '0.23'."""
    return "{:.2f}".format(angka)


def potong(teks, maksimal):
    teks = str(teks)
    if len(teks) <= maksimal:
        return teks
    return teks[: maksimal - 3] + "..."


def susun_baris(isi_baris, lebar, rata_kanan):
    """Satukan satu baris tabel; kolom di 'rata_kanan' diratakan ke kanan."""
    bagian = []
    for i in range(len(isi_baris)):
        isi = isi_baris[i]
        if i in rata_kanan:
            bagian.append(isi.rjust(lebar[i]))
        else:
            bagian.append(isi.ljust(lebar[i]))
    return " | ".join(bagian)


def tabel_teks(header, baris, rata_kanan=(), maks_lebar=24):
    """Bangun tabel ASCII sebagai list string (bisa dicetak atau diekspor)."""
    sel = []
    for b in baris:
        baris_baru = []
        for isi in b:
            baris_baru.append(potong(isi, maks_lebar))
        sel.append(baris_baru)

    lebar = []
    for h in header:
        lebar.append(len(h))
    for b in sel:
        for i in range(len(b)):
            lebar[i] = max(lebar[i], len(b[i]))

    potongan = []
    for w in lebar:
        potongan.append("-" * w)
    pemisah = "-+-".join(potongan)

    hasil = [susun_baris(header, lebar, rata_kanan), pemisah]
    for b in sel:
        hasil.append(susun_baris(b, lebar, rata_kanan))
    return hasil


def tabel(header, baris, rata_kanan=(), maks_lebar=24):
    for teks in tabel_teks(header, baris, rata_kanan, maks_lebar):
        print(teks)


#cek angka
def hanya_angka(teks):
    """True jika teks tidak kosong dan semua hurufnya angka 0-9."""
    if teks == "":
        return False
    for huruf in teks:
        if huruf not in ANGKA:
            return False
    return True


def adalah_bulat(teks):
    """True jika teks bilangan bulat (boleh diawali + atau -)."""
    if teks.startswith("-") or teks.startswith("+"):
        teks = teks[1:]
    return hanya_angka(teks)


def adalah_desimal(teks):
    """True jika teks bilangan desimal dengan titik, misalnya '12.5' (boleh diawali + atau -)."""
    if teks.startswith("-") or teks.startswith("+"):
        teks = teks[1:]
    jumlah_titik = 0
    ada_angka = False
    for huruf in teks:
        if huruf == ".":
            jumlah_titik += 1
        elif huruf in ANGKA:
            ada_angka = True
        else:
            return False
    return ada_angka and jumlah_titik <= 1


#tanggal
def tanggal_valid(teks):
    """True jika teks berformat YYYY-MM-DD dan benar-benar ada di kalender."""
    bagian = teks.split("-")
    if len(bagian) != 3:
        return False
    tahun = bagian[0]
    bulan = bagian[1]
    hari = bagian[2]
    if len(tahun) != 4 or len(bulan) > 2 or len(hari) > 2:
        return False
    if not (hanya_angka(tahun) and hanya_angka(bulan) and hanya_angka(hari)):
        return False
    tahun = int(tahun)
    bulan = int(bulan)
    hari = int(hari)
    if tahun < 1 or bulan < 1 or bulan > 12:
        return False
    hari_dalam_bulan = calendar.monthrange(tahun, bulan)[1]
    return hari >= 1 and hari <= hari_dalam_bulan


def parse_tanggal(teks):
    """Ubah 'YYYY-MM-DD' menjadi objek date (teks harus lolos tanggal_valid)."""
    bagian = teks.split("-")
    return date(int(bagian[0]), int(bagian[1]), int(bagian[2]))


#input
def input_teks(prompt, lama=None, boleh_kosong=False):
    """Input teks. Jika 'lama' diberikan, Enter = pertahankan nilai lama."""
    while True:
        if lama is not None:
            tampil = "{} [{}]: ".format(prompt, lama)
        else:
            tampil = "{}: ".format(prompt)
        nilai = " ".join(input(tampil).split()).replace("|", "/")
        if nilai == "" and lama is not None:
            return str(lama)
        if nilai == "" and not boleh_kosong:
            print("  ! Input tidak boleh kosong.")
            continue
        return nilai


def input_angka(prompt, tipe=float, minimal=0, maksimal=None, lama=None):
    """Input angka (int/float) dengan batas minimal/maksimal."""
    while True:
        if lama is not None:
            tampil = "{} [{}]: ".format(prompt, lama)
        else:
            tampil = "{}: ".format(prompt)
        mentah = input(tampil).strip().replace(",", ".")
        if mentah == "" and lama is not None:
            return lama
        if tipe is int:
            valid = adalah_bulat(mentah)
        else:
            valid = adalah_desimal(mentah)
        if not valid:
            jenis = "bulat" if tipe is int else "desimal"
            print("  ! Masukkan angka {} yang valid.".format(jenis))
            continue
        nilai = tipe(mentah)
        if minimal is not None and nilai < minimal:
            print("  ! Nilai minimal {}.".format(minimal))
            continue
        if maksimal is not None and nilai > maksimal:
            print("  ! Nilai maksimal {}.".format(maksimal))
            continue
        return nilai


def input_tanggal(prompt, lama=None):
    """Input tanggal YYYY-MM-DD; '.' berarti hari ini. Mengembalikan string ISO."""
    petunjuk = "YYYY-MM-DD, '.' = hari ini"
    while True:
        tampil = "{} ({})".format(prompt, petunjuk)
        if lama:
            tampil += " [{}]: ".format(lama)
        else:
            tampil += ": "
        mentah = input(tampil).strip()
        if mentah == "" and lama:
            return lama
        if mentah == ".":
            return date.today().isoformat()
        if tanggal_valid(mentah):
            return parse_tanggal(mentah).isoformat()
        print("  ! Format tanggal salah. Contoh: 2026-10-20")


def input_pilihan(prompt, pilihan, lama=None):
    """Pilih satu dari daftar dengan mengetik nomornya."""
    daftar = ""
    for i in range(len(pilihan)):
        if i > 0:
            daftar += ", "
        daftar += "{}={}".format(i + 1, pilihan[i])
    while True:
        tampil = "{} ({})".format(prompt, daftar)
        if lama is not None:
            tampil += " [{}]: ".format(lama)
        else:
            tampil += ": "
        mentah = input(tampil).strip()
        if mentah == "" and lama is not None:
            return lama
        if hanya_angka(mentah) and int(mentah) >= 1 and int(mentah) <= len(pilihan):
            return pilihan[int(mentah) - 1]
        print("  ! Pilihan tidak tersedia.")


def konfirmasi(pertanyaan):
    while True:
        jawab = input("{} (y/n): ".format(pertanyaan)).strip().lower()
        if jawab in ("y", "ya"):
            return True
        if jawab in ("n", "t", "tidak"):
            return False
        print("  ! Jawab dengan y atau n.")
