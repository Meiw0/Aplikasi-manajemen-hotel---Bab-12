-- ============================================
-- DATABASE APLIKASI PERHOTELAN
-- Bab 12: Aplikasi Dengan Basis Data
-- ============================================

CREATE DATABASE IF NOT EXISTS db_hotel;
USE db_hotel;

-- Tabel TAMU
CREATE TABLE tamu (
    id_tamu INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    no_identitas VARCHAR(20) NOT NULL UNIQUE,
    telepon VARCHAR(15),
    alamat TEXT,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel KAMAR
CREATE TABLE kamar (
    id_kamar INT AUTO_INCREMENT PRIMARY KEY,
    no_kamar VARCHAR(10) NOT NULL UNIQUE,
    tipe ENUM('Standard', 'Deluxe', 'Suite', 'Executive') NOT NULL,
    harga_per_malam DECIMAL(10,2) NOT NULL,
    status ENUM('Tersedia', 'Terisi', 'Maintenance') DEFAULT 'Tersedia'
);

-- Tabel GUDANG
CREATE TABLE gudang (
    id_gudang INT AUTO_INCREMENT PRIMARY KEY,
    nama_gudang VARCHAR(100) NOT NULL,
    lokasi VARCHAR(100)
);

-- Tabel BARANG
CREATE TABLE barang (
    id_barang INT AUTO_INCREMENT PRIMARY KEY,
    nama_barang VARCHAR(100) NOT NULL,
    stok INT DEFAULT 0,
    harga DECIMAL(10,2) NOT NULL,
    satuan VARCHAR(20)
);

-- Tabel STOK_GUDANG (many-to-many BARANG & GUDANG)
CREATE TABLE stok_gudang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_barang INT NOT NULL,
    id_gudang INT NOT NULL,
    jumlah INT DEFAULT 0,
    tgl_update DATE,
    FOREIGN KEY (id_barang) REFERENCES barang(id_barang) ON DELETE CASCADE,
    FOREIGN KEY (id_gudang) REFERENCES gudang(id_gudang) ON DELETE CASCADE
);

-- Tabel TRANSAKSI (check-in / check-out)
CREATE TABLE transaksi (
    id_transaksi INT AUTO_INCREMENT PRIMARY KEY,
    id_tamu INT NOT NULL,
    id_kamar INT NOT NULL,
    tgl_checkin DATE NOT NULL,
    tgl_checkout DATE,
    total_harga DECIMAL(12,2) DEFAULT 0,
    status_bayar ENUM('Belum Bayar', 'Lunas', 'Cicilan') DEFAULT 'Belum Bayar',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tamu) REFERENCES tamu(id_tamu),
    FOREIGN KEY (id_kamar) REFERENCES kamar(id_kamar)
);

-- Tabel DETAIL_KONSUMSI (barang yang dipakai tamu selama menginap)
CREATE TABLE detail_konsumsi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_transaksi INT NOT NULL,
    id_barang INT NOT NULL,
    jumlah INT NOT NULL DEFAULT 1,
    subtotal DECIMAL(10,2),
    FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi) ON DELETE CASCADE,
    FOREIGN KEY (id_barang) REFERENCES barang(id_barang)
);

-- ============================================
-- DATA SAMPLE
-- ============================================

INSERT INTO tamu (nama, no_identitas, telepon, alamat, email) VALUES
('Budi Santoso', '3374010101900001', '081234567890', 'Jl. Merdeka No.1 Semarang', 'budi@email.com'),
('Siti Rahayu', '3374020202910002', '082345678901', 'Jl. Veteran No.5 Solo', 'siti@email.com'),
('Ahmad Fauzi', '3374030303920003', '083456789012', 'Jl. Diponegoro No.10 Yogya', 'ahmad@email.com');

INSERT INTO kamar (no_kamar, tipe, harga_per_malam, status) VALUES
('101', 'Standard', 350000, 'Tersedia'),
('102', 'Standard', 350000, 'Tersedia'),
('201', 'Deluxe', 550000, 'Tersedia'),
('202', 'Deluxe', 550000, 'Terisi'),
('301', 'Suite', 1200000, 'Tersedia'),
('401', 'Executive', 2000000, 'Tersedia');

INSERT INTO gudang (nama_gudang, lokasi) VALUES
('Gudang Utama', 'Lantai B1'),
('Gudang Minuman', 'Lantai 1 Belakang');

INSERT INTO barang (nama_barang, stok, harga, satuan) VALUES
('Air Mineral 600ml', 100, 8000, 'botol'),
('Sabun Mandi', 50, 5000, 'buah'),
('Handuk Kecil', 30, 15000, 'lembar'),
('Kopi Sachet', 200, 3000, 'sachet'),
('Teh Celup', 200, 2000, 'sachet'),
('Snack Keripik', 80, 12000, 'bungkus');

INSERT INTO stok_gudang (id_barang, id_gudang, jumlah, tgl_update) VALUES
(1, 1, 50, CURDATE()), (1, 2, 50, CURDATE()),
(2, 1, 50, CURDATE()), (3, 1, 30, CURDATE()),
(4, 2, 100, CURDATE()), (5, 2, 100, CURDATE()),
(6, 2, 80, CURDATE());
