"""
============================================
APLIKASI PERHOTELAN - Python + MySQL
Versi Integrasi dengan UX Check-out Dinamis
============================================
Requirement: pip install mysql-connector-python
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime


# ============================================
# KONEKSI DATABASE
# ============================================

def get_connection():
    """Membuat koneksi ke database MySQL"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Sesuaikan dengan password MySQL Anda
            database='db_hotel'
        )
        return conn
    except Error as e:
        print(f"[ERROR] Koneksi gagal: {e}")
        return None


# ============================================
# MODUL TAMU
# ============================================

def lihat_semua_tamu():
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tamu ORDER BY id_tamu")
        rows = cur.fetchall()
        print("\n===== DAFTAR TAMU =====")
        print(f"{'ID':<5} {'Nama':<20} {'No. Identitas':<20} {'Telepon':<15} {'Email'}")
        print("-" * 75)
        for r in rows:
            print(f"{r['id_tamu']:<5} {r['nama']:<20} {r['no_identitas']:<20} {r['telepon']:<15} {r['email']}")
    except Error as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()


def update_tamu(id_tamu, telepon=None, alamat=None, email=None):
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        updates = []
        vals = []
        if telepon:
            updates.append("telepon = %s");
            vals.append(telepon)
        if alamat:
            updates.append("alamat = %s");
            vals.append(alamat)
        if email:
            updates.append("email = %s");
            vals.append(email)
        if not updates:
            print("[INFO] Tidak ada data yang diupdate.")
            return

        vals.append(id_tamu)
        sql = f"UPDATE tamu SET {', '.join(updates)} WHERE id_tamu = %s"
        cur.execute(sql, vals)
        conn.commit()
        print(f"[OK] Data tamu ID {id_tamu} berhasil diupdate.")
    except Error as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()


def hapus_tamu(id_tamu):
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tamu WHERE id_tamu = %s", (id_tamu,))
        conn.commit()
        print(f"[OK] Tamu ID {id_tamu} berhasil dihapus.")
    except Error as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()


# ============================================
# MODUL KAMAR
# ============================================

def lihat_kamar_tersedia():
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM kamar WHERE status = 'Tersedia' ORDER BY no_kamar")
        rows = cur.fetchall()
        print("\n===== KAMAR TERSEDIA =====")
        print(f"{'ID':<5} {'No. Kamar':<12} {'Tipe':<12} {'Harga/Malam':<15} {'Status'}")
        print("-" * 60)
        for r in rows:
            print(
                f"{r['id_kamar']:<5} {r['no_kamar']:<12} {r['tipe']:<12} Rp{r['harga_per_malam']:>10,.0f}  {r['status']}")
    except Error as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()


# ============================================
# MODUL TRANSAKSI
# ============================================

def checkin_tamu_baru(nama, no_identitas, telepon, alamat, email, id_kamar, tgl_checkin):
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()

        cur.execute("SELECT status FROM kamar WHERE id_kamar = %s", (id_kamar,))
        kamar = cur.fetchone()

        if not kamar:
            print("[ERROR] Kamar tidak ditemukan.")
            return
        if kamar[0] != 'Tersedia':
            print(f"[ERROR] Kamar tidak tersedia (Status saat ini: {kamar[0]}).")
            return

        sql_tamu = """INSERT INTO tamu (nama, no_identitas, telepon, alamat, email)
                      VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(sql_tamu, (nama, no_identitas, telepon, alamat, email))
        id_tamu_baru = cur.lastrowid

        sql_trx = """INSERT INTO transaksi (id_tamu, id_kamar, tgl_checkin)
                     VALUES (%s, %s, %s)"""
        cur.execute(sql_trx, (id_tamu_baru, id_kamar, tgl_checkin))
        id_transaksi_baru = cur.lastrowid

        cur.execute("UPDATE kamar SET status = 'Terisi' WHERE id_kamar = %s", (id_kamar,))

        conn.commit()

        print(f"\n[OK] PROSES REGRISTRASI & CHECK-IN BERHASIL!")
        print(f"     ID Tamu Baru   : {id_tamu_baru} ({nama})")
        print(f"     ID Transaksi   : {id_transaksi_baru}")
        return id_transaksi_baru

    except Error as e:
        conn.rollback()
        print(f"[ERROR] Transaksi gagal dan dibatalkan (rollback). Detail: {e}")
    finally:
        conn.close()


def lihat_tamu_menginap():
    """Fungsi khusus untuk menampilkan tamu yang belum check-out"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor(dictionary=True)
        # Mengambil transaksi yang tgl_checkout-nya bernilai NULL
        cur.execute("""SELECT t.id_transaksi, tm.nama, k.no_kamar, k.tipe, t.tgl_checkin
                       FROM transaksi t
                                JOIN tamu tm ON t.id_tamu = tm.id_tamu
                                JOIN kamar k ON t.id_kamar = k.id_kamar
                       WHERE t.tgl_checkout IS NULL
                       ORDER BY t.tgl_checkin ASC""")
        rows = cur.fetchall()

        if not rows:
            print("\n[INFO] Saat ini tidak ada tamu yang sedang menginap (Semua sudah Check-out).")
            return False

        print("\n===== DAFTAR TAMU YANG SEDANG MENGINAP =====")
        print(f"{'ID Trx':<8} {'Nama Tamu':<22} {'Kamar':<10} {'Tipe':<12} {'Tgl Check-in'}")
        print("-" * 70)
        for r in rows:
            tgl_in_str = r['tgl_checkin'].strftime("%d-%m-%Y") if r['tgl_checkin'] else '-'
            print(f"{r['id_transaksi']:<8} {r['nama']:<22} {r['no_kamar']:<10} {r['tipe']:<12} {tgl_in_str}")
        return True
    except Error as e:
        print(f"[ERROR] {e}")
        return False
    finally:
        conn.close()


