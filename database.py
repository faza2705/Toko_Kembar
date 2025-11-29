# database.py
import sqlite3
import pandas as pd

# Inisialisasi koneksi
conn = sqlite3.connect("bee_alaska.db", check_same_thread=False)
cursor = conn.cursor()

# Buat tabel jika belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS neraca_saldo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    akun TEXT,
    debit REAL,
    kredit REAL
)
""")
conn.commit()

# Fungsi untuk menyimpan data saldo awal
def simpan_saldo(akun, debit, kredit):
    cursor.execute("""
        INSERT INTO neraca_saldo (akun, debit, kredit)
        VALUES (?, ?, ?)
    """, (akun, debit, kredit))
    conn.commit()

# Fungsi untuk mengambil data neraca saldo
def ambil_saldo_dengan_id():
    return pd.read_sql("""
        SELECT id, akun AS 'Nama Akun', debit AS 'Debit', kredit AS 'Kredit'
        FROM neraca_saldo
    """, conn)

def hapus_saldo_per_id(baris_id):
    cursor.execute("DELETE FROM neraca_saldo WHERE id = ?", (baris_id,))
    conn.commit()

# Fungsi untuk hapus semua data
def hapus_semua_saldo():
    cursor.execute("DELETE FROM neraca_saldo")
    conn.commit()

# Membuat tabel jurnal_umum jika belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS jurnal_umum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    akun TEXT,
    keterangan TEXT,
    debit REAL,
    kredit REAL
)
""")
conn.commit()

# Fungsi untuk menyimpan entri jurnal
def simpan_jurnal(tanggal, akun, keterangan, debit, kredit):
    cursor.execute("""
        INSERT INTO jurnal_umum (tanggal, akun, keterangan, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (tanggal, akun, keterangan, debit, kredit))
    conn.commit()

# Fungsi untuk mengambil seluruh jurnal sebagai DataFrame pandas
def ambil_jurnal():
    return pd.read_sql("""
        SELECT id, tanggal AS 'Tanggal', akun AS 'Nama Akun', 
               keterangan AS 'Keterangan', debit AS 'Debit', kredit AS 'Kredit' 
        FROM jurnal_umum
        ORDER BY tanggal, id
    """, conn, index_col="id")

# Fungsi hapus satu jurnal berdasarkan id
def hapus_jurnal_id(id_jurnal):
    cursor.execute("DELETE FROM jurnal_umum WHERE id = ?", (id_jurnal,))
    conn.commit()

# Fungsi hapus semua data jurnal umum
def hapus_semua_jurnal():
    cursor.execute("DELETE FROM jurnal_umum")
    conn.commit()