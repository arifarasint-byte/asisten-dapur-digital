import streamlit as st
import pandas as pd
import urllib.parse
from database_helper import load_data, add_resep, convert_base64_to_image

# Set halaman utama Streamlit
st.set_page_config(page_title="Smart Meal Planner", page_icon="🍳", layout="wide")

st.title("🍳 Smart Meal Planner & Resep Keluarga")
st.caption("Aplikasi Perencana Menu Makan Harian & Galeri Resep Digital")

# Inisialisasi session state untuk menyimpan rencana mingguan sementara
if "plan" not in st.session_state:
    st.session_state.plan = {
        hari: {"Sarapan": "Pilih Menu", "Makan Siang": "Pilih Menu", "Makan Malam": "Pilih Menu"}
        for hari in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    }

# Load data resep dari Excel via helper
df_resep = load_data()
daftar_menu = ["Pilih Menu", "Makan di Luar"] + df_resep["Nama_Menu"].tolist()

# Membuat Menu Tab Navigasi
tab1, tab2, tab3 = st.tabs(["📅 Perencana Mingguan", "🥗 Galeri Resep", "➕ Tambah Resep Baru"])

# --- TAB 1: PERENCANA MINGGUAN ---
with tab1:
    st.subheader("Susun Menu Makan Minggu Ini")
    
    # Membuat grid input untuk 7 hari
    hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    cols = st.columns(7)
    
    for idx, hari in enumerate(hari_list):
        with cols[idx]:
            st.markdown(f"**{hari}**")
            st.session_state.plan[hari]["Sarapan"] = st.selectbox(f"Sarapan ({hari})", daftar_menu, index=daftar_menu.index(st.session_state.plan[hari]["Sarapan"]), label_visibility="collapsed")
            st.session_state.plan[hari]["Makan Siang"] = st.selectbox(f"Siang ({hari})", daftar_menu, index=daftar_menu.index(st.session_state.plan[hari]["Makan Siang"]), label_visibility="collapsed")
            st.session_state.plan[hari]["Makan Malam"] = st.selectbox(f"Malam ({hari})", daftar_menu, index=daftar_menu.index(st.session_state.plan[hari]["Makan Malam"]), label_visibility="collapsed")
            st.write("---")

    # Tombol Ajaib Generate Daftar Belanjaan
    if st.button("🚀 Generate Daftar Belanjaan Otomatis", type="primary"):
        st.session_state.generate_clicked = True

    # Cek apakah user sudah mengklik tombol generate
    if st.session_state.get("generate_clicked", False):
        st.subheader("🛒 Daftar Belanjaan Anda:")
        
        menu_terpilih = []
        for hari in hari_list:
            for waktu in ["Sarapan", "Makan Siang", "Makan Malam"]:
                m = st.session_state.plan[hari][waktu]
                if m not in ["Pilih Menu", "Makan di Luar"]:
                    menu_terpilih.append(m)
        
        if menu_terpilih:
            # Ambil bahan-bahan dari excel berdasarkan menu yang dipilih pengguna
            bahan_final = []
            df_filtered = df_resep[df_resep["Nama_Menu"].isin(menu_terpilih)]
            for bahan_teks in df_filtered["Bahan_Bahan"].dropna():
                items = [item.strip() for item in bahan_teks.split(",")]
                bahan_final.extend(items)
            
            # Hilangkan duplikat bahan baku
            bahan_unik = sorted(list(set(bahan_final)))
            
            # Tampilkan list belanjaan siap pakai dengan checkbox interaktif
            status_belanja = {}
            for b in bahan_unik:
                status_belanja[b] = st.checkbox(f"⬜ {b}", key=f"shop_{b}")
            
            st.write("---")
            st.subheader("📲 Kirim Catatan ke WhatsApp")
            st.write("Gunakan fitur ini untuk mengirim sisa bahan yang belum Anda centang langsung ke HP.")
            
            # Ambil list bahan yang BELUM dicentang/dibeli untuk dikirim ke WA
            bahan_belum_dibeli = [b for b, sudah_dibeli in status_belanja.items() if not sudah_dibeli]
            
            if bahan_belum_dibeli:
                # Membuat format teks cantik untuk WhatsApp
                text_wa = "*🚨 REKAPAN DAFTAR BELANJAAN 🚨*\n"
                text_wa += "_Berikut adalah sisa bahan makanan yang harus dibeli:_\n\n"
                for idx, b in enumerate(bahan_belum_dibeli, 1):
                    text_wa += f"{idx}. ▫️ {b}\n"
                text_wa += "\n_Dikirim otomatis dari Aplikasi Smart Meal Planner_"
                
                # Menggunakan format tautan wa.me resmi yang paling stabil
                encoded_text = urllib.parse.quote(text_wa)
                whatsapp_url = f"https://wa.me/?text={encoded_text}"
                
                # Menggunakan st.link_button bawaan resmi Streamlit (Aman dari blokir browser)
                st.link_button("🟢 Kirim Sisa Bahan Belanja ke WhatsApp", whatsapp_url, type="secondary")
            else:
                st.success("🎉 Semua bahan sudah selesai dicentang! Selamat berbelanja.")
                
        else:
            st.warning("Silakan pilih minimal 1 menu makanan pada jadwal di atas terlebih dahulu.")

