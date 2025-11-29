import streamlit as st
import pandas as pd
import io 
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import locale
locale.setlocale(locale.LC_ALL, '')
from database import simpan_saldo, ambil_saldo_dengan_id, hapus_saldo_per_id, hapus_semua_saldo # Import fungsi dari database.py
from database import simpan_jurnal, ambil_jurnal, hapus_jurnal_id, hapus_semua_jurnal  # pastikan ini sudah di-import
from database import ambil_saldo_dengan_id, ambil_jurnal

st.set_page_config(page_title="Aplikasi Toko Kembar", layout="wide")

# ===== GLOBAL BURGUNDY THEME =====
st.markdown("""
    <style>

        /* Background utama seluruh halaman */
        .main {
            background-color: #f7e9ed !important;  /* pink rose sangat lembut */
        }

        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #f2d9df !important;  /* rose sedikit tua */
        }

        /* Kotak input (textbox, selectbox, dsb) */
        div[data-baseweb="input"] > input {
            background-color: #fdf6f8 !important;
            border: 1px solid #b3546a !important;  /* burgundy muda */
            border-radius: 8px !important;
        }

        button[kind="primary"], .stButton>button {
            background-color: #e03663 !important;   /* burgundy terang */
            color: white !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: 1px solid #c72b55 !important;   /* outline sedikit lebih gelap */
        }
        .stButton>button:hover {
            background-color: #ff4f7a !important;   /* lebih terang saat hover */
            transition: 0.2s;
        }

        /* Radio button text */
        .stRadio label {
            color: #7a1631 !important;  /* burgundy */
            font-weight: 600;
        }

        /* Box / container background (Card style) */
        .stMarkdown, .stContainer {
            background-color: #f7e9ed !important;  /* rose soft */
        }

        /* Judul halaman */
        h1, h2, h3, h4 {
            color: #7a1631 !important;   /* burgundy */
        }

        /* Teks lainnya */
        p, label, span {
            color: #5a0f27 !important;   /* burgundy gelap */
        }

    </style>
""", unsafe_allow_html=True)

# ===== TAMBAHAN CSS UNTUK AREA PUTIH → ROSE SOFT =====
st.markdown("""
    <style>
        /* Background area konten utama */
        .block-container {
            background-color: #f9f0f3 !important;  /* sangat lembut */
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            border-radius: 12px !important;
        }

        /* Background wrapper Streamlit */
        div[data-testid="stAppViewContainer"] {
            background-color: #f8e6eb !important;  /* rose kalem */
        }

        /* Elemen umum */
        .stMarkdown, .stContainer, .element-container {
            background-color: transparent !important;
        }

        /* Header box */
        .header-box {
            background-color: #f7e9ed !important;  /* rose */
        }

    </style>
""", unsafe_allow_html=True)

# Container horizontal antara logo & teks
col1, col2 = st.columns([1, 5])

with col1:
    st.image("pp.png", width=130)  # ganti nama file sesuai logo kamu

with col2:
    st.markdown("""
        <h1 style="margin: 5px; padding: 0; font-size: 50px; color: black;">
            TOKO KEMBAR
        </h1>
        <p style="margin: 0; padding: 0; font-size: 23px; color: black;">
            Sistem Informasi Akuntansi
        </p>
    """, unsafe_allow_html=True)

# Inisialisasi session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {"admin": "123"}
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_notification" not in st.session_state:
    st.session_state.show_notification = False
if "notification_message" not in st.session_state:
    st.session_state.notification_message = ""
if "notification_type" not in st.session_state:
    st.session_state.notification_type = "success"
if "reset_mode" not in st.session_state:
    st.session_state.reset_mode = False

