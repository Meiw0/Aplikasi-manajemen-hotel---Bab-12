"""
APLIKASI MANAJEMEN HOTEL - Python + MySQL (Versi Simpel)
Bab 12: Aplikasi Dengan Basis Data
pip install mysql-connector-python
"""

import mysql.connector
from datetime import date

DB = dict(host='localhost', user='root', password='', database='db_hotel')

def db():
    return mysql.connector.connect(**DB)

def tabel(header, rows):
    print("\n" + "-" * 60)
    print(header)
    print("-" * 60)
    for r in rows:
        print(r)
    print("-" * 60)


# ── TAMU ────────────────────────────────────────────

def lihat_tamu():
    with db() as c:
        cur = c.cursor()
        cur.execute("SELECT id_tamu, nama, telepon FROM tamu")
        tabel("ID  | Nama                 | Telepon",
              [f"{r[0]:<4}| {r[1]:<21}| {r[2]}" for r in cur])

def tambah_tamu():
    nama = input("Nama       : ")
    nik  = input("No. KTP    : ")
    tlp  = input("Telepon    : ")
    adr  = input("Alamat     : ")
    eml  = input("Email      : ")
    with db() as c:
        cur = c.cursor()
        cur.execute("INSERT INTO tamu (nama,no_identitas,telepon,alamat,email) VALUES(%s,%s,%s,%s,%s)",
                    (nama, nik, tlp, adr, eml))
        c.commit()
        print(f"✓ Tamu '{nama}' ditambahkan (ID: {cur.lastrowid})")


# ── KAMAR ───────────────────────────────────────────

def lihat_kamar():
    with db() as c:
        cur = c.cursor()
        cur.execute("SELECT id_kamar, no_kamar, tipe, harga_per_malam FROM kamar WHERE status='Tersedia'")
        tabel("ID  | No   | Tipe       | Harga/Malam",
              [f"{r[0]:<4}| {r[1]:<5}| {r[2]:<11}| Rp {r[3]:,.0f}" for r in cur])


# ── TRANSAKSI ────────────────────────────────────────

def checkin():
    lihat_tamu()
    id_tamu  = input("\nID Tamu  : ")
    lihat_kamar()
    id_kamar = input("ID Kamar : ")
    tgl      = input("Tgl masuk (YYYY-MM-DD) [kosong=hari ini]: ") or str(date.today())

    with db() as c:
        cur = c.cursor(dictionary=True)

        # Validasi kamar
        cur.execute("SELECT status, harga_per_malam FROM kamar WHERE id_kamar=%s", (id_kamar,))
        kamar = cur.fetchone()
        if not kamar or kamar['status'] != 'Tersedia':
            print("✗ Kamar tidak tersedia!"); return

        # Buat transaksi
        cur.execute("INSERT INTO transaksi (id_tamu,id_kamar,tgl_checkin) VALUES(%s,%s,%s)",
                    (id_tamu, id_kamar, tgl))
        id_trx = cur.lastrowid
        cur.execute("UPDATE kamar SET status='Terisi' WHERE id_kamar=%s", (id_kamar,))
        c.commit()
        print(f"✓ Check-in berhasil! ID Transaksi: {id_trx}")

        # Langsung tanya konsumsi
        while True:
            tambah = input("\nTambah konsumsi barang? (y/n): ").lower()
            if tambah != 'y':
                break
            lihat_barang()
            id_b = input("ID Barang : ")
            qty  = int(input("Jumlah    : "))

            cur.execute("SELECT nama_barang, harga, stok FROM barang WHERE id_barang=%s", (id_b,))
            brg = cur.fetchone()
            if not brg or brg['stok'] < qty:
                print("✗ Stok tidak cukup!"); continue

            subtotal = float(brg['harga']) * qty
            cur.execute("INSERT INTO detail_konsumsi (id_transaksi,id_barang,jumlah,subtotal) VALUES(%s,%s,%s,%s)",
                        (id_trx, id_b, qty, subtotal))
            cur.execute("UPDATE barang SET stok=stok-%s WHERE id_barang=%s", (qty, id_b))
            c.commit()
            print(f"✓ {qty}x {brg['nama_barang']} — Rp {subtotal:,.0f}")

