import streamlit as st
import gspread
import pandas as pd
import base64
from PIL import Image
import io

def get_spreadsheet():
    """Membuka file Google Sheets menggunakan data rahasia dari Streamlit Secrets."""
    secrets = dict(st.secrets["connections"]["gsheets"])
    spreadsheet_url = secrets.pop("spreadsheet")
    gc = gspread.service_account_from_dict(secrets)
    return gc.open_by_url(spreadsheet_url)

def verify_login(username, password):
    """Memeriksa kecocokan Username dan Password di sheet 'Users'."""
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("Users")
        df_users = pd.DataFrame(ws.get_all_records())
        
        if df_users.empty:
            return False, None
            
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
    sh = get_spreadsheet()
    sheet_name = get_user_worksheet_name(username)
    
    try:
        ws = sh.worksheet(sheet_name)
        df = pd.DataFrame(ws.get_all_records())
        return df
    except gspread.WorksheetNotFound:
        # Buat tab worksheet baru otomatis jika user baru pertama login
        ws = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
        
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
        # Tulis header dan data awal ke Google Sheets
        ws.update([df_init.columns.values.tolist()] + df_init.values.tolist())
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
                st.warning("Ukuran foto terlalu kompleks, foto tidak disimpan agar sel Google Sheets tidak penuh.")
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
    sh = get_spreadsheet()
    sheet_name = get_user_worksheet_name(username)
    ws = sh.worksheet(sheet_name)
    df = load_user_data(username)
    
    new_id = int(df["ID"].max() + 1) if not df.empty else 1
    foto_b64 = convert_image_to_base64(uploaded_file)
    
    new_row = [
        new_id, nama, kategori, waktu, bahan, cara, 
        kalori if kalori else "-", foto_b64
    ]
    
    # Tambahkan langsung sebagai baris baru di paling bawah Google Sheets
    ws.append_row(new_row)
    return True