# --- FUNGSI WELCOME MESSAGE (hanya muncul sebelum login) ---
def show_welcome_message():
    st.markdown("""
    <style>
        .welcome-card {
            background-color: #fff3fa;
            border: 1px solid #f0cbd6;
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 18px;
        }
        .welcome-title {
            font-size: 35px;
            font-weight: 700;
            color: #7a1631;
            margin: 0 0 6px 0;
        }
        .welcome-body {
            font-size: 23px;
            color: #5a0f27;
            line-height: 1.6;
            margin: 0;
        }
        .welcome-note {
            margin-top: 14px;
            font-size: 20px;
            color: #7a1631;
        }
    </style>

    <div class="welcome-card">
        <div class="welcome-title">⭐ Selamat Datang!</div>
        <div class="welcome-body">
            Selamat datang di <strong>Sistem Informasi Akuntansi – Toko Kembar</strong>.<br>
            Aplikasi ini dirancang untuk membantu pengelolaan transaksi, pencatatan keuangan, 
            dan penyusunan laporan secara mudah, cepat, dan akurat.
        </div>
        <div class="welcome-note">
            Silakan lanjutkan ke halaman <strong>Login</strong> untuk mulai menggunakan sistem.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- ❗ TAMPILKAN WELCOME JIKA BELUM LOGIN ---
if not st.session_state.logged_in:
    show_welcome_message()

# Fungsi untuk menampilkan notifikasi
def show_notification():
    if st.session_state.show_notification:
        notification_container = st.container()
        
        # Buat tombol close dan pesan dalam satu baris
        col1, col2 = notification_container.columns([0.95, 0.05])
        
        # Tampilkan pesan sesuai tipe
        if st.session_state.notification_type == "success":
            col1.success(st.session_state.notification_message)
        elif st.session_state.notification_type == "info":
            col1.info(st.session_state.notification_message)
        elif st.session_state.notification_type == "warning":
            col1.warning(st.session_state.notification_message)
        elif st.session_state.notification_type == "error":
            col1.error(st.session_state.notification_message)
        
        # Tombol untuk menutup notifikasi
        if col2.button("✖"):
            st.session_state.show_notification = False
            st.rerun()

# Panggil fungsi notifikasi di awal aplikasi
show_notification()

#Reset Password
def reset_password():
    st.sidebar.subheader("Reset Password")

    username = st.sidebar.text_input("Username yang direset")
    new_pass = st.sidebar.text_input("Password Baru", type="password")
    confirm_pass = st.sidebar.text_input("Konfirmasi Password Baru", type="password")

    if st.sidebar.button("← Kembali ke Login"):
        st.session_state.reset_mode = False
        st.rerun()

    if st.sidebar.button("Reset Password"):
        if username not in st.session_state.users:
            st.sidebar.error("Username tidak ditemukan!")
        elif new_pass != confirm_pass:
            st.sidebar.error("Password tidak cocok!")
        elif new_pass.strip() == "":
            st.sidebar.error("Password tidak boleh kosong!")
        else:
            st.session_state.users[username] = new_pass
            st.session_state.show_notification = True
            st.session_state.notification_message = "Password berhasil direset!"
            st.session_state.notification_type = "success"
            st.session_state.reset_mode = False
            st.rerun()

# Autentikasi login
def login():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            
            # Set notifikasi login berhasil
            st.session_state.show_notification = True
            st.session_state.notification_message = f"Login berhasil! Selamat datang, {username}!"
            st.session_state.notification_type = "success"
            
            st.rerun()
        else:
            st.sidebar.error("Username atau password salah")

    if st.sidebar.button("Lupa Password?"):
        st.session_state.reset_mode = True
        st.rerun()   
        
#Routing Login / Reset
if not st.session_state.logged_in:

    if st.session_state.reset_mode:
        reset_password()
        st.stop()

    login()
    st.stop()      
 
# sidebar
st.sidebar.title("Siklus Akuntansi")
menu = st.sidebar.radio("", ["Neraca Saldo", "Jurnal Umum", "Buku Besar", 
                             "Neraca Saldo Setelah Disesuaikan", "Laporan Laba Rugi", 
                             "Laporan Perubahan Ekuitas", "Laporan Posisi Keuangan"])

# Tombol logout
if st.sidebar.button("Logout"):
    username = st.session_state.username  # Simpan username untuk pesan
    st.session_state.logged_in = False
    st.session_state.username = ""
    
    # Set notifikasi logout berhasil
    st.session_state.show_notification = True
    st.session_state.notification_message = f"Logout berhasil! Sampai jumpa kembali, {username}!"
    st.session_state.notification_type = "info"
    
    st.rerun()

# Neraca Saldo    
if menu == "Neraca Saldo":
    st.title("Neraca Saldo")

    df_akun = [
        "Kas", "Piutang Usaha", "Perlengkapan", "Persediaan Barang Dagang", "Peralatan usaha", "Tanah",
        "Bangunan", "Akumulasi Penyusutan Bangunan", "Kendaraan", "Akumulasi Penyusutan Kendaraan",
        "Utang Usaha", "Utang Gaji", "Utang Pajak", "Modal, Tina", "Prive, Tina", "Ikhtisar Laba Rugi",  
        "Penjualan", "Diskon Penjualan", "Beban Angkut Penjualan", "Retur Penjualan", 
        "Harga Pokok Penjualan", "Diskon Pembelian", "Retur Pembelian", "Beban Angkut Pembelian", 
        "Beban Gaji Karyawan", "Beban Administrasi Bank", "Beban Perlengkapan", "Beban Listrik, Air & Telp",
        "Beban Penyusutan Bangunan", "Beban Penyusutan Kendaraan", "Beban Pajak", "Beban lain-lain",
    ]

    # Expander untuk menambah data saldo awal
    with st.expander("Tambah Saldo Awal"):
        akun = st.selectbox("Nama Akun", df_akun)
        saldo_debit = st.number_input("Saldo Debit", min_value=0.0)
        saldo_kredit = st.number_input("Saldo Kredit", min_value=0.0)
        if st.button("Tambah Saldo Awal"):
            simpan_saldo(akun, saldo_debit, saldo_kredit)
            st.success("Saldo awal berhasil disimpan!")
            st.rerun()

    df = ambil_saldo_dengan_id()

    if not df.empty:
        saldo_debit = df["Debit"].sum()
        saldo_kredit = df["Kredit"].sum()

        # Expander: Hapus baris dengan tombol per baris
        with st.expander("Hapus Baris Tertentu"):
            st.markdown("Klik tombol di samping untuk menghapus baris tertentu.")
            for i, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 1])
                col1.write(i)
                col2.write(row["Nama Akun"])
                col3.write(f"{int(row['Debit'])}" if row["Debit"] else "")
                col4.write(f"{int(row['Kredit'])}" if row["Kredit"] else "")
                if col5.button("Hapus", key=f"hapus_{row['id']}"):
                    hapus_saldo_per_id(row["id"])
                    st.warning(f"Baris dengan akun '{row['Nama Akun']}' telah dihapus.")
                    st.rerun()

        # Expander untuk menghapus semua data
        with st.expander("Kosongkan Semua Data Neraca Saldo"):
            st.warning("⚠ Tindakan ini akan menghapus seluruh neraca saldo yang tersimpan.")
            konfirmasi = st.checkbox("Saya yakin ingin menghapus semua data.")
            if konfirmasi and st.button("Hapus Semua Data"):
                hapus_semua_saldo()
                st.success("Seluruh data neraca saldo telah dikosongkan.")
                st.rerun()

        st.markdown("### Neraca Saldo Tersimpan")

        total_row = pd.DataFrame([{ 
            "Nama Akun": "Total", 
            "Debit": saldo_debit, 
            "Kredit": saldo_kredit 
        }])
        df_total = pd.concat([df.drop(columns=["id"]), total_row], ignore_index=True)

        df_total["Debit"] = df_total["Debit"].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") if x != 0 else "")
        df_total["Kredit"] = df_total["Kredit"].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") if x != 0 else "")

        st.dataframe(df_total, use_container_width=True)

        # ===========================
        # EXPORT NERACA SALDO KE EXCEL
        # ===========================

        def export_neraca_saldo_excel(df):
            output = io.BytesIO()

            # Buang kolom id jika masih ada
            if "id" in df.columns:
                df_export = df.drop(columns=["id"])
            else:
                df_export = df.copy()

            # Simpan ke Excel
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_export.to_excel(writer, sheet_name="Neraca Saldo", index=False)

                # Format angka menjadi Rupiah
                ws = writer.book["Neraca Saldo"]
                for row in ws.iter_rows(min_row=2):
                    for cell in row[1:3]:  # Debit & Kredit
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = '"Rp"#,##0'

                # Auto width kolom
                for col in ws.columns:
                    max_length = 0
                    for cell in col:
                        try:
                            max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    ws.column_dimensions[col[0].column_letter].width = max_length + 2

            output.seek(0)
            return output

        # Tombol download
        excel_file = export_neraca_saldo_excel(df)
        st.download_button(
            label="📥 Download Excel",
            data=excel_file,
            file_name="Neraca_Saldo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if saldo_debit != saldo_kredit:
                st.warning("⚠ Total Debit tidak sama dengan Total Kredit!")
    else:
         st.info("Belum ada data neraca saldo.")

# Jurnal Umum
if menu == "Jurnal Umum":
    st.title("Jurnal Umum")

    # Daftar akun
    df_akun = ["Kas", "Piutang Usaha", "Perlengkapan", "Persediaan Barang Dagang", "Peralatan usaha", "Tanah",
                "Bangunan", "Akumulasi Penyusutan Bangunan", "Kendaraan", "Akumulasi Penyusutan Kendaraan",
                "Utang Usaha", "Utang Gaji", "Utang Pajak", "Modal, Tina", "Prive, Tina", "Ikhtisar Laba Rugi",  
                "Penjualan", "Diskon Penjualan", "Beban Angkut Penjualan", "Retur Penjualan", 
                "Harga Pokok Penjualan", "Diskon Pembelian", "Retur Pembelian", "Beban Angkut Pembelian", 
                "Beban Gaji Karyawan", "Beban Administrasi Bank", "Beban Perlengkapan", "Beban Listrik, Air & Telp",
                "Beban Penyusutan Bangunan", "Beban Penyusutan Kendaraan", "Beban Pajak", "Beban lain-lain",]

    # Tambah Transaksi
    with st.expander("Tambah Transaksi"):
        tanggal = st.date_input("Tanggal", key="tgl_input")
        keterangan = st.text_input("Keterangan", key="ket_input")

        st.markdown("**➡️ Input Akun dan Nominal Debit**")
        col1, col2 = st.columns(2)
        with col1:
            akun_debit = st.selectbox("Akun Debit", df_akun, key="akun_debit_input")
        with col2:
            nominal_debit = st.number_input("Nominal Debit", min_value=0.0, format="%.2f", key="nominal_debit_input")

        st.markdown("**➡️ Input Akun dan Nominal Kredit**")
        col3, col4 = st.columns(2)
        with col3:
            akun_kredit = st.selectbox("Akun Kredit", df_akun, key="akun_kredit_input")
        with col4:
            nominal_kredit = st.number_input("Nominal Kredit", min_value=0.0, format="%.2f", key="nominal_kredit_input")

        if st.button("Tambah Transaksi", key="btn_tambah"):
            if akun_debit == akun_kredit:
                st.error("Akun Debit dan Kredit tidak boleh sama.")
            elif nominal_debit != nominal_kredit:
                st.warning("⚠️ Nominal Debit dan Kredit tidak sama. Pastikan jurnal seimbang!")
                simpan_jurnal(str(tanggal), akun_debit, keterangan, nominal_debit, 0.0)
                simpan_jurnal(str(tanggal), akun_kredit, keterangan, 0.0, nominal_kredit)
                st.success("Transaksi tidak seimbang tetap disimpan!")
                st.rerun()
            else:
                simpan_jurnal(str(tanggal), akun_debit, keterangan, nominal_debit, 0.0)
                simpan_jurnal(str(tanggal), akun_kredit, keterangan, 0.0, nominal_kredit)
                st.success("Transaksi berhasil disimpan!")
                st.rerun()

    # Ambil data jurnal dari database
    df = ambil_jurnal()

    if not df.empty:
        total_debit = df["Debit"].sum()
        total_kredit = df["Kredit"].sum()

        # Hapus Baris Tertentu
        with st.expander("Hapus Baris Tertentu"):
            st.markdown("Klik tombol 'Hapus' di samping untuk menghapus baris tertentu.")
            for i, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 1])
                col1.write(i)
                col2.write(row["Nama Akun"])
                col3.write(f"{int(row['Debit'])}" if row["Debit"] else "")
                col4.write(f"{int(row['Kredit'])}" if row["Kredit"] else "")
                if col5.button("Hapus", key=f"hapus_{row.name}"):
                    hapus_jurnal_id(row.name)
                    st.warning(f"Baris dengan akun '{row['Nama Akun']}' telah dihapus.")
                    st.rerun()

        # Hapus Semua
        with st.expander("Kosongkan Semua Data Jurnal Umum"):
            konfirmasi = st.checkbox("Saya yakin ingin menghapus semua data jurnal umum.", key="chk_konfirmasi_hapus")
            if konfirmasi:
                if st.button("Hapus Semua Data", key="btn_hapus_semua"):
                    hapus_semua_jurnal()
                    st.warning("Seluruh data jurnal umum telah dikosongkan.")
                    st.rerun()

        # Tambah baris total
        total_row = pd.DataFrame([{
            "Tanggal": "",
            "Nama Akun": "",
            "Keterangan": "Total",
            "Debit": total_debit,
            "Kredit": total_kredit
        }])
        df_total = pd.concat([df, total_row], ignore_index=True)

        # Format rupiah
        def format_rupiah(x):
            if x == 0 or x == "":
                return ""
            return f"Rp {int(x):,}".replace(",", ".")

        df_total["Debit"] = df_total["Debit"].apply(format_rupiah)
        df_total["Kredit"] = df_total["Kredit"].apply(format_rupiah)

        # Tampilkan tabel
        st.markdown("### Jurnal Umum Tersimpan")
        st.dataframe(df_total, use_container_width=True)

        # ============================================================
        # 📥 EXPORT JURNAL UMUM KE EXCEL (MIRIP NERACA SALDO)
        # ============================================================

        df_export = ambil_jurnal()  # Data dari database

        # Buang kolom id jika ada
        if "id" in df_export.columns:
            df_export = df_export.drop(columns=["id"])

        import io
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Jurnal Umum")

            ws = writer.book["Jurnal Umum"]

            # Auto-width kolom
            for col in ws.columns:
                max_length = 0
                col_letter = col[0].column_letter

                for cell in col:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass

                ws.column_dimensions[col_letter].width = max_length + 2

        output.seek(0)

        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name="Jurnal_Umum.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if total_debit != total_kredit:
            st.warning("⚠️ Total Debit tidak sama dengan Total Kredit!")
    else:
        st.info("Belum ada data transaksi. Silakan tambahkan dulu.")

# Buku Besar
if menu == "Buku Besar":
    st.title("Buku Besar")

    # Kelompok akun
    akun_debit_normal = ["Kas", "Piutang Usaha", "Perlengkapan", "Persediaan Barang Dagang", "Peralatan usaha", "Tanah",
                         "Bangunan", "Kendaraan", "Prive, Tina", "Ikhtisar Laba Rugi", "Diskon Penjualan", "Beban Angkut Penjualan", "Retur Penjualan", 
                         "Harga Pokok Penjualan", "Diskon Pembelian", "Retur Pembelian", "Beban Angkut Pembelian", 
                         "Beban Gaji Karyawan", "Beban Administrasi Bank", "Beban Perlengkapan", "Beban Listrik, Air & Telp",
                         "Beban Penyusutan Bangunan", "Beban Penyusutan Kendaraan", "Beban Pajak", "Beban lain-lain",]
    akun_kredit_normal = ["Akumulasi Penyusutan Bangunan", "Akumulasi Penyusutan Kendaraan", "Utang Usaha", "Utang Gaji", "Utang Pajak", "Modal, Tina",
                          "Penjualan"]

    # Fungsi saldo awal
    def saldo_awal_akun(akun, debit, kredit):
        if akun in akun_debit_normal:
            return + debit - kredit
        elif akun in akun_kredit_normal:
            return + kredit - debit
        else:
            return + debit - kredit

    # Fungsi saldo berjalan
    def hitung_saldo_berjalan(akun, debit, kredit, saldo_sebelumnya):
        if akun in akun_debit_normal:
            return saldo_sebelumnya + debit - kredit
        elif akun in akun_kredit_normal:
            return saldo_sebelumnya + kredit - debit
        else:
            return saldo_sebelumnya + debit - kredit

    # Ambil data dari database
    saldo_awal = ambil_saldo_dengan_id().to_dict("records")
    jurnal = ambil_jurnal().to_dict("records")

    # Buat dict saldo awal
    saldo_awal_dict = {}
    for item in saldo_awal:
        nama = item["Nama Akun"]
        saldo_awal_dict[nama] = saldo_awal_akun(nama, item["Debit"], item["Kredit"])

    # Persiapkan jurnal
    df_jurnal = pd.DataFrame(jurnal)
    if not df_jurnal.empty:
        df_jurnal["Tanggal"] = pd.to_datetime(df_jurnal["Tanggal"], errors='coerce')
        df_jurnal["Debit"] = pd.to_numeric(df_jurnal["Debit"], errors='coerce').fillna(0)
        df_jurnal["Kredit"] = pd.to_numeric(df_jurnal["Kredit"], errors='coerce').fillna(0)
        df_jurnal = df_jurnal.sort_values("Tanggal").reset_index(drop=True)
    else:
        df_jurnal = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Keterangan", "Debit", "Kredit"])

    # Gabungkan semua akun dari saldo awal dan jurnal
    akun_list = list(set(saldo_awal_dict.keys()).union(set(df_jurnal["Nama Akun"].unique())))

    # Fungsi bantu untuk pecah saldo ke debit/kredit
    def pecah_saldo_ke_kolom(akun, nilai):
        if akun in akun_debit_normal:
            return (nilai if nilai >= 0 else 0, abs(nilai) if nilai < 0 else 0)
        elif akun in akun_kredit_normal:
            return (abs(nilai) if nilai < 0 else 0, nilai if nilai >= 0 else 0)
        else:
            return (nilai if nilai >= 0 else 0, abs(nilai) if nilai < 0 else 0)

    # Hitung buku besar per akun
    buku_besar = {}
    for akun in akun_list:
        saldo = saldo_awal_dict.get(akun, 0)
        saldo_debit, saldo_kredit = pecah_saldo_ke_kolom(akun, saldo)

        rows = [{
            "Tanggal": "",
            "Keterangan": "Saldo Awal",
            "Debit": "",
            "Kredit": "",
            "Saldo Debit": saldo_debit,
            "Saldo Kredit": saldo_kredit
        }]

        df_akun = df_jurnal[df_jurnal["Nama Akun"] == akun]
        for _, row in df_akun.iterrows():
            saldo = hitung_saldo_berjalan(akun, row["Debit"], row["Kredit"], saldo)
            saldo_debit, saldo_kredit = pecah_saldo_ke_kolom(akun, saldo)

            rows.append({
                "Tanggal": row["Tanggal"].strftime("%Y-%m-%d") if pd.notnull(row["Tanggal"]) else "",
                "Keterangan": row.get("Keterangan", ""),
                "Debit": row["Debit"],
                "Kredit": row["Kredit"],
                "Saldo Debit": saldo_debit,
                "Saldo Kredit": saldo_kredit
            })

        buku_besar[akun] = pd.DataFrame(rows)

    # Format rupiah
    def format_rupiah(x):
        if x == "" or x == 0 or pd.isna(x):
            return ""
        else:
            return f"Rp {int(x):,}".replace(",", ".")

    # Tampilkan hasil
    for akun, df_bb in buku_besar.items():
        st.subheader(f"Nama Akun: {akun}")
        df_display = df_bb.copy()
        df_display["Debit"] = df_display["Debit"].apply(format_rupiah)
        df_display["Kredit"] = df_display["Kredit"].apply(format_rupiah)
        df_display["Saldo Debit"] = df_display["Saldo Debit"].apply(format_rupiah)
        df_display["Saldo Kredit"] = df_display["Saldo Kredit"].apply(format_rupiah)
        st.dataframe(df_display, use_container_width=True)

    # Simpan ke session_state agar bisa dipakai di menu lain jika perlu
    st.session_state["buku_besar"] = buku_besar
    
    # ============================================================
    # 📁 EXPORT BUKU BESAR KE EXCEL (OPENPYXL)
    # ============================================================

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        # Loop setiap akun dan buat sheet sendiri
        for akun, df_bb in buku_besar.items():
            sheet_name = akun[:31]  # nama sheet maksimal 31 karakter

            df_export = df_bb.copy()

            # Simpan ke sheet Excel
            df_export.to_excel(writer, index=False, sheet_name=sheet_name)

            ws = writer.book[sheet_name]

            # Auto width kolom
            for col in ws.columns:
                max_length = 0
                col_letter = col[0].column_letter

                for cell in col:
                    try:
                        val = str(cell.value)
                        if val is None:
                            val = ""
                        max_length = max(max_length, len(val))
                    except:
                        pass

                ws.column_dimensions[col_letter].width = max_length + 2

    output.seek(0)

    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name="Buku_Besar.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
  
# Neraca Saldo Setelah Disesuaikan
if menu == "Neraca Saldo Setelah Disesuaikan":
    st.title("Neraca Saldo Setelah Disesuaikan")
    
    akun_debit_normal = ["Kas", "Piutang Usaha", "Perlengkapan", "Persediaan Barang Dagang", "Peralatan usaha", "Tanah",
                         "Bangunan", "Kendaraan", "Prive, Tina", "Ikhtisar Laba Rugi", "Diskon Penjualan", "Beban Angkut Penjualan", "Retur Penjualan", 
                         "Harga Pokok Penjualan", "Diskon Pembelian", "Retur Pembelian", "Beban Angkut Pembelian", 
                         "Beban Gaji Karyawan", "Beban Administrasi Bank", "Beban Perlengkapan", "Beban Listrik, Air & Telp",
                         "Beban Penyusutan Bangunan", "Beban Penyusutan Kendaraan", "Beban Pajak", "Beban lain-lain",]
    akun_kredit_normal = ["Akumulasi Penyusutan Bangunan", "Akumulasi Penyusutan Kendaraan", "Utang Usaha", "Utang Gaji", "Utang Pajak", "Modal, Tina",
                          "Penjualan"]

    buku_besar = st.session_state.get("buku_besar", {})
    
    rows = []
    total_debit = 0
    total_kredit = 0
    
    for akun, df_bb in buku_besar.items():
        if len(df_bb) > 0:
            saldo_debit = df_bb.iloc[-1]["Saldo Debit"] if not pd.isna(df_bb.iloc[-1]["Saldo Debit"]) else 0
            saldo_kredit = df_bb.iloc[-1]["Saldo Kredit"] if not pd.isna(df_bb.iloc[-1]["Saldo Kredit"]) else 0
            
            if akun in akun_debit_normal:
                debit_val = saldo_debit
                kredit_val = 0
                total_debit += debit_val
            elif akun in akun_kredit_normal:
                debit_val = 0
                kredit_val = saldo_kredit
                total_kredit += kredit_val
            
            if debit_val > 0 or kredit_val > 0:
                rows.append({
                    "Nama Akun": akun,
                    "Debit": debit_val if debit_val > 0 else "",
                    "Kredit": kredit_val if kredit_val > 0 else ""
                })
    
    rows.append({
        "Nama Akun": "TOTAL",
        "Debit": total_debit,
        "Kredit": total_kredit
    })

    # Simpan ke session_state tanpa baris total
    st.session_state["neraca_saldo_disesuaikan"] = rows[:-1]

    def format_rupiah(x):
        if x == "" or x == 0 or pd.isna(x):
            return ""
        else:
            return f"Rp {int(x):,}".replace(",", ".")

    df_display = pd.DataFrame(rows)
    df_display["Debit"] = df_display["Debit"].apply(format_rupiah)
    df_display["Kredit"] = df_display["Kredit"].apply(format_rupiah)
    st.dataframe(df_display, use_container_width=True)
    
    if total_debit != total_kredit:
            st.warning("⚠️ Total Debit tidak sama dengan Total Kredit!")
    
    # ============================================================
    # 📁 EXPORT NERACA SALDO SETELAH DISESUAIKAN
    # ============================================================

    def export_neraca_saldo_disesuaikan(rows):
        output = io.BytesIO()

        # Buat DataFrame export
        df_export = pd.DataFrame(rows)

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Neraca Disesuaikan")

            ws = writer.book["Neraca Disesuaikan"]

            # Auto width setiap kolom
            for col in ws.columns:
                max_length = 0
                col_letter = col[0].column_letter

                for cell in col:
                    value = cell.value
                    if value is None:
                        value = ""
                    value = str(value)
                    if len(value) > max_length:
                        max_length = len(value)

                ws.column_dimensions[col_letter].width = max_length + 2

        output.seek(0)
        return output

    # Tombol Siapkan File
    excel_file = export_neraca_saldo_disesuaikan(rows)
    st.download_button(
        label="📤 Download Excel",
        data=excel_file,
        file_name="Neraca_Saldo_Sesudah_Disesuaikan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Laporan Laba Rugi
if menu == "Laporan Laba Rugi":
    st.title("Laporan Laba Rugi")

    neraca_saldo = st.session_state.get("neraca_saldo_disesuaikan", [])

    def format_rupiah(x):
        if x == 0 or x == "" or pd.isna(x):
            return ""
        return f"Rp {int(x):,}".replace(",", ".")

    if neraca_saldo:
        df_neraca = pd.DataFrame(neraca_saldo)

        # -------------------------
        # Fungsi ambil saldo
        # -------------------------
        def get_saldo(df, nama, kolom="Debit"):
            if df.empty:
                return 0
            row = df[df["Nama Akun"] == nama]
            if not row.empty:
                val = row.iloc[0][kolom]
                if val == "" or pd.isna(val):
                    return 0
                return val
            return 0

        # -------------------------
        # PENDAPATAN
        # -------------------------
        penjualan = get_saldo(df_neraca, "Penjualan", "Kredit")
        diskon_penjualan = get_saldo(df_neraca, "Diskon Penjualan", "Debit")
        retur_penjualan = get_saldo(df_neraca, "Retur Penjualan", "Debit")
        beban_angkut_penjualan = get_saldo(df_neraca, "Beban Angkut Penjualan", "Debit")

        penjualan_bersih = penjualan - diskon_penjualan - retur_penjualan - beban_angkut_penjualan

        # -------------------------
        # HPP (REVISI TOTAL)
        # -------------------------
        hpp = get_saldo(df_neraca, "Persediaan Barang Dagang", "Debit")

        # -------------------------
        # BEBAN OPERASIONAL
        # -------------------------
        beban_gaji = get_saldo(df_neraca, "Beban Gaji Karyawan")
        beban_perlengkapan = get_saldo(df_neraca, "Beban Perlengkapan")
        beban_listrik = get_saldo(df_neraca, "Beban Listrik, Air & Telp")
        penyusutan_bangunan = get_saldo(df_neraca, "Beban Penyusutan Bangunan")
        penyusutan_kendaraan = get_saldo(df_neraca, "Beban Penyusutan Kendaraan")

        total_beban_operasional = (
            beban_gaji +
            beban_perlengkapan +
            beban_listrik +
            penyusutan_bangunan +
            penyusutan_kendaraan
        )

        # -------------------------
        # BEBAN NON-OPERASIONAL
        # -------------------------
        beban_admin_bank = get_saldo(df_neraca, "Beban Administrasi Bank")
        beban_lain = get_saldo(df_neraca, "Beban lain-lain")
        total_beban_non_op = beban_admin_bank + beban_lain

        # Pajak
        beban_pajak = get_saldo(df_neraca, "Beban Pajak")

        # -------------------------
        # PERHITUNGAN LABA
        # -------------------------
        laba_kotor = penjualan_bersih - hpp
        laba_operasional = laba_kotor - total_beban_operasional
        laba_sebelum_pajak = laba_operasional - total_beban_non_op
        laba_setelah_pajak = laba_sebelum_pajak - beban_pajak

        st.session_state["laba_bersih"] = laba_setelah_pajak

        # -------------------------
        # TAMPILKAN LAPORAN
        # -------------------------
        data = [
            ["Penjualan", "", format_rupiah(penjualan)],
            ["Diskon Penjualan", format_rupiah(diskon_penjualan), ""],
            ["Retur Penjualan", format_rupiah(retur_penjualan), ""],
            ["Beban Angkut Penjualan", format_rupiah(beban_angkut_penjualan), ""],
            ["Penjualan Bersih", "", format_rupiah(penjualan_bersih)],
            ["", "", ""],

            ["Harga Pokok Penjualan", "", format_rupiah(hpp)],
            ["Laba Kotor", "", format_rupiah(laba_kotor)],
            ["", "", ""],

            ["Beban Operasional:", "", ""],
            ["Beban Gaji Karyawan", format_rupiah(beban_gaji), ""],
            ["Beban Perlengkapan", format_rupiah(beban_perlengkapan), ""],
            ["Beban Listrik, Air & Telp", format_rupiah(beban_listrik), ""],
            ["Beban Penyusutan Bangunan", format_rupiah(penyusutan_bangunan), ""],
            ["Beban Penyusutan Kendaraan", format_rupiah(penyusutan_kendaraan), ""],
            ["Total Beban Operasional", "", format_rupiah(total_beban_operasional)],
            ["", "", ""],

            ["Laba Operasional", "", format_rupiah(laba_operasional)],
            ["", "", ""],

            ["Beban Non-Operasional:", "", ""],
            ["Beban Administrasi Bank", format_rupiah(beban_admin_bank), ""],
            ["Beban Lain-lain", format_rupiah(beban_lain), ""],
            ["Total Beban Non-Operasional", "", format_rupiah(total_beban_non_op)],
            ["", "", ""],

            ["Laba Sebelum Pajak", "", format_rupiah(laba_sebelum_pajak)],
            ["Beban Pajak", "", format_rupiah(beban_pajak)],
            ["Laba Bersih Setelah Pajak", "", format_rupiah(laba_setelah_pajak)],
        ]

        df_laporan = pd.DataFrame(data, columns=["Keterangan", "1", "2"])
        st.dataframe(df_laporan, use_container_width=True, height=700)

    else:
        st.warning("Data Neraca Saldo Disesuaikan belum tersedia. Silakan buka menu tersebut terlebih dahulu.")

    # ============================================================
    # 📁 EXPORT LAPORAN LABA RUGI (FORMAT SAMA DENGAN YANG LAIN)
    # ============================================================

    def export_laba_rugi(data):
        output = io.BytesIO()

        # Ubah ke DataFrame untuk export
        df_export = pd.DataFrame(data, columns=["Keterangan", "Debit", "Kredit"])

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Laba Rugi")

            ws = writer.book["Laba Rugi"]

            # Auto width setiap kolom
            for col in ws.columns:
                max_length = 0
                col_letter = col[0].column_letter

                for cell in col:
                    value = cell.value
                    if value is None:
                        value = ""
                    value = str(value)
                    if len(value) > max_length:
                        max_length = len(value)

                ws.column_dimensions[col_letter].width = max_length + 2

        output.seek(0)
        return output

    # Tombol Siapkan File
    excel_file = export_laba_rugi(data)
    st.download_button(
        label="📤 Download Excel",
        data=excel_file,
        file_name="Laporan_Laba_Rugi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
# Laporan Perubahan Ekuitas
if menu == "Laporan Perubahan Ekuitas":
    st.title("Laporan Perubahan Ekuitas")

    # Ambil data dari session_state
    neraca_saldo = st.session_state.get("neraca_saldo_disesuaikan")
    laba_bersih = st.session_state.get("laba_bersih")

    def format_rupiah(x):
        if x == 0 or x == "" or pd.isna(x):
            return ""
        return f"Rp {int(x):,}".replace(",", ".")

    # Validasi data
    if neraca_saldo is None:
        st.warning("Data Neraca Saldo Disesuaikan belum tersedia. Silakan buka menu tersebut terlebih dahulu.")
    elif laba_bersih is None:
        st.warning("Laporan Laba Rugi belum tersedia. Silakan buka menu Laporan Laba Rugi terlebih dahulu.")
    else:
        # --- Ambil Modal Awal ---
        modal_awal = 0
        prive = 0

        for row in neraca_saldo:
            nama = row["Nama Akun"]

            # Ambil modal awal dari akun Modal, Tina (kredit)
            if nama == "Modal, Tina":
                val = row.get("Kredit", 0)
                if isinstance(val, str):
                    val = int(val.replace("Rp ", "").replace(".", ""))
                modal_awal = val

            # Ambil prive (debit → mengurangi modal)
            if nama == "Prive, Tina":
                val = row.get("Debit", 0)
                if isinstance(val, str):
                    val = int(val.replace("Rp ", "").replace(".", ""))
                prive = val

        # Hitung modal akhir
        modal_akhir = modal_awal + laba_bersih - prive

        # Simpan untuk laporan posisi keuangan
        st.session_state["modal_akhir"] = modal_akhir

        # Tampilkan tabel
        data = [
            ["Modal Awal", format_rupiah(modal_awal)],
            ["Laba/Rugi", format_rupiah(laba_bersih)],
            ["Prive", f"- {format_rupiah(prive)}"],
            ["Modal Akhir", format_rupiah(modal_akhir)]
        ]

        df_modal = pd.DataFrame(data, columns=["Keterangan", "Jumlah"])
        st.dataframe(df_modal, use_container_width=True)
    
        # ============================================================
        # 📁 EXPORT LAPORAN PERUBAHAN EKUITAS (OPENPYXL)
        # ============================================================

        def export_perubahan_ekuitas(data):
            output = io.BytesIO()

            # Buat DataFrame export
            df_export = pd.DataFrame(data, columns=["Keterangan", "Jumlah"])

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_export.to_excel(writer, index=False, sheet_name="Perubahan Ekuitas")

                ws = writer.book["Perubahan Ekuitas"]

                # Auto width tiap kolom
                for col in ws.columns:
                    max_length = 0
                    col_letter = col[0].column_letter

                    for cell in col:
                        value = cell.value if cell.value is not None else ""
                        value = str(value)
                        max_length = max(max_length, len(value))

                    ws.column_dimensions[col_letter].width = max_length + 2

            output.seek(0)
            return output

        # Tombol Siapkan File
        excel_file = export_perubahan_ekuitas(data)
        st.download_button(
            label="📤 Download Excel",
            data=excel_file,
            file_name="Laporan_Perubahan_Ekuitas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
# Laporan Posisi Keuangan 
if menu == "Laporan Posisi Keuangan":
    st.title("Laporan Posisi Keuangan")

    neraca_saldo = st.session_state.get("neraca_saldo_disesuaikan", [])
    modal_akhir = st.session_state.get("modal_akhir")

    def format_rupiah(x):
        if x == "" or x == 0 or pd.isna(x):
            return ""
        return f"Rp {int(x):,}".replace(",", ".")

    if not neraca_saldo:
        st.warning("Data Neraca Saldo Disesuaikan belum tersedia. Silakan buka menu tersebut terlebih dahulu.")
    elif modal_akhir is None:
        st.warning("Modal Akhir belum tersedia. Silakan buka menu Laporan Perubahan Ekuitas terlebih dahulu.")
    else:
        # ========================== #
        # KLASIFIKASI AKUN
        # ========================== #
        aset_lancar = [
            "Kas",
            "Piutang Usaha",
            "Perlengkapan",
            "Persediaan Barang Dagang"
        ]

        aset_tetap = [
            "Peralatan usaha",
            "Tanah",
            "Bangunan",
            "Kendaraan"
        ]

        akumulasi_penyusutan = [
            "Akumulasi Penyusutan Bangunan",
            "Akumulasi Penyusutan Kendaraan"
        ]

        liabilitas = [
            "Utang usaha",
            "Utang Gaji",
            "Utang Pajak"
        ]

        df = pd.DataFrame(neraca_saldo)

        # Ambil saldo (debit = positif, kredit = positif tergantung akun)
        def get_saldo(akun):
            row = df[df["Nama Akun"] == akun]
            if not row.empty:
                debit = row.iloc[0]["Debit"] if row.iloc[0]["Debit"] != "" else 0
                kredit = row.iloc[0]["Kredit"] if row.iloc[0]["Kredit"] != "" else 0
                return int(debit) if int(debit) > 0 else int(kredit)
            return 0

        rows_stafel = []

        # ========================== #
        #           ASET
        # ========================== #
        rows_stafel.append(["ASET", "", ""])

        # Aset Lancar
        total_aset_lancar = 0
        rows_stafel.append(["  Aset Lancar", "", ""])
        for akun in aset_lancar:
            saldo = get_saldo(akun)
            total_aset_lancar += saldo
            rows_stafel.append([f"    {akun}", format_rupiah(saldo), ""])
        rows_stafel.append(["  Total Aset Lancar", "", format_rupiah(total_aset_lancar)])

        # Aset Tidak Lancar
        total_aset_tetap = 0
        rows_stafel.append(["  Aset Tidak Lancar", "", ""])
        for akun in aset_tetap:
            saldo = get_saldo(akun)
            total_aset_tetap += saldo
            rows_stafel.append([f"    {akun}", format_rupiah(saldo), ""])

        # Akumulasi Penyusutan (pengurang aset)
        for akun in akumulasi_penyusutan:
            saldo = get_saldo(akun)
            total_aset_tetap -= saldo
            rows_stafel.append([f"    {akun}", f"-{format_rupiah(saldo)}", ""])

        rows_stafel.append(["  Total Aset Tidak Lancar", "", format_rupiah(total_aset_tetap)])

        total_aset = total_aset_lancar + total_aset_tetap
        rows_stafel.append(["Total Aset", "", format_rupiah(total_aset)])

        rows_stafel.append(["", "", ""])  # Baris kosong

        # ========================== #
        #     LIABILITAS & EKUITAS
        # ========================== #
        rows_stafel.append(["LIABILITAS DAN EKUITAS", "", ""])

        # Liabilitas
        rows_stafel.append(["  Liabilitas", "", ""])
        total_liabilitas = 0
        for akun in liabilitas:
            saldo = get_saldo(akun)
            total_liabilitas += saldo
            rows_stafel.append([f"    {akun}", format_rupiah(saldo), ""])
        rows_stafel.append(["  Total Liabilitas", "", format_rupiah(total_liabilitas)])

        # Ekuitas (tanpa prive)
        rows_stafel.append(["  Ekuitas", "", ""])
        rows_stafel.append([f"    Modal, Tina", format_rupiah(modal_akhir), ""])
        rows_stafel.append(["  Total Ekuitas", "", format_rupiah(modal_akhir)])

        # Total passiva
        total_passiva = total_liabilitas + modal_akhir
        rows_stafel.append(["Total Liabilitas dan Ekuitas", "", format_rupiah(total_passiva)])

        # Tampilkan tabel
        df_stafel = pd.DataFrame(rows_stafel, columns=["Keterangan", "1", "2"])
        st.table(df_stafel)

        if total_aset != total_passiva:
            st.warning("⚠️ Total Aset tidak sama dengan Total Liabilitas + Ekuitas!")

        # ============================================================
        # 📁 EXPORT LAPORAN POSISI KEUANGAN (NERACA)
        # ============================================================

        def export_posisi_keuangan(rows_stafel):
            output = io.BytesIO()

            # DataFrame export
            df_export = pd.DataFrame(rows_stafel, columns=["Keterangan", "1", "2"])

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_export.to_excel(writer, index=False, sheet_name="Laporan Posisi Keuangan")

                ws = writer.book["Laporan Posisi Keuangan"]

                # Auto lebar kolom
                for col in ws.columns:
                    max_length = 0
                    col_letter = col[0].column_letter

                    for cell in col:
                        value = cell.value if cell.value is not None else ""
                        value = str(value)
                        max_length = max(max_length, len(value))

                    ws.column_dimensions[col_letter].width = max_length + 2

            output.seek(0)
            return output

        # Tombol Siapkan File
        excel_file = export_posisi_keuangan(rows_stafel)
        st.download_button(
            label="📤 Download Excel",
            data=excel_file,
            file_name="Laporan_Posisi_Keuangan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )  