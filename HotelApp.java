import java.sql.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.Locale;
import java.util.Scanner;

public class HotelApp {

    static final String URL  = "jdbc:mysql://localhost:3306/db_hotel";
    static final String USER = "root";
    static final String PASS = "";
    static Scanner sc = new Scanner(System.in);
    static DateTimeFormatter FMT = DateTimeFormatter.ofPattern("dd MMMM yyyy", new Locale("id", "ID"));

    static Connection db() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASS);
    }

    static void garis() { System.out.println("-".repeat(60)); }

    static String fmtTgl(String sqlDate) {
        if (sqlDate == null) return "Masih menginap";
        return LocalDate.parse(sqlDate).format(FMT);
    }


    // ── Bagian Tamu ────────────────────────────────────────────

    static void lihatTamu() throws SQLException {
        try (Connection c = db(); Statement st = c.createStatement()) {
            ResultSet rs = st.executeQuery("SELECT id_tamu, nama, telepon FROM tamu");
            garis();
            System.out.printf("%-5s %-25s %s%n", "ID", "Nama", "Telepon");
            garis();
            while (rs.next())
                System.out.printf("%-5d %-25s %s%n",
                        rs.getInt(1), rs.getString(2), rs.getString(3));
            garis();
        }
    }

    static void tambahTamu() throws SQLException {
        System.out.print("Nama    : "); String nama = sc.nextLine();
        System.out.print("No. KTP : "); String nik  = sc.nextLine();
        System.out.print("Telepon : "); String tlp  = sc.nextLine();
        System.out.print("Alamat  : "); String adr  = sc.nextLine();
        System.out.print("Email   : "); String eml  = sc.nextLine();
        try (Connection c = db();
             PreparedStatement ps = c.prepareStatement(
                     "INSERT INTO tamu (nama,no_identitas,telepon,alamat,email) VALUES(?,?,?,?,?)",
                     Statement.RETURN_GENERATED_KEYS)) {
            ps.setString(1,nama); ps.setString(2,nik); ps.setString(3,tlp);
            ps.setString(4,adr); ps.setString(5,eml);
            ps.executeUpdate();
            ResultSet rs = ps.getGeneratedKeys();
            rs.next();
            System.out.println("✓ Tamu '" + nama + "' ditambahkan (ID: " + rs.getInt(1) + ")");
        }
    }


    // ── Bagian Kamar ───────────────────────────────────────────

    static void lihatKamar() throws SQLException {
        try (Connection c = db(); Statement st = c.createStatement()) {
            ResultSet rs = st.executeQuery(
                    "SELECT id_kamar, no_kamar, tipe, harga_per_malam FROM kamar WHERE status='Tersedia'");
            garis();
            System.out.printf("%-5s %-7s %-12s %s%n", "ID", "No", "Tipe", "Harga/Malam");
            garis();
            while (rs.next())
                System.out.printf("%-5d %-7s %-12s Rp %,.0f%n",
                        rs.getInt(1), rs.getString(2), rs.getString(3), rs.getDouble(4));
            garis();
        }
    }


    // ── Bagian Barang ──────────────────────────────────────────

    static void lihatBarang() throws SQLException {
        try (Connection c = db(); Statement st = c.createStatement()) {
            ResultSet rs = st.executeQuery(
                    "SELECT id_barang, nama_barang, stok, harga, satuan FROM barang");
            garis();
            System.out.printf("%-5s %-23s %-6s %s%n", "ID", "Nama Barang", "Stok", "Harga");
            garis();
            while (rs.next())
                System.out.printf("%-5d %-23s %-6d Rp %,.0f/%s%n",
                        rs.getInt(1), rs.getString(2), rs.getInt(3),
                        rs.getDouble(4), rs.getString(5));
            garis();
        }
    }


    // ── CHECK-IN ────────────────────────────────────────────────

    static void checkIn() throws SQLException {
        lihatTamu();
        System.out.print("\nID Tamu  : "); int idTamu  = Integer.parseInt(sc.nextLine());
        lihatKamar();
        System.out.print("ID Kamar : "); int idKamar = Integer.parseInt(sc.nextLine());
        System.out.print("Tgl masuk (YYYY-MM-DD) [kosong=hari ini]: ");
        String tglInput = sc.nextLine().trim();
        String tgl = tglInput.isEmpty() ? LocalDate.now().toString() : tglInput;

        try (Connection c = db()) {
            PreparedStatement cek = c.prepareStatement(
                    "SELECT status FROM kamar WHERE id_kamar=?");
            cek.setInt(1, idKamar);
            ResultSet rs = cek.executeQuery();
            if (!rs.next() || !rs.getString(1).equals("Tersedia")) {
                System.out.println("✗ Kamar tidak tersedia!"); return;
            }

            PreparedStatement ins = c.prepareStatement(
                    "INSERT INTO transaksi (id_tamu,id_kamar,tgl_checkin) VALUES(?,?,?)",
                    Statement.RETURN_GENERATED_KEYS);
            ins.setInt(1, idTamu); ins.setInt(2, idKamar);
            ins.setDate(3, Date.valueOf(tgl));
            ins.executeUpdate();
            ResultSet rsKey = ins.getGeneratedKeys();
            rsKey.next();
            int idTrx = rsKey.getInt(1);

            c.prepareStatement("UPDATE kamar SET status='Terisi' WHERE id_kamar=" + idKamar)
                    .executeUpdate();

            System.out.println("✓ Check-in berhasil! ID Transaksi: " + idTrx);
            System.out.println("  Tanggal masuk: " + LocalDate.parse(tgl).format(FMT));

            while (true) {
                System.out.print("\nTambah konsumsi barang? (y/n): ");
                if (!sc.nextLine().trim().equalsIgnoreCase("y")) break;

                lihatBarang();
                System.out.print("ID Barang : "); int idB = Integer.parseInt(sc.nextLine());
                System.out.print("Jumlah    : "); int qty = Integer.parseInt(sc.nextLine());

                PreparedStatement qBrg = c.prepareStatement(
                        "SELECT nama_barang, harga, stok FROM barang WHERE id_barang=?");
                qBrg.setInt(1, idB);
                ResultSet brg = qBrg.executeQuery();
                if (!brg.next() || brg.getInt("stok") < qty) {
                    System.out.println("✗ Stok tidak cukup!"); continue;
                }
                double subtotal = brg.getDouble("harga") * qty;

                PreparedStatement insK = c.prepareStatement(
                        "INSERT INTO detail_konsumsi (id_transaksi,id_barang,jumlah,subtotal) VALUES(?,?,?,?)");
                insK.setInt(1,idTrx); insK.setInt(2,idB);
                insK.setInt(3,qty); insK.setDouble(4,subtotal);
                insK.executeUpdate();

                c.prepareStatement("UPDATE barang SET stok=stok-" + qty + " WHERE id_barang=" + idB)
                        .executeUpdate();
                System.out.printf("✓ %dx %s — Rp %,.0f%n", qty, brg.getString("nama_barang"), subtotal);
            }
        }
    }


    // ── CHECK-OUT ───────────────────────────────────────────────

    static void checkOut() throws SQLException {
        try (Connection c = db(); Statement st = c.createStatement()) {
            ResultSet rs = st.executeQuery(
                    "SELECT t.id_transaksi, tm.nama, k.no_kamar, t.tgl_checkin " +
                            "FROM transaksi t JOIN tamu tm ON t.id_tamu=tm.id_tamu " +
                            "JOIN kamar k ON t.id_kamar=k.id_kamar WHERE t.tgl_checkout IS NULL");
            garis();
            System.out.printf("%-8s %-22s %-7s %s%n", "ID Trx", "Nama", "Kamar", "Check-in");
            garis();
            boolean ada = false;
            while (rs.next()) {
                ada = true;
                System.out.printf("%-8d %-22s %-7s %s%n",
                        rs.getInt(1), rs.getString(2), rs.getString(3),
                        fmtTgl(rs.getString(4)));
            }
            garis();
            if (!ada) { System.out.println("✗ Tidak ada tamu yang menginap."); return; }
        }

        System.out.print("\nID Transaksi : "); int idTrx = Integer.parseInt(sc.nextLine());
        System.out.print("Tgl checkout (YYYY-MM-DD) [kosong=hari ini]: ");
        String tglInput = sc.nextLine().trim();
        String tglOut = tglInput.isEmpty() ? LocalDate.now().toString() : tglInput;

        try (Connection c = db()) {
            PreparedStatement q = c.prepareStatement(
                    "SELECT t.tgl_checkin, k.harga_per_malam, k.id_kamar, tm.nama " +
                            "FROM transaksi t JOIN kamar k ON t.id_kamar=k.id_kamar " +
                            "JOIN tamu tm ON t.id_tamu=tm.id_tamu WHERE t.id_transaksi=?");
            q.setInt(1, idTrx);
            ResultSet trx = q.executeQuery();
            if (!trx.next()) { System.out.println("✗ Transaksi tidak ditemukan."); return; }

            LocalDate checkin  = trx.getDate("tgl_checkin").toLocalDate();
            LocalDate checkout = LocalDate.parse(tglOut);
            long durasi = Math.max(ChronoUnit.DAYS.between(checkin, checkout), 1);
            double biayaKamar = durasi * trx.getDouble("harga_per_malam");
            int idKamar = trx.getInt("id_kamar");
            String namaTamu = trx.getString("nama");

            PreparedStatement qK = c.prepareStatement(
                    "SELECT COALESCE(SUM(subtotal),0) FROM detail_konsumsi WHERE id_transaksi=?");
            qK.setInt(1, idTrx);
            ResultSet rsK = qK.executeQuery();
            rsK.next();
            double konsumsi = rsK.getDouble(1);

            double total = biayaKamar + konsumsi;
            c.prepareStatement(String.format(
                    "UPDATE transaksi SET tgl_checkout='%s', total_harga=%s, status_bayar='Lunas' WHERE id_transaksi=%d",
                    tglOut, total, idTrx)).executeUpdate();
            c.prepareStatement("UPDATE kamar SET status='Tersedia' WHERE id_kamar=" + idKamar)
                    .executeUpdate();

            System.out.println("\n╔══════════════════════════════════╗");
            System.out.println("  STRUK CHECKOUT");
            System.out.printf( "  Tamu     : %s%n", namaTamu);
            System.out.printf( "  Check-in : %s%n", checkin.format(FMT));
            System.out.printf( "  Check-out: %s%n", checkout.format(FMT));
            System.out.printf( "  Durasi   : %d malam%n", durasi);
            System.out.printf( "  Kamar    : Rp %,.0f%n", biayaKamar);
            System.out.printf( "  Konsumsi : Rp %,.0f%n", konsumsi);
            System.out.println("  ──────────────────────────────");
            System.out.printf( "  TOTAL    : Rp %,.0f%n", total);
            System.out.println("  Status   : LUNAS ✓");
            System.out.println("╚══════════════════════════════════╝");
        }
    }


    // ── Bagian Riwayat ──────────────────────────────────────────

    static void riwayat() throws SQLException {
        try (Connection c = db(); Statement st = c.createStatement()) {
            ResultSet rs = st.executeQuery(
                    "SELECT t.id_transaksi, tm.nama, k.no_kamar, t.tgl_checkin, " +
                            "t.tgl_checkout, t.total_harga, t.status_bayar " +
                            "FROM transaksi t JOIN tamu tm ON t.id_tamu=tm.id_tamu " +
                            "JOIN kamar k ON t.id_kamar=k.id_kamar ORDER BY t.id_transaksi DESC LIMIT 10");
            System.out.println("\n===== RIWAYAT TRANSAKSI (10 terakhir) =====");
            while (rs.next()) {
                System.out.printf("[%d] %s | Kamar %s%n",
                        rs.getInt(1), rs.getString(2), rs.getString(3));
                System.out.printf("     In : %s%n", fmtTgl(rs.getString("tgl_checkin")));
                System.out.printf("     Out: %s%n", fmtTgl(rs.getString("tgl_checkout")));
                System.out.printf("     Total: Rp %,.0f  |  %s%n%n",
                        rs.getDouble(6), rs.getString(7));
            }
        }
    }


    // ── Bagian Menu ─────────────────────────────────────────────

    public static void main(String[] args) {
        while (true) {
            System.out.println("\n╔══════════════════════════════╗");
            System.out.println("      MANAJEMEN HOTEL");
            System.out.println("╠══════════════════════════════╣");
            System.out.println("  1. Lihat Tamu");
            System.out.println("  2. Tambah Tamu");
            System.out.println("  3. Kamar Tersedia");
            System.out.println("  4. Check-in");
            System.out.println("  5. Check-out");
            System.out.println("  6. Riwayat Transaksi");
            System.out.println("  7. Daftar Barang");
            System.out.println("  0. Keluar");
            System.out.println("╚══════════════════════════════╝");
            System.out.print("Pilih: ");
            String pilih = sc.nextLine().trim();
            try {
                switch (pilih) {
                    case "1" -> lihatTamu();
                    case "2" -> tambahTamu();
                    case "3" -> lihatKamar();
                    case "4" -> checkIn();
                    case "5" -> checkOut();
                    case "6" -> riwayat();
                    case "7" -> lihatBarang();
                    case "0" -> { System.out.println("Sampai jumpa! 👋"); return; }
                    default  -> System.out.println("Menu tidak valid!");
                }
            } catch (Exception e) {
                System.out.println("[ERROR] " + e.getMessage());
            }
        }
    }
}
