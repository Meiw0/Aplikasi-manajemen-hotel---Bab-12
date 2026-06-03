-- ============================================
-- DATABASE APLIKASI PERHOTELAN
-- Versi Sederhana (Manajemen Inti Tanpa Modul Konsumsi)
-- ============================================

CREATE DATABASE IF NOT EXISTS db_hotel;
USE db_hotel;

-- Membersihkan tabel lama agar sinkron dengan kode Python terbaru
DROP TABLE IF EXISTS detail_konsumsi;
DROP TABLE IF EXISTS stok_gudang;
DROP TABLE IF EXISTS barang;
DROP TABLE IF EXISTS gudang;
DROP TABLE IF EXISTS transaksi;
DROP TABLE IF EXISTS kamar;
DROP TABLE IF EXISTS tamu;

-- ============================================
-- PEMBUATAN TABEL
-- ============================================

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