def checkout(id_transaksi, tgl_checkout):
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""SELECT t.*, k.harga_per_malam, k.id_kamar
                       FROM transaksi t
                                JOIN kamar k ON t.id_kamar = k.id_kamar
                       WHERE t.id_transaksi = %s
                         AND t.tgl_checkout IS NULL""", (id_transaksi,))
        trx = cur.fetchone()

        if not trx:
            print("[ERROR] Transaksi tidak ditemukan atau tamu sudah melakukan Check-out sebelumnya.")
            return

        checkin_date = trx['tgl_checkin']
        if isinstance(checkin_date, str):
            checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        if isinstance(tgl_checkout, str):
            tgl_checkout = datetime.strptime(tgl_checkout, '%Y-%m-%d').date()

        durasi = (tgl_checkout - checkin_date).days
        if durasi <= 0:
            durasi = 1

        biaya_kamar = durasi * float(trx['harga_per_malam'])
        total = biaya_kamar

        cur2 = conn.cursor()
        cur2.execute("""UPDATE transaksi
                        SET tgl_checkout = %s,
                            total_harga  = %s,
                            status_bayar = 'Lunas'
                        WHERE id_transaksi = %s""",
                     (tgl_checkout, total, id_transaksi))
        cur2.execute("UPDATE kamar SET status = 'Tersedia' WHERE id_kamar = %s", (trx['id_kamar'],))
        conn.commit()

        tgl_in_cetak = checkin_date.strftime("%d-%m-%Y")
        tgl_out_cetak = tgl_checkout.strftime("%d-%m-%Y")

        print(f"\n===== STRUK CHECKOUT =====")
        print(f"ID Transaksi : {id_transaksi}")
        print(f"Check-in     : {tgl_in_cetak}  |  Check-out: {tgl_out_cetak}")
        print(f"Durasi       : {durasi} malam")
        print(f"Biaya kamar  : Rp {biaya_kamar:,.0f}")
        print(f"TOTAL        : Rp {total:,.0f}")
        print("Status       : LUNAS")
    except Error as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()


def lihat_transaksi():
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""SELECT t.id_transaksi,
                              tm.nama,
                              k.no_kamar,
                              k.tipe,
                              t.tgl_checkin,
                              t.tgl_checkout,
                              t.total_harga,
                              t.status_bayar
                       FROM transaksi t
                                JOIN tamu tm ON t.id_tamu = tm.id_tamu
                                JOIN kamar k ON t.id_kamar = k.id_kamar
                       ORDER BY t.id_transaksi DESC""")
        rows = cur.fetchall()
        print("\n===== RIWAYAT KESELURUHAN TRANSAKSI =====")
        for r in rows:
            tgl_in_str = r['tgl_checkin'].strftime("%d-%m-%Y") if r['tgl_checkin'] else '-'
            tgl_out_str = r['tgl_checkout'].strftime("%d-%m-%Y") if r['tgl_checkout'] else 'Masih menginap'

            print(f"[{r['id_transaksi']}] {r['nama']} | Kamar {r['no_kamar']} ({r['tipe']})")
            print(f"     In: {tgl_in_str}  Out: {tgl_out_str}")

            # Mencegah error tipe data NoneType saat memformat total harga
            harga = float(r['total_harga']) if r['total_harga'] else 0.0
            print(f"     Total: Rp {harga:,.0f}  Status: {r['status_bayar']}")
            print()
    except Error as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()


