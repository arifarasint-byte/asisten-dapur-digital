import streamlit as st
import gspread
import pandas as pd
import base64
from PIL import Image
import io
import urllib.parse

st.set_page_config(page_title="Smart Meal Planner Pro", page_icon="🍳", layout="wide")

SPREADSHEET_ID = "1RyqKa7Set8U7kWONbX1VlMEgxke6LI5_xwHGlex-btg"

def get_spreadsheet():
    secrets = dict(st.secrets["connections"]["gsheets"])
    secrets.pop("spreadsheet", None)
    g_domain = "google" + "apis.com"
    bot_domain = "iam.gservice" + "account.com"
    secrets["client_email"] = "bot-dapur@my-project-meal-514623." + bot_domain
    secrets["auth_uri"] = f"https://google.com"
    secrets["token_uri"] = f"https://oauth2.{g_domain}/token"
    secrets["auth_provider_x509_cert_url"] = f"https://www.{g_domain}/oauth2/v1/certs"
    gc = gspread.service_account_from_dict(secrets)
    return gc.open_by_key(SPREADSHEET_ID)

def verify_login(username, password):
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("Users")
        df_users = pd.DataFrame(ws.get_all_records())
        if df_users.empty:
            st.warning("Sheet Users kosong.")
            return False, None
        df_users["Username"] = df_users["Username"].astype(str).str.strip().str.lower()
        df_users["Password"] = df_users["Password"].astype(str).str.strip()
        user_match = df_users[(df_users["Username"] == str(username).strip().lower()) & (df_users["Password"] == str(password).strip())]
        if not user_match.empty:
            return True, next(iter(user_match["Nama_Pembeli"]))
        return False, None
    except Exception as e:
        st.error(f"Detail Error: {repr(e)}")
        return False, None

def load_user_data(username):
    sh = get_spreadsheet()
    clean_user = "".join(e for e in str(username).lower() if e.isalnum())
    sheet_name = f"Resep_{clean_user}"
    try:
        ws = sh.worksheet(sheet_name)
        return pd.DataFrame(ws.get_all_records())
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
        initial_data = [
            {"ID": 1, "Nama_Menu": "Tumis Kangkung Tempe", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "1 ikat kangkung, 1/2 papan tempe, 2 siung bawang putih, 3 siung bawang merah, 2 sdm saus tiram, secukupnya garam", "Cara_Masak": "Goreng tempe dadu. Tumis duo bawang. Masukkan kangkung dan tempe, beri saus tiram dan garam.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 2, "Nama_Menu": "Dada Ayam Panggang Teflon", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "150g dada ayam tanpa kulit, 1 siung bawang putih cincang, 1/2 sdt lada hitam, 1 sdm kecap asin, 1 sdt minyak zaitun", "Cara_Masak": "Marinasi ayam 15 menit. Panggang di teflon dengan minyak zaitun api kecil hingga matang.", "Estimasi_Kalori": "± 250 kkal", "Foto_Base64": ""}
        ]
        df_init = pd.DataFrame(initial_data)
        ws.update([df_init.columns.values.tolist()] + df_init.values.tolist())
        return df_init

def convert_image_to_base64(uploaded_file):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            image.thumbnail((300, 300))
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=70)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str if len(img_str) <= 49000 else ""
        except Exception:
            return ""
    return ""

def convert_base64_to_image(base64_str):
    if base64_str and str(base64_str).strip() not in ["", "nan"]:
        try:
            return Image.open(io.BytesIO(base64.b64decode(base64_str)))
        except Exception:
            return None
    return None

def add_user_resep(username, nama, kategori, waktu, bahan, cara, kalori, uploaded_file):
    sh = get_spreadsheet()
    clean_user = "".join(e for e in str(username).lower() if e.isalnum())
    ws = sh.worksheet(f"Resep_{clean_user}")
    df = load_user_data(username)
    new_id = int(df["ID"].max() + 1) if not df.empty else 1
    ws.append_row([new_id, nama, kategori, waktu, bahan, cara, kalori if kalori else "-", convert_image_to_base64(uploaded_file)])
    return True


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.nama_pembeli = ""

if not st.session_state.logged_in:
    st.title("🔐 Login Asisten Dapur Digital")
    st.write("Silakan masuk menggunakan Username dan Password Anda.")
    with st.form("login_form"):
        input_user = st.text_input("Username / Email")
        input_pass = st.text_input("Password", type="password")
        if st.form_submit_button("Masuk ke Dapur Saya", type="primary"):
            if input_user and input_pass:
                with st.spinner("Memverifikasi akun..."):
                    valid, nama = verify_login(input_user, input_pass)
                    if valid:
                        st.session_state.logged_in = True
                        st.session_state.username = input_user
                        st.session_state.nama_pembeli = nama
                        st.rerun()
                    else:
                        st.error("Username atau Password salah!")
            else:
                st.warning("Mohon isi Username dan Password Anda.")
    st.stop()

