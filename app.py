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
            {"ID": 1, "Nama_Menu": "Tumis Kangkung Tempe", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "1 ikat kangkung, 1/2 papan tempe, 2 siung bawang putih, 3 siung bawang merah, 2 sdm saus tiram, garam", "Cara_Masak": "Goreng tempe dadu. Tumis duo bawang. Masukkan kangkung dan tempe, beri saus tiram dan garam.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 2, "Nama_Menu": "Nasi Goreng Kampung", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "2 piring nasi putih, 2 butir telur, 3 siung bawang merah, 2 siung bawang putih, 2 sdm kecap manis, 1 batang daun bawang", "Cara_Masak": "Orak-arik telur. Tumis bumbu halus. Masukkan nasi, kecap manis, garam, dan daun bawang, aduk rata.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 3, "Nama_Menu": "Telur Dadar Padang Tebal", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "4 butir telur ayam, 2 sdm tepung beras, 3 siung bawang merah iris, 2 cabai merah keriting iris, 1 lembar daun kunyit, garam", "Cara_Masak": "Kocok telur dengan larutan tepung beras dan semua irisan bumbu. Goreng dengan minyak panas api sedang hingga matang.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 4, "Nama_Menu": "Sayur Sop Ayam Bening", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "250g sayap ayam, 2 buah wortel, 1 buah kentang, 50g buncis, 3 siung bawang putih geprek, 1 batang seledri, lada bubuk", "Cara_Masak": "Rebus ayam dan bawang putih hingga kaldu keluar. Masukkan wortel dan kentang hingga empuk, tambahkan buncis, garam, lada, dan seledri.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 5, "Nama_Menu": "Tempe Orek Basah Kecap", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "1 papan tempe potong korek, 3 siung bawang merah, 2 siung bawang putih, 2 cabai hijau, 3 sdm kecap manis, 1 lembar daun salam", "Cara_Masak": "Goreng tempe setengah kering. Tumis bumbu iris dan daun salam. Masukkan tempe, kecap manis, dan sedikit air, masak hingga meresap.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 6, "Nama_Menu": "Ayam Goreng Lengkuas", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "500g ayam potong, 100g lengkuas parut, 4 siung bawang putih, 5 siung bawang merah, 2 cm kunyit, 2 lembar daun salam, ketumbar", "Cara_Masak": "Ungkep ayam bersama bumbu halus, lengkuas parut, dan daun salam hingga air menyusut. Goreng ayam dan serundeng lengkuas hingga keemasan.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 7, "Nama_Menu": "Sayur Asem Jakarta", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "1 buah jagung manis, 1 buah labu siam, 5 lonjor kacang panjang, 50g melinjo, 3 sdm air asam jawa, 4 siung bawang merah, 2 cabai merah", "Cara_Masak": "Rebus air bersama bumbu halus, jagung, dan melinjo. Masukkan labu siam, kacang panjang, air asam jawa, garam, dan gula merah.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 8, "Nama_Menu": "Tahu Crispy Cabai Garam", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "5 buah tahu putih potong dadu, 4 sdm tepung maizena, 3 siung bawang putih cincang, 3 cabai rawit iris, 1 batang daun bawang", "Cara_Masak": "Balur tahu dengan maizena lalu goreng garing. Tumis bawang putih, cabai, dan daun bawang, masukkan tahu goreng, beri garam dan lada.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 9, "Nama_Menu": "Ikan Kembung Balado", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "3 ekor ikan kembung, 6 cabai merah keriting, 4 siung bawang merah, 2 siung bawang putih, 1 buah tomat merah, jeruk nipis", "Cara_Masak": "Lumuri ikan dengan jeruk nipis dan garam lalu goreng matang. Tumis sambal balado halus hingga tanak, masukkan ikan goreng.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 10, "Nama_Menu": "Capcay Kuah Bakso", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "5 butir bakso sapi iris, 1 buah wortel, 100g kembang kol, 1 ikat sawi hijau, 3 siung bawang putih cincang, 1 sdm saus tiram, 1 sdt maizena", "Cara_Masak": "Tumis bawang putih dan bakso. Masukkan wortel, kembang kol, dan air. Bumbui saus tiram, garam, dan lada. Masukkan sawi dan larutan maizena.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 11, "Nama_Menu": "Bubur Ayam Gurih Rumahan", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "1 cup beras, 150g dada ayam suwir, 1 liter air kaldu, 2 lembar daun salam, kecap asin, daun bawang, bawang goreng", "Cara_Masak": "Masak beras dengan air kaldu, daun salam, dan garam sambil sesekali diaduk hingga menjadi bubur lembut. Sajikan dengan ayam suwir dan pelengkap.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 12, "Nama_Menu": "Perkedel Kentang Daging", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "300g kentang goreng halus, 50g daging cincang, 2 siung bawang putih goreng, 1 butir telur untuk celupan, seledri, pala bubuk", "Cara_Masak": "Campur kentang halus dengan daging cincang, bawang putih goreng halus, seledri, garam, dan pala. Bentuk bulat, celup telur, goreng keemasan.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 13, "Nama_Menu": "Tumis Buncis Jagung Muda", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "150g buncis iris serong, 5 buah jagung muda putren, 3 siung bawang merah, 2 siung bawang putih, 1 sdm saus tiram, cabai merah", "Cara_Masak": "Tumis bumbu iris hingga harum. Masukkan buncis, putren, dan sedikit air. Beri saus tiram, garam, dan gula, masak hingga matang renyah.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 14, "Nama_Menu": "Soto Ayam Kuah Kuning", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "500g ayam, 2 batang serai, 3 lembar daun jeruk, 2 cm kunyit bakar, 4 siung bawang putih, 5 siung bawang merah, soun, kol iris", "Cara_Masak": "Rebus ayam. Tumis bumbu halus bersama serai dan daun jeruk, masukkan ke kuah kaldu ayam. Sajikan dengan ayam suwir, soun, dan kol.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 15, "Nama_Menu": "Telur Balado Bulat", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "6 butir telur rebus kupas, 7 cabai merah keriting, 5 siung bawang merah, 2 siung bawang putih, 1 buah tomat, 1 lembar daun jeruk", "Cara_Masak": "Goreng telur rebus sebentar hingga berkulit. Tumis bumbu halus dan daun jeruk hingga matang berminyak, masukkan telur dan aduk rata.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 16, "Nama_Menu": "Bakwan Jagung Renyah", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "2 buah jagung manis sisir, 5 sdm tepung terigu, 1 sdm tepung beras, 2 siung bawang putih halus, 1 batang daun bawang, ketumbar", "Cara_Masak": "Campur jagung manis, tepung terigu, tepung beras, bumbu halus, dan sedikit air hingga adonan kental. Goreng sesendok demi sesendok hingga garing.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 17, "Nama_Menu": "Ayam Kecap Mentega", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "400g ayam potong goreng setengah matang, 2 sdm margarin, 1/2 bawang bombay iris, 2 siung bawang putih geprek, 3 sdm kecap manis, 1 sdm saus tiram", "Cara_Masak": "Lelehkan margarin, tumis bawang putih dan bombay. Masukkan ayam, kecap manis, saus tiram, dan sedikit air, masak hingga kuah mengental.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 18, "Nama_Menu": "Sayur Lodeh Labu Siam", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "1 buah labu siam potong korek, 50g tempe potong dadu, 1 bungkus santan instan 65ml, 4 siung bawang merah, 2 siung bawang putih, daun salam, lengkuas", "Cara_Masak": "Rebus bumbu halus, daun salam, lengkuas, labu siam, dan tempe hingga empuk. Tuang santan, garam, dan gula, aduk perlahan hingga mendidih.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 19, "Nama_Menu": "Mie Goreng Tek-Tek Rumahan", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "1 bungkus mie telur rebus, 2 butir telur, 3 lembar sawi hijau, 3 butir bakso iris, 3 siung bawang putih halus, 2 sdm kecap manis, 1 sdm saus tiram", "Cara_Masak": "Orak-arik telur, tumis bawang putih. Masukkan bakso, sawi, mie, kecap manis, saus tiram, dan lada. Aduk rata di api besar.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 20, "Nama_Menu": "Lele Goreng Sambal Terasi", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "4 ekor ikan lele bersih, 2 siung bawang putih halus, kunyit bubuk, 5 cabai rawit, 3 cabai merah, 1 sdt terasi bakar, 1 buah tomat", "Cara_Masak": "Marinasi lele dengan bawang putih, kunyit, dan garam lalu goreng kering. Goreng bahan sambal sebentar lalu ulek dengan terasi, garam, dan gula.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 21, "Nama_Menu": "Roti Bakar Telur Keju", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "4 lembar roti tawar, 2 butir telur kocok, 2 lembar keju slice, 1 sdm margarin, saus tomat secukupnya", "Cara_Masak": "Dadar telur tipis di teflon beroles margarin, tempelkan roti tawar di atasnya, balik, isi dengan keju slice, lipat dan panggang kecokelatan.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 22, "Nama_Menu": "Tumis Tauge Tahu Kuning", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "150g tauge bersih, 3 buah tahu kuning potong dadu, 3 siung bawang merah, 2 siung bawang putih, 1 batang daun bawang, garam, lada", "Cara_Masak": "Goreng tahu setengah matang. Tumis bawang merah dan putih, masukkan tahu dan tauge, beri garam, lada, dan daun bawang, aduk cepat 2 menit.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 23, "Nama_Menu": "Sup Bakso Sosis Wortel", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "6 butir bakso sapi, 2 buah sosis iris, 1 buah wortel iris bulat, 50g makaroni rebus, 2 siung bawang putih geprek, seledri", "Cara_Masak": "Didihkan air dengan bawang putih geprek. Masukkan wortel hingga empuk, lalu masukkan bakso, sosis, makaroni, garam, lada, dan seledri.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 24, "Nama_Menu": "Cumi Asin Cabai Hijau", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "150g cumi asin rendam air panas, 6 cabai hijau besar iris serong, 4 siung bawang merah, 2 siung bawang putih, 1 buah tomat hijau", "Cara_Masak": "Potong cumi asin yang sudah dicuci bersih. Tumis duo bawang, cabai hijau, dan tomat hingga layu, masukkan cumi asin dan sedikit gula, aduk rata.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 25, "Nama_Menu": "Nasi Uduk Rice Cooker", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "2 cup beras, 1 bungkus santan instan 65ml, 2 batang serai geprek, 2 lembar daun salam, 1 lembar daun pandan, garam", "Cara_Masak": "Cuci beras, masukkan ke rice cooker bersama santan, air secukupnya, serai, daun salam, pandan, dan garam. Masak hingga matang dan aduk rata.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 26, "Nama_Menu": "Tempe Mendoan Hangat", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "1 papan tempe iris tipis lebar, 5 sdm tepung terigu, 1 sdm tepung beras, 2 batang daun bawang iris, 2 siung bawang putih, ketumbar, kunyit", "Cara_Masak": "Campur tepung dengan bumbu halus, irisan daun bawang, dan air. Celupkan tempe, goreng sebentar dalam minyak panas agar tetap lembut.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 27, "Nama_Menu": "Ayam Suwir Kemangi Pedas", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "300g dada ayam rebus suwir, 1 ikat daun kemangi, 5 cabai merah keriting, 3 cabai rawit, 4 siung bawang merah, 2 siung bawang putih, daun jeruk", "Cara_Masak": "Tumis bumbu halus dan daun jeruk hingga harum. Masukkan ayam suwir dan sedikit air kaldu, bumbui garam dan gula, terakhir masukkan kemangi.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 28, "Nama_Menu": "Sayur Bening Bayam Jagung", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "1 ikat bayam petik daunnya, 1 buah jagung manis potong, 3 siung bawang merah iris, 2 cm temu kunci geprek, garam, gula", "Cara_Masak": "Didihkan air bersama irisan bawang merah, temu kunci, dan jagung hingga matang. Masukkan bayam, garam, dan gula, masak 2 menit lalu angkat.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 29, "Nama_Menu": "Sarden Kaleng Tumis Bawang", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "1 kaleng kecil ikan sarden, 3 siung bawang merah iris, 2 siung bawang putih iris, 3 cabai rawit utuh, 1/2 bawang bombay iris", "Cara_Masak": "Tumis semua irisan bawang hingga harum. Tuang ikan sarden beserta sausnya dan cabai rawit, masak hingga mendidih dan kuah mengental.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 30, "Nama_Menu": "Martabak Telur Mini Kulit Lumpia", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "8 lembar kulit lumpia, 3 butir telur, 2 batang daun bawang iris, 50g kornet atau ayam cincang, garam, lada bubuk", "Cara_Masak": "Kocok telur bersama daun bawang, kornet, garam, dan lada. Tuang ke atas kulit lumpia di wajan datar sedikit minyak, lipat dan goreng garing.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {"ID": 31, "Nama_Menu": "Dada Ayam Panggang Teflon", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "150g dada ayam tanpa kulit, 1 siung bawang putih cincang, 1/2 sdt lada hitam, 1 sdm kecap asin, 1 sdt minyak zaitun", "Cara_Masak": "Marinasi ayam 15 menit. Panggang di teflon dengan minyak zaitun api kecil hingga matang kecokelatan.", "Estimasi_Kalori": "± 250 kkal", "Foto_Base64": ""},
            {"ID": 32, "Nama_Menu": "Oatmeal Pisang Chia Seed", "Kategori": "Diet & Sehat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "4 sdm rolled oats, 200ml susu rendah lemak, 1 buah pisang matang iris, 1 sdt chia seed, sejumput kayu manis bubuk", "Cara_Masak": "Masak oats dengan susu rendah lemak hingga mengental. Sajikan dengan potongan pisang, taburan chia seed, dan kayu manis.", "Estimasi_Kalori": "± 290 kkal", "Foto_Base64": ""},
            {"ID": 33, "Nama_Menu": "Pepes Ikan Kembung Kemangi", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "2 ekor ikan kembung, 1 ikat kemangi, 4 siung bawang merah, 2 siung bawang putih, 2 cm kunyit, 1 batang serai, daun pisang", "Cara_Masak": "Lumuri ikan dengan bumbu halus. Bungkus dengan daun pisang bersama kemangi dan serai, kukus 25 menit hingga matang tanpa minyak.", "Estimasi_Kalori": "± 240 kkal", "Foto_Base64": ""},
            {"ID": 34, "Nama_Menu": "Sup Ayam Jahe Bening", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "150g dada ayam potong dadu, 3 cm jahe iris tipis, 1 buah wortel, 100g brokoli, 2 siung bawang putih geprek, daun bawang", "Cara_Masak": "Rebus ayam bersama jahe dan bawang putih. Masukkan wortel dan brokoli hingga empuk, beri sedikit garam dan lada.", "Estimasi_Kalori": "± 220 kkal", "Foto_Base64": ""},
            {"ID": 35, "Nama_Menu": "Telur Rebus Alpukat Roti Gandum", "Kategori": "Diet & Sehat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "2 lembar roti gandum panggang, 1/2 buah alpukat matang lumat, 2 butir telur rebus iris, lada hitam, sedikit garam", "Cara_Masak": "Oleskan alpukat lumat di atas roti gandum panggang, susun irisan telur rebus di atasnya, taburi lada hitam dan garam.", "Estimasi_Kalori": "± 340 kkal", "Foto_Base64": ""},
            {"ID": 36, "Nama_Menu": "Tumis Brokoli Udang Bawang Putih", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "150g brokoli potong kuntum, 100g udang kupas, 2 siung bawang putih cincang, 1 sdt minyak zaitun, 1 sdm saus tiram", "Cara_Masak": "Tumis bawang putih dengan minyak zaitun, masukkan udang hingga berubah warna. Tambahkan brokoli, saus tiram, dan sedikit air.", "Estimasi_Kalori": "± 230 kkal", "Foto_Base64": ""},
            {"ID": 37, "Nama_Menu": "Gado-Gado Siram Tanpa Santan", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "100g bayam rebus, 100g tauge rebus, 1 buah tahu kukus, 1 butir telur rebus, 3 sdm bumbu kacang sangrai encer", "Cara_Masak": "Tata sayuran rebus, tahu kukus, dan telur rebus di piring. Siram dengan saus kacang sangrai yang diencerkan air hangat.", "Estimasi_Kalori": "± 330 kkal", "Foto_Base64": ""},
            {"ID": 38, "Nama_Menu": "Orak-Arik Putih Telur Bayam", "Kategori": "Diet & Sehat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "4 putih telur dan 1 telur utuh, 1 genggam bayam cincang, 3 buah tomat ceri belah dua, 1 sdt minyak zaitun, lada", "Cara_Masak": "Tumis bayam dan tomat ceri dengan minyak zaitun hingga layu. Tuang kocokan telur, beri garam dan lada, orak-arik hingga matang.", "Estimasi_Kalori": "± 210 kkal", "Foto_Base64": ""},
            {"ID": 39, "Nama_Menu": "Tahu Kukus Siram Daging Cincang", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "2 buah tahu sutra putih, 80g daging ayam cincang tanpa lemak, 2 siung bawang putih cincang, 1 sdm kecap asin, daun bawang", "Cara_Masak": "Kukus tahu sutra 10 menit. Tumis bawang putih dan ayam cincang dengan sedikit air dan kecap asin, siramkan ke atas tahu kukus.", "Estimasi_Kalori": "± 245 kkal", "Foto_Base64": ""},
            {"ID": 40, "Nama_Menu": "Salad Dada Ayam Wijen Sangrai", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "120g dada ayam rebus suwir, 100g selada romain, 1/2 buah timun iris, 5 buah tomat ceri, 1.5 sdm dressing wijen sangrai", "Cara_Masak": "Campurkan seluruh sayuran segar dan suwiran dada ayam dalam mangkuk, siram dengan dressing wijen sangrai sebelum disajikan.", "Estimasi_Kalori": "± 280 kkal", "Foto_Base64": ""},
            {"ID": 41, "Nama_Menu": "Smoothie Bowl Naga Pisang", "Kategori": "Diet & Sehat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "100g buah naga merah beku, 1/2 buah pisang beku, 100ml yogurt plain rendah lemak, 1 sdm granola", "Cara_Masak": "Blender buah naga, pisang, dan yogurt hingga lembut kental. Tuang ke mangkuk dan beri taburan granola di atasnya.", "Estimasi_Kalori": "± 260 kkal", "Foto_Base64": ""},
            {"ID": 42, "Nama_Menu": "Ikan Dori Panggang Lemon", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "150g fillet ikan dori, 1 sdm air perasan lemon, 1 siung bawang putih parut, 1/2 sdt oregano kering, 1 sdt minyak zaitun", "Cara_Masak": "Marinasi ikan dori dengan lemon, bawang putih, oregano, dan garam. Panggang di teflon anti lengket hingga matang lembut.", "Estimasi_Kalori": "± 235 kkal", "Foto_Base64": ""},
            {"ID": 43, "Nama_Menu": "Nasi Merah Ayam Teriyaki Sehat", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "100g nasi merah matang, 120g dada ayam potong dadu, 1.5 sdm saus teriyaki, 1/4 bawang bombay iris, 50g buncis rebus", "Cara_Masak": "Tumis bawang bombay dan dada ayam tanpa minyak di wajan anti lengket, masukkan saus teriyaki dan sedikit air. Sajikan dengan nasi merah dan buncis.", "Estimasi_Kalori": "± 360 kkal", "Foto_Base64": ""},
            {"ID": 44, "Nama_Menu": "Sup Krim Labu Kuning Tanpa Krim", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "200g labu kuning kukus, 150ml susu rendah lemak, 1 siung bawang putih tumis, pala bubuk, garam, lada", "Cara_Masak": "Blender labu kuning kukus bersama susu dan bawang putih hingga halus. Masak kembali sebentar dengan garam, lada, dan pala bubuk.", "Estimasi_Kalori": "± 195 kkal", "Foto_Base64": ""},
            {"ID": 45, "Nama_Menu": "Urap Sayur Kelapa Sangrai", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "100g bayam rebus, 100g kacang panjang rebus, 50g tauge rebus, 3 sdm kelapa parut sangrai bumbu kencur", "Cara_Masak": "Sangrai kelapa parut dengan bumbu halus kencur, bawang putih, dan cabai hingga kering harum. Campurkan bersama sayuran rebus.", "Estimasi_Kalori": "± 215 kkal", "Foto_Base64": ""},
            {"ID": 46, "Nama_Menu": "Overnight Oats Apel Kayu Manis", "Kategori": "Diet & Sehat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "4 sdm rolled oats, 150ml susu almond atau rendah lemak, 1/2 buah apel potong dadu, 1 sdt madu, kayu manis bubuk", "Cara_Masak": "Campur semua bahan dalam wadah tertutup, simpan di kulkas semalaman agar oats lembut dan siap disantap pagi hari.", "Estimasi_Kalori": "± 275 kkal", "Foto_Base64": ""},
            {"ID": 47, "Nama_Menu": "Tumis Pakcoy Jamur Saus Tiram", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "2 bonggol pakcoy belah dua, 100g jamur kancing iris, 2 siung bawang putih cincang, 1 sdm saus tiram, 1 sdt minyak wijen", "Cara_Masak": "Tumis bawang putih dan jamur hingga layu. Masukkan pakcoy, saus tiram, minyak wijen, dan sedikit air, masak cepat hingga hijau segar.", "Estimasi_Kalori": "± 150 kkal", "Foto_Base64": ""},
            {"ID": 48, "Nama_Menu": "Pecel Sayur Bumbu Sangrai", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Siang", "Bahan_Bahan": "100g kangkung rebus, 100g kol rebus, 50g tauge rebus, 1 potong tempe panggang, 2.5 sdm sambal pecel kacang sangrai", "Cara_Masak": "Seduh sambal pecel sangrai dengan air hangat. Siramkan di atas sayuran rebus dan sajikan bersama tempe panggang tanpa minyak.", "Estimasi_Kalori": "± 310 kkal", "Foto_Base64": ""},
            {"ID": 49, "Nama_Menu": "Capcay Kuah Bening Dada Ayam", "Kategori": "Diet & Sehat", "Waktu_Makan": "Makan Malam", "Bahan_Bahan": "100g dada ayam iris tipis, 1 buah wortel, 100g kembang kol, 1 ikat sawi putih, 2 siung bawang putih geprek, lada", "Cara_Masak": "Tumis bawang putih dengan sedikit air, masukkan dada ayam hingga berubah warna. Tambahkan kaldu, wortel, kembang kol, sawi, garam, dan lada.", "Estimasi_Kalori": "± 225 kkal", "Foto_Base64": ""},
            {"ID": 50, "Nama_Menu": "Telur Dadar Gulung Sayuran", "Kategori": "Diet & Sehat", "Waktu_Makan": "Sarapan", "Bahan_Bahan": "3 butir telur ayam, 2 sdm wortel cincang halus, 1 batang daun bawang iris, 1 sdt minyak zaitun, garam, lada", "Cara_Masak": "Kocok telur bersama wortel cincang, daun bawang, garam, dan lada. Tuang bertahap di teflon anti lengket dan gulung perlahan hingga matang.", "Estimasi_Kalori": "± 240 kkal", "Foto_Base64": ""}
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