# ============================================
# MENU UTAMA (CLI)
# ============================================

def menu():
    while True:
        print("\n" + "=" * 40)
        print("   APLIKASI MANAJEMEN HOTEL")
        print("=" * 40)
        print("1. Manajemen Tamu (Lihat/Update/Hapus)")
        print("2. Cek Kamar Tersedia")
        print("3. Transaksi Kamar (Check-in/out)")
        print("0. Keluar")
        pilih = input("Pilih menu: ").strip()

        if pilih == '1':
            print("\n-- MANAJEMEN DATA TAMU -- 1.Lihat Semua 2.Update Data 3.Hapus Data")
            sub = input("Pilih opsi: ").strip()
            if sub == '1':
                lihat_semua_tamu()
            elif sub == '2':
                i = int(input("ID Tamu: "))
                tlp = input("Telepon baru (kosong=skip): ") or None
                eml = input("Email baru (kosong=skip): ") or None
                update_tamu(i, telepon=tlp, email=eml)
            elif sub == '4' or sub == '3':
                i = int(input("ID Tamu yang dihapus: "))
                hapus_tamu(i)

        elif pilih == '2':
            lihat_kamar_tersedia()

        elif pilih == '3':
            print("\n-- OPERASI TRANSAKSI -- 1.Check-in (Tamu Baru) 2.Check-out 3.Lihat Riwayat")
            sub = input("Pilih opsi: ").strip()

            if sub == '1':
                print("\n--- FORM CHECK-IN & REGISTRASI TAMU ---")
                nama = input("Nama Lengkap Tamu : ")
                nik = input("No. Identitas/NIK : ")
                tlp = input("Nomor Telepon     : ")
                adr = input("Alamat Rumah      : ")
                eml = input("Alamat Email      : ")

                print("\n--- PILIHAN KAMAR YANG TERSEDIA ---")
                lihat_kamar_tersedia()
                id_k = int(input("\nMasukkan ID Kamar Pilihan: "))

                tgl_input = input("Tanggal check-in (DD-MM-YYYY): ")
                try:
                    tgl_db = datetime.strptime(tgl_input, "%d-%m-%Y").strftime("%Y-%m-%d")
                    checkin_tamu_baru(nama, nik, tlp, adr, eml, id_k, tgl_db)
                except ValueError:
                    print("[ERROR] Format tanggal salah. Pastikan menggunakan format DD-MM-YYYY (Contoh: 30-01-2026).")

            elif sub == '2':
                print("\n--- PROSES CHECK-OUT ---")

                # PANGGIL FUNGSI UNTUK MENAMPILKAN TABEL TAMU AKTIF
                ada_tamu_aktif = lihat_tamu_menginap()

                # Jika tidak ada tamu yang sedang menginap, hentikan proses checkout dan kembali ke menu
                if not ada_tamu_aktif:
                    continue

                print("\n(Ketik '0' jika ingin membatalkan dan kembali ke menu)")
                id_trx_str = input("Masukkan ID Transaksi yang akan check-out: ")

                if id_trx_str == '0':
                    print("[INFO] Operasi check-out dibatalkan.")
                    continue

                try:
                    id_trx = int(id_trx_str)
                    tgl_input = input("Tanggal check-out (DD-MM-YYYY): ")
                    tgl_db = datetime.strptime(tgl_input, "%d-%m-%Y").strftime("%Y-%m-%d")
                    checkout(id_trx, tgl_db)
                except ValueError:
                    print("[ERROR] Masukan tidak valid. Pastikan ID menggunakan angka dan format tanggal DD-MM-YYYY.")

            elif sub == '3':
                lihat_transaksi()

        elif pilih == '0':
            print("Sampai jumpa! Sistem dinonaktifkan.")
            break
        else:
            print("[INFO] Pilihan menu tidak valid.")


if __name__ == '__main__':
    menu()