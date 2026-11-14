import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64
from PIL import Image
import io

def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def verify_login(username, password):
    """Memeriksa apakah username dan password terdaftar di sheet 'Users'."""
    conn = get_connection()
    try:
        df_users = conn.read(worksheet="Users", ttl=0)
        df_users["Username"] = df_users["Username"].astype(str)
        df_users["Password"] = df_users["Password"].astype(str)
        
        user_match = df_users[
            (df_users["Username"] == str(username).strip()) & 
            (df_users["Password"] == str(password).strip())
        ]
        
        if not user_match.empty:
            return True, user_match.iloc[0]["Nama_Pembeli"]
        return False, None
    except Exception as e:
        st.error(f"Gagal terhubung ke database user: {e}")
        return False, None

def get_user_worksheet_name(username):
    """Membuat nama tab sheet yang bersih dan unik untuk setiap pembeli."""
    clean_user = "".join(e for e in str(username) if e.isalnum())
    return f"Resep_{clean_user}"

def init_user_database(username):
    """Membuatkan sheet khusus untuk user jika belum ada + isi resep awal."""
    conn = get_connection()
    sheet_name = get_user_worksheet_name(username)
    
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df
    except Exception:
        # Data resep awal otomatis disuntikkan saat user pertama kali login
        initial_data = [
            {
                "ID": 1,
                "Nama_Menu": "Tumis Kangkung Tempe",
                "Kategori": "Rumahan & Hemat",
                "Waktu_Makan": "Makan Siang",
                "Bahan_Bahan": "1 ikat kangkung, 1/2 papan tempe, 2 siung bawang putih, 3 siung bawang merah, 2 sdm saus tiram, secukupnya garam",
                "Cara_Masak": "Goreng tempe dadu. Tumis duo bawang. Masukkan kangkung dan tempe, beri saus tiram dan garam.",
                "Estimasi_Kalori": "-",
                "Foto_Base64": ""
            },
            {
                "ID": 2,
                "Nama_Menu": "Dada Ayam Panggang Teflon",
                "Kategori": "Diet & Sehat",
                "Waktu_Makan": "Makan Malam",
                "Bahan_Bahan": "150g dada ayam tanpa kulit, 1 siung bawang putih cincang, 1/2 sdt lada hitam, 1 sdm kecap asin, 1 sdt minyak zaitun",
                "Cara_Masak": "Marinasi ayam 15 menit. Panggang di teflon dengan minyak zaitun api kecil hingga matang.",
                "Estimasi_Kalori": "± 250 kkal",
                "Foto_Base64": ""
            }
        ]
        df_init = pd.DataFrame(initial_data)
        conn.create(worksheet=sheet_name, data=df_init)
        return df_init

def load_user_data(username):
    return init_user_database(username)

def convert_image_to_base64(uploaded_file):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            image.thumbnail((300, 300)) 
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=70)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            if len(img_str) > 49000:
                st.warning("Ukuran foto terlalu kompleks, foto tidak disimpan agar database tidak error.")
                return ""
            return img_str
        except Exception:
            return ""
    return ""

def convert_base64_to_image(base64_str):
    if base64_str and str(base64_str).strip() != "" and str(base64_str) != "nan":
        try:
            img_data = base64.b64decode(base64_str)
            return Image.open(io.BytesIO(img_data))
        except Exception:
            return None
    return None

def add_user_resep(username, nama, kategori, waktu, bahan, cara, kalori, uploaded_file):
    conn = get_connection()
    sheet_name = get_user_worksheet_name(username)
    df = load_user_data(username)
    
    new_id = int(df["ID"].max() + 1) if not df.empty else 1
    foto_b64 = convert_image_to_base64(uploaded_file)
    
    new_row = {
        "ID": new_id,
        "Nama_Menu": nama,
        "Kategori": kategori,
        "Waktu_Makan": waktu,
        "Bahan_Bahan": bahan,
        "Cara_Masak": cara,
        "Estimasi_Kalori": kalori if kalori else "-",
        "Foto_Base64": foto_b64
    }
    
    df_updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    conn.update(worksheet=sheet_name, data=df_updated)
    return True