col_header1, col_header2 = st.columns([4, 1])
with col_header1:
    st.title(f"🍳 Dapur Digital: {st.session_state.nama_pembeli}")
    st.caption("Perencana Menu Makan Mingguan & Daftar Belanja WhatsApp Otomatis")
with col_header2:
    if st.button("🚪 Keluar (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.nama_pembeli = ""
        st.session_state.pop("plan", None)
        st.rerun()

current_user = st.session_state.username
df_resep = load_user_data(current_user)
daftar_menu = ["Pilih Menu", "Makan di Luar"] + df_resep["Nama_Menu"].tolist()

if "plan" not in st.session_state:
    st.session_state.plan = {h: {"Sarapan": "Pilih Menu", "Makan Siang": "Pilih Menu", "Makan Malam": "Pilih Menu"} for h in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]}

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
        menu_terpilih = [st.session_state.plan[h][w] for h in hari_list for w in ["Sarapan", "Makan Siang", "Makan Malam"] if st.session_state.plan[h][w] not in ["Pilih Menu", "Makan di Luar"]]
        if menu_terpilih:
            bahan_final = [item.strip() for bahan_teks in df_resep[df_resep["Nama_Menu"].isin(menu_terpilih)]["Bahan_Bahan"].dropna() for item in str(bahan_teks).split(",")]
            bahan_unik = sorted(list(set(bahan_final)))
            status_belanja = {b: st.checkbox(f"⬜ {b}", key=f"shop_{b}") for b in bahan_unik}
            st.write("---")
            st.subheader("📲 Kirim Catatan ke WhatsApp")
            bahan_belum_dibeli = [b for b, sudah in status_belanja.items() if not sudah]
            if bahan_belum_dibeli:
                text_wa = f"*🚨 DAFTAR BELANJA ({st.session_state.nama_pembeli.upper()}) 🚨*\n\n" + "\n".join([f"{i}. ▫️ {b}" for i, b in enumerate(bahan_belum_dibeli, 1)]) + "\n\n_Dikirim dari Smart Meal Planner_"
                whatsapp_url = "https://wa.me" + "/?text=" + urllib.parse.quote(text_wa)
                st.link_button("🟢 Kirim Sisa Bahan Belanja ke WhatsApp", whatsapp_url, type="secondary")
            else:
                st.success("🎉 Semua bahan sudah selesai dicentang!")
        else:
            st.warning("Silakan pilih minimal 1 menu makanan pada jadwal di atas.")

with tab2:
    st.subheader("📚 Koleksi Resep Pribadi Anda")
    kategori_filter = st.radio("Filter Kategori:", ["Semua Kategori", "Rumahan & Hemat", "Diet & Sehat"], horizontal=True)
    df_tampil = df_resep if kategori_filter == "Semua Kategori" else df_resep[df_resep["Kategori"] == kategori_filter]
    if df_tampil.empty:
        st.info("Belum ada resep di kategori ini.")
    else:
        for _, row in df_tampil.iterrows():
            kalori_info = f" - {row['Estimasi_Kalori']}" if str(row['Estimasi_Kalori']) != "-" else ""
            with st.expander(f"📖 {row['Nama_Menu']} ({row['Kategori']}){kalori_info}"):
                col_img, col_txt = st.columns(2)
                with col_img:
                    img = convert_base64_to_image(row["Foto_Base64"])
                    st.image(img if img else "https://placehold.co" + "/400x300?text=Belum+Ada+Foto", use_container_width=True)
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
        bahan = st.text_area("Bahan-Bahan (Pisahkan dengan koma)*")
        cara = st.text_area("Langkah/Cara Memasak*")
        foto = st.file_uploader("Upload Foto Masakan", type=["jpg", "jpeg", "png"])
        if st.form_submit_button("Simpan ke Database Cloud"):
            if nama and bahan and cara:
                with st.spinner("Menyimpan ke cloud..."):
                    if add_user_resep(current_user, nama, kat, waktu, bahan, cara, kalori, foto):
                        st.success(f"🎉 Resep '{nama}' tersimpan di akun Anda!")
                        st.rerun()
            else:
                st.error("Mohon isi semua kolom bertanda bintang (*).")