def checkout():
    # Tampilkan tamu yang masih menginap
    with db() as c:
        cur = c.cursor()
        cur.execute("""SELECT t.id_transaksi, tm.nama, k.no_kamar, t.tgl_checkin
                       FROM transaksi t
                       JOIN tamu tm ON t.id_tamu=tm.id_tamu
                       JOIN kamar k ON t.id_kamar=k.id_kamar
                       WHERE t.tgl_checkout IS NULL""")
        rows = cur.fetchall()

    if not rows:
        print("✗ Tidak ada tamu yang menginap saat ini."); return

    tabel("ID Trx | Nama                 | Kamar | Check-in",
          [f"{r[0]:<7}| {r[1]:<21}| {r[2]:<6}| {r[3]}" for r in rows])

    id_trx = input("\nID Transaksi : ")
    tgl_out = input("Tgl checkout (YYYY-MM-DD) [kosong=hari ini]: ") or str(date.today())

    with db() as c:
        cur = c.cursor(dictionary=True)
        cur.execute("""SELECT t.tgl_checkin, k.harga_per_malam, k.id_kamar, tm.nama
                       FROM transaksi t
                       JOIN kamar k ON t.id_kamar=k.id_kamar
                       JOIN tamu tm ON t.id_tamu=tm.id_tamu
                       WHERE t.id_transaksi=%s""", (id_trx,))
        trx = cur.fetchone()

        from datetime import datetime
        checkin_d  = trx['tgl_checkin']
        checkout_d = datetime.strptime(tgl_out, '%Y-%m-%d').date()
        durasi     = max((checkout_d - checkin_d).days, 1)
        biaya_kamar = durasi * float(trx['harga_per_malam'])

        cur.execute("SELECT COALESCE(SUM(subtotal),0) AS total FROM detail_konsumsi WHERE id_transaksi=%s", (id_trx,))
        konsumsi = float(cur.fetchone()['total'])
        total    = biaya_kamar + konsumsi

        cur.execute("UPDATE transaksi SET tgl_checkout=%s, total_harga=%s, status_bayar='Lunas' WHERE id_transaksi=%s",
                    (tgl_out, total, id_trx))
        cur.execute("UPDATE kamar SET status='Tersedia' WHERE id_kamar=%s", (trx['id_kamar'],))
        c.commit()

        print(f"""
╔══════════════════════════════════╗
  STRUK CHECKOUT
  Tamu     : {trx['nama']}
  Durasi   : {durasi} malam
  Kamar    : Rp {biaya_kamar:>10,.0f}
  Konsumsi : Rp {konsumsi:>10,.0f}
  ──────────────────────────────
  TOTAL    : Rp {total:>10,.0f}
  Status   : LUNAS ✓
╚══════════════════════════════════╝""")

def lihat_transaksi():
    with db() as c:
        cur = c.cursor()
        cur.execute("""SELECT t.id_transaksi, tm.nama, k.no_kamar,
                              t.tgl_checkin, t.tgl_checkout, t.total_harga, t.status_bayar
                       FROM transaksi t
                       JOIN tamu tm ON t.id_tamu=tm.id_tamu
                       JOIN kamar k ON t.id_kamar=k.id_kamar
                       ORDER BY t.id_transaksi DESC LIMIT 10""")
        rows = cur.fetchall()
    print("\n===== RIWAYAT TRANSAKSI (10 terakhir) =====")
    for r in rows:
        out = str(r[4]) if r[4] else "Masih menginap"
        print(f"[{r[0]}] {r[1]} | Kamar {r[2]} | In: {r[3]} Out: {out}")
        print(f"     Total: Rp {r[5]:,.0f}  |  {r[6]}\n")


# ── BARANG ───────────────────────────────────────────

def lihat_barang():
    with db() as c:
        cur = c.cursor()
        cur.execute("SELECT id_barang, nama_barang, stok, harga, satuan FROM barang")
        tabel("ID  | Nama Barang           | Stok | Harga",
              [f"{r[0]:<4}| {r[1]:<22}| {r[2]:<5}| Rp {r[3]:,.0f}/{r[4]}" for r in cur])


# ── MENU ─────────────────────────────────────────────

MENU = {
    '1': ('Lihat Tamu',       lihat_tamu),
    '2': ('Tambah Tamu',      tambah_tamu),
    '3': ('Kamar Tersedia',   lihat_kamar),
    '4': ('Check-in',         checkin),
    '5': ('Check-out',        checkout),
    '6': ('Riwayat Transaksi',lihat_transaksi),
    '7': ('Daftar Barang',    lihat_barang),
}

def menu():
    while True:
        print("\n╔══════════════════════════════╗")
        print("    MANAJEMEN HOTEL")
        print("╠══════════════════════════════╣")
        for k, (label, _) in MENU.items():
            print(f"  {k}. {label}")
        print("  0. Keluar")
        print("╚══════════════════════════════╝")
        pilih = input("Pilih: ").strip()
        if pilih == '0':
            print("Sampai jumpa! 👋"); break
        elif pilih in MENU:
            MENU[pilih][1]()
        else:
            print("Menu tidak valid!")

if __name__ == '__main__':
    menu()
