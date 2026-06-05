CREATE DATABASE IF NOT EXISTS db_hotel;
USE db_hotel;

DROP TABLE IF EXISTS transaksi;
DROP TABLE IF EXISTS kamar;
DROP TABLE IF EXISTS tamu;

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

-- DATA SAMPLE KAMAR (Total 16 Kamar)
INSERT INTO kamar (no_kamar, tipe, harga_per_malam, status) VALUES
('101', 'Standard', 350000, 'Tersedia'),
('102', 'Standard', 350000, 'Tersedia'),
('103', 'Deluxe', 550000, 'Tersedia'),
('104', 'Deluxe', 550000, 'Terisi'),
('105', 'Suite', 1200000, 'Tersedia'),
('106', 'Executive', 2000000, 'Tersedia'),
('107', 'Standard', 350000, 'Tersedia'),
('108', 'Standard', 350000, 'Terisi'),
('109', 'Standard', 350000, 'Tersedia'),
('110', 'Deluxe', 550000, 'Tersedia'),
('111', 'Deluxe', 550000, 'Tersedia'),
('112', 'Suite', 1200000, 'Tersedia'),
('113', 'Suite', 1200000, 'Terisi'),
('114', 'Executive', 2000000, 'Tersedia'),
('115', 'Executive', 2000000, 'Tersedia'),
('116', 'Executive', 2000000, 'Tersedia');