# --- TAB 2: GALERI RESEP ---
with tab2:
    st.subheader("📚 Galeri Resep Bawaan & Koleksi Anda")
    
    kategori_filter = st.radio("Filter Kategori:", ["Semua Kategori", "Rumahan & Hemat", "Diet & Sehat"], horizontal=True)
    
    df_tampil = df_resep
    if kategori_filter != "Semua Kategori":
        df_tampil = df_resep[df_resep["Kategori"] == kategori_filter]
        
    if df_tampil.empty:
        st.info("Belum ada resep di kategori ini.")
    else:
        for _, row in df_tampil.iterrows():
            kalori_info = f" - {row['Estimasi_Kalori']}" if row['Estimasi_Kalori'] != "-" else ""
            label_expander = f"📖 {row['Nama_Menu']} ({row['Kategori']}){kalori_info}"
            
            with st.expander(label_expander):
                col_img, col_txt = st.columns(2)
                with col_img:
                    img = convert_base64_to_image(row["Foto_Base64"])
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.image("https://placehold.co", use_container_width=True)
                with col_txt:
                    st.markdown("**Bahan-Bahan:**")
                    st.write(row["Bahan_Bahan"])
                    st.markdown("**Cara Memasak:**")
                    st.write(row["Cara_Masak"])

# --- TAB 3: TAMBAH RESEP BARU ---
with tab3:
    st.subheader("➕ Tambahkan Resep Kreasi Baru Anda")
    with st.form("form_resep", clear_on_submit=True):
        nama = st.text_input("Nama Masakan/Menu*")
        kat = st.selectbox("Kategori Menu*", ["Rumahan & Hemat", "Diet & Sehat"])
        waktu = st.selectbox("Rekomendasi Waktu Makan", ["Sarapan", "Makan Siang", "Makan Malam"])
        kalori = st.text_input("Estimasi Kalori (Khusus menu diet, cth: ± 300 kkal)", value="-")
        bahan = st.text_area("Bahan-Bahan (Pisahkan dengan tanda koma ', ' agar daftar belanja rapi)*")
        cara = st.text_area("Langkah/Cara Memasak*")
        foto = st.file_uploader("Upload Foto Hasil Masakan", type=["jpg", "jpeg", "png"])
        
        submit = st.form_submit_button("Simpan Resep ke Excel Database")
        if submit:
            if nama and bahan and cara:
                sukses = add_resep(nama, kat, waktu, bahan, cara, kalori, foto)
                if sukses:
                    st.success(f"🎉 Resep '{nama}' berhasil disimpan! Silakan cek Tab Galeri atau Refresh halaman.")
                    st.rerun()
            else:
                st.error("Mohon isi semua kolom yang bertanda bintang (*).")
