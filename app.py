import streamlit as st
import pandas as pd
import urllib.parse
from database_helper import (
    verify_login, load_user_data, add_user_resep, convert_base64_to_image
)

st.set_page_config(page_title="Smart Meal Planner Pro", page_icon="🍳", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.nama_pembeli = ""

# --- GERBANG LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Login Asisten Dapur Digital")
    st.write("Silakan masuk menggunakan Username dan Password Anda.")
    
    with st.form("login_form"):
        input_user = st.text_input("Username / Email")
        input_pass = st.text_input("Password", type="password")
        btn_login = st.form_submit_button("Masuk ke Dapur Saya", type="primary")
        
        if btn_login:
            if input_user and input_pass:
                with st.spinner("Memverifikasi akun..."):
                    valid, nama = verify_login(input_user, input_pass)
                    if valid:
                        st.session_state.logged_in = True
                        st.session_state.username = input_user
                        st.session_state.nama_pembeli = nama
                        st.success(f"Selamat datang, {nama}!")
                        st.rerun()
                    else:
                        st.error("Username atau Password salah!")
            else:
                st.warning("Mohon isi Username dan Password Anda.")
    st.stop()

# --- HALAMAN UTAMA SETELAH LOGIN ---
col_header1, col_header2 = st.columns([4, 1])
with col_header1:
    st.title(f"🍳 Dapur Digital: {st.session_state.nama_pembeli}")
    st.caption("Perencana Menu Makan Mingguan & Daftar Belanja WhatsApp Otomatis")
with col_header2:
    if st.button("🚪 Keluar (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.nama_pembeli = ""
        if "plan" in st.session_state:
            del st.session_state.plan
        st.rerun()

current_user = st.session_state.username
df_resep = load_user_data(current_user)
daftar_menu = ["Pilih Menu", "Makan di Luar"] + df_resep["Nama_Menu"].tolist()

if "plan" not in st.session_state:
    st.session_state.plan = {
        hari: {"Sarapan": "Pilih Menu", "Makan Siang": "Pilih Menu", "Makan Malam": "Pilih Menu"}
        for hari in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    }

tab1, tab2, tab3 = st.tabs(["📅 Perencana Mingguan", "🥗 Galeri Resep", "➕ Tambah Resep Baru"])

with tab1:
    st.subheader("Susun Menu Makan Minggu Ini")
    hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    cols = st.columns(7)
    
    for idx, hari in enumerate(hari_list):
        with cols[idx]:
            st.markdown(f"**{hari}**")
            st.session_state.plan[hari]["Sarapan"] = st.selectbox(f"Sarapan ({hari})", daftar_menu, index=daftar_menu.index(st.session_state.plan[hari]["Sarapan"]), label_visibility="collapsed")
            st.session_state.plan[hari]["Makan Siang"] = st.selectbox(f"Siang ({hari})", daftar_menu, index=daftar_menu.index(st.session_state.plan[hari]["Makan Siang"]), label_visibility="collapsed")
            st.session_state.plan[hari]["Makan Malam"] = st.selectbox(f"Malam ({hari})", daftar_menu, index=daftar_menu.index(st.session_state.plan[hari]["Makan Malam"]), label_visibility="collapsed")
            st.write("---")

    if st.button("🚀 Generate Daftar Belanjaan Otomatis", type="primary"):
        st.session_state.generate_clicked = True

    if st.session_state.get("generate_clicked", False):
        st.subheader("🛒 Daftar Belanjaan Anda:")
        menu_terpilih = []
        for hari in hari_list:
            for waktu in ["Sarapan", "Makan Siang", "Makan Malam"]:
                m = st.session_state.plan[hari][waktu]
                if m not in ["Pilih Menu", "Makan di Luar"]:
                    menu_terpilih.append(m)
        
        if menu_terpilih:
            bahan_final = []
            df_filtered = df_resep[df_resep["Nama_Menu"].isin(menu_terpilih)]
            for bahan_teks in df_filtered["Bahan_Bahan"].dropna():
                items = [item.strip() for item in str(bahan_teks).split(",")]
                bahan_final.extend(items)
            
            bahan_unik = sorted(list(set(bahan_final)))
            status_belanja = {}
            for b in bahan_unik:
                status_belanja[b] = st.checkbox(f"⬜ {b}", key=f"shop_{b}")
            
            st.write("---")
            st.subheader("📲 Kirim Catatan ke WhatsApp")
            bahan_belum_dibeli = [b for b, sudah_dibeli in status_belanja.items() if not sudah_dibeli]
            
            if bahan_belum_dibeli:
                text_wa = f"*🚨 DAFTAR BELANJA ({st.session_state.nama_pembeli.upper()}) 🚨*\n\n"
                for idx, b in enumerate(bahan_belum_dibeli, 1):
                    text_wa += f"{idx}. ▫️ {b}\n"
                text_wa += "\n_Dikirim dari Smart Meal Planner_"
                
                encoded_text = urllib.parse.quote(text_wa)
                whatsapp_url = f"https://wa.me/?text={encoded_text}"
                st.link_button("🟢 Kirim Sisa Bahan Belanja ke WhatsApp", whatsapp_url, type="secondary")
            else:
                st.success("🎉 Semua bahan sudah selesai dicentang!")
        else:
            st.warning("Silakan pilih minimal 1 menu makanan pada jadwal di atas.")

with tab2:
    st.subheader("📚 Koleksi Resep Pribadi Anda")
    kategori_filter = st.radio("Filter Kategori:", ["Semua Kategori", "Rumahan & Hemat", "Diet & Sehat"], horizontal=True)
    
    df_tampil = df_resep
    if kategori_filter != "Semua Kategori":
        df_tampil = df_resep[df_resep["Kategori"] == kategori_filter]
        
    if df_tampil.empty:
        st.info("Belum ada resep di kategori ini.")
    else:
        for _, row in df_tampil.iterrows():
            kalori_info = f" - {row['Estimasi_Kalori']}" if str(row['Estimasi_Kalori']) != "-" else ""
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

with tab3:
    st.subheader("➕ Tambahkan Resep Baru ke Cloud")
    with st.form("form_resep", clear_on_submit=True):
        nama = st.text_input("Nama Masakan/Menu*")
        kat = st.selectbox("Kategori Menu*", ["Rumahan & Hemat", "Diet & Sehat"])
        waktu = st.selectbox("Rekomendasi Waktu Makan", ["Sarapan", "Makan Siang", "Makan Malam"])
        kalori = st.text_input("Estimasi Kalori (cth: ± 300 kkal)", value="-")
        bahan = st.text_area("Bahan-Bahan (Pisahkan dengan koma ', ')*")
        cara = st.text_area("Langkah/Cara Memasak*")
        foto = st.file_uploader("Upload Foto Masakan", type=["jpg", "jpeg", "png"])
        
        submit = st.form_submit_button("Simpan ke Database Cloud")
        if submit:
            if nama and bahan and cara:
                with st.spinner("Menyimpan ke cloud..."):
                    sukses = add_user_resep(current_user, nama, kat, waktu, bahan, cara, kalori, foto)
                    if sukses:
                        st.success(f"🎉 Resep '{nama}' tersimpan di akun Anda!")
                        st.rerun()
            else:
                st.error("Mohon isi semua kolom bertanda bintang (*).")
