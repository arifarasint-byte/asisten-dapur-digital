import os
import base64
import pandas as pd
from PIL import Image
import io

# Konstanta jalur file database
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "database.xlsx")

def init_database():
    """
    Membuat folder 'database' dan file 'database.xlsx' secara otomatis
    jika file tersebut belum ada di sistem/GitHub.
    """
    # Buat folder jika belum ada
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"📁 Folder '{DB_DIR}' berhasil dibuat.")
        
    # Buat file Excel dengan struktur kolom jika belum ada
    if not os.path.exists(DB_PATH):
        columns = [
            "ID", "Nama_Menu", "Kategori", "Waktu_Makan", 
            "Bahan_Bahan", "Cara_Masak", "Estimasi_Kalori", "Foto_Base64"
        ]
        # Membuat contoh data awal (Seed Data) agar aplikasi tidak kosong saat pertama run
        initial_data = [
            # === CATEGORY: RUMAHAN & HEMAT (30 RESEP) ===
	    {	"ID": 1, "Nama_Menu": "Tumis Kangkung Tempe", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "1 ikat kangkung, 1/2 papan tempe, 2 siung bawang putih, 3 siung bawang merah, 2 sdm saus tiram, secukupnya garam", 
             	"Cara_Masak": "Goreng tempe dadu. Tumis duo bawang. Masukkan kangkung dan tempe, beri saus tiram dan garam. Masak cepat.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
	    {	"ID": 1, "Nama_Menu": "Tumis Kangkung Tempe", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "1 ikat kangkung, 1/2 papan tempe, 2 siung bawang putih, 3 siung bawang merah, 2 sdm saus tiram, secukupnya garam", 
             	"Cara_Masak": "Goreng tempe dadu. Tumis duo bawang. Masukkan kangkung dan tempe, beri saus tiram dan garam. Masak cepat.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 2, "Nama_Menu": "Ayam Goreng Lengkuas", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "500g daging ayam, 200g lengkuas parut, 2 lembar daun salam, 1 batang serai, 3 siung bawang putih, 1 sdt kunyit bubuk, secukupnya garam", 
             	"Cara_Masak": "Ungkep ayam dengan bumbu halus, lengkuas parut, salam, dan serai hingga meresap. Goreng ayam dan remahan lengkuasnya hingga keemasan.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 3, "Nama_Menu": "Sayur Asem Jakarta", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "1 buah labu siam, 1 buah jagung manis, 50g kacang panjang, 30g daun melinjo, 2 lembar daun salam, 1 ruas lengkuas, 3 buah asam jawa, secukupnya garam", 
             	"Cara_Masak": "Rebus air bersama bumbu racik, daun salam, dan lengkuas. Masukkan jagung dan labu siam hingga empuk, lalu susul sayuran lainnya. Beri garam.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 4, "Nama_Menu": "Telur Dadar Gulung Sawi", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", 
             	"Bahan_Bahan": "3 butir telur, 2 lembar sawi hijau cincang, 1 batang daun bawang, 1/2 sdt merica, secukupnya garam, 1 sdm minyak", 
             	"Cara_Masak": "Kocok telur bersama sawi, daun bawang, garam, dan merica. Tuang tipis di teflon, gulung perlahan, ulangi sampai adonan habis.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 5, "Nama_Menu": "Bakwan Jagung Crispy", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", 
             	"Bahan_Bahan": "2 buah jagung manis pipil, 4 sdm tepung terigu, 2 sdm tepung beras, 1 batang daun bawang, 1 siung bawang putih, secukupnya garam, secukupnya air", 
             	"Cara_Masak": "Campur jagung, tepung, daun bawang, bumbu halus, dan air hingga kental. Goreng sesendok demi sesendok dalam minyak panas hingga garing.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 6, "Nama_Menu": "Orek Tempe Basah", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "1 papan tempe, 3 siung bawang merah, 2 siung bawang putih, 2 buah cabai merah, 3 sdm kecap manis, 1 lembar daun salam, secukupnya garam", 
             	"Cara_Masak": "Potong tempe memanjang, goreng setengah matang. Tumis bumbu, masukkan kecap manis dan sedikit air. Masukkan tempe, masak hingga meresap.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 7, "Nama_Menu": "Sop Ayam Ceker Bening", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", 
             	"Bahan_Bahan": "250g ceker ayam, 2 buah wortel, 2 buah kentang, 1 batang seledri, 2 siung bawang putih geprek, 1/2 sdt pala bubuk, secukupnya garam dan merica", 
             	"Cara_Masak": "Rebus ceker hingga empuk, buang buihnya. Masukkan bawang putih, pala, wortel, dan kentang. Masak hingga matang, taburi seledri.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 8, "Nama_Menu": "Sambal Goreng Kentang Ati", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "3 buah kentang, 2 pasang ati ampela rebus, 5 buah cabai merah keriting, 3 siung bawang merah, 2 siung bawang putih, 1 bungkus santan instan kecil, secukupnya garam", 
             	"Cara_Masak": "Potong dadu kentang dan ati ampela, goreng terpisah. Tumis bumbu halus, masukkan santan. Masukkan kentang dan ati, aduk hingga bumbu mengering.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 9, "Nama_Menu": "Tumis Tahu Toge Saus Tiram", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", 
             	"Bahan_Bahan": "5 buah tahu putih, 100g tauge, 2 siung bawang putih, 2 sdm saus tiram, 1 batang daun bawang, secukupnya garam", 
             	"Cara_Masak": "Potong dadu tahu, goreng setengah matang. Tumis bawang putih, masukkan tauge dan tahu. Tambahkan saus tiram, garam, dan daun bawang. Angkat cepat.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 10, "Nama_Menu": "Cah Sawi Putih Telur", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", 
             	"Bahan_Bahan": "1 bonggol sawi putih, 1 butir telur, 2 siung bawang putih cincang, 2 buah cabai rawit, secukupnya garam dan kaldu bubuk", 
             	"Cara_Masak": "Tumis bawang putih dan cabai. Masukkan telur, buat orak-arik. Masukkan potongan sawi putih, beri garam dan sedikit air. Masak hingga layu.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 11, "Nama_Menu": "Perkedel Kentang Lembut", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "500g kentang, 1 batang seledri cincang, 2 siung bawang putih goreng, 1 butir telur kocok, secukupnya garam dan merica", 
             	"Cara_Masak": "Potong kentang, goreng lalu haluskan bersama bawang putih goreng. Campur seledri, garam, merica. Bentuk bulat pipih, celup telur, goreng.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 12, "Nama_Menu": "Ikan Asin Balado", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "100g ikan asin bulu ayam, 5 buah cabai merah, 3 siung bawang merah, 1 siung bawang putih, 1 sdt gula merah, secukupnya minyak", 
             	"Cara_Masak": "Goreng ikan asin hingga renyah, tiriskan. Tumis bumbu halus kasar dan gula merah hingga matang. Matikan api, tunggu agak hangat, campur ikan asin.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 13, "Nama_Menu": "Soto Ayam Lamongan", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "300g daging ayam, 1 bungkus bumbu soto instan, 50g soun rebus, 100g kol iris, 1 batang seledri, secukupnya bawang goreng, secukupnya air", 
             	"Cara_Masak": "Rebus ayam dengan bumbu soto hingga matang, angkat lalu suwir ayamnya. Tata soun dan kol di mangkuk, siram kuah panas, beri suwiran ayam.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 14, "Nama_Menu": "Nasi Goreng Kampung", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Sarapan", 
             	"Bahan_Bahan": "2 piring nasi putih dingin, 3 siung bawang merah, 2 siung bawang putih, 2 buah cabai rawit, 1 butir telur, 1 sdm kecap manis, secukupnya garam", 
             	"Cara_Masak": "Tumis bumbu halus, masukkan telur orak-arik. Masukkan nasi, beri kecap manis dan garam. Aduk cepat dengan api besar hingga bumbu merata.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 15, "Nama_Menu": "Mie Goreng Jawa", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", 
            	 "Bahan_Bahan": "1 bungkus mie telur rebus, 50g kol iris, 1 butir telur, 2 siung bawang putih, 2 butir kemiri, 3 sdm kecap manis, secukupnya garam", 
             	"Cara_Masak": "Haluskan bawang putih dan kemiri, tumis hingga wangi. Masukkan telur dan kol. Masukkan mie, tambahkan kecap manis dan garam. Aduk rata.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 16, "Nama_Menu": "Fuyunghai Telur Ekonomis", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Malam", 
            	"Bahan_Bahan": "3 butir telur, 50g kol iris halus, 1/2 buah wortel serut, 2 sdm tepung terigu, 3 sdm saus tomat, 1 siung bawang putih, secukupnya gula dan garam", 
            	 "Cara_Masak": "Campur telur, kol, wortel, terigu, dan garam, goreng tebal. Saus: Tumis bawang putih, masukkan saus tomat, sedikit air, gula, dan garam. Siram di atas telur.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 17, "Nama_Menu": "Capcay Goreng Bakso", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "1 buah wortel, 50g kembang kol, 5 lembar sawi hijau, 5 butir bakso sapi iris, 2 siung bawang putih cincang, 1 sdm saus tiram, 1 sdt tepung maizena", 
             	"Cara_Masak": "Tumis bawang putih dan bakso. Masukkan wortel dan kembang kol, beri sedikit air. Masukkan sawi, saus tiram, garam. Kentalkan dengan larutan maizena.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 18, "Nama_Menu": "Semur Tahu Tempe", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "5 buah tahu kulit, 1/2 papan tempe potong, 4 siung bawang merah, 2 siung bawang putih, 5 sdm kecap manis, 1/4 sdt pala bubuk, secukupnya garam", 
             	"Cara_Masak": "Tumis bumbu halus duo bawang dan pala. Masukkan tahu, tempe, kecap manis, garam, dan air. Masak dengan api kecil hingga air menyusut dan meresap.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 19, "Nama_Menu": "Sayur Lodeh Labu Siam", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "1 buah labu siam potong korek api, 1 bungkus santan instan kecil, 2 siung bawang putih, 3 siung bawang merah, 1 ruas lengkuas, 1 lembar daun salam, secukupnya garam", 
             	"Cara_Masak": "Rebus air bersama irisan duo bawang, salam, dan lengkuas. Masukkan labu siam hingga empuk. Tambahkan santan dan garam, aduk terus agar tidak pecah.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
            {	"ID": 20, "Nama_Menu": "Ayam Kecap Bawang Bombay", "Kategori": "Rumahan & Hemat", "Waktu_Makan": "Makan Siang", 
             	"Bahan_Bahan": "500g daging ayam potongan, 1/2 buah bawang bombay iris, 2 siung bawang putih geprek, 4 sdm kecap manis, 1 sdm saus tiram, secukupnya garam",
	        "Cara_Masak": "Goreng ayam setengah matang. Tumis bawang putih dan bombay hingga wangi. Masukkan ayam, kecap manis, saus tiram, garam, dan sedikit air. Masak hingga meresap.", "Estimasi_Kalori": "-", "Foto_Base64": ""},
        ]
        df = pd.DataFrame(initial_data, columns=columns)
        
        # Simpan ke Excel
        with pd.ExcelWriter(DB_PATH, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Resep")
        print(f"📊 File database '{DB_PATH}' berhasil diinisialisasi.")
    else:
        print(f"✅ File database '{DB_PATH}' sudah ada.")

def load_data():
    """Membaca seluruh data resep dari Excel menjadi Pandas DataFrame."""
    init_database()  # Pastikan file ada sebelum dibaca
    return pd.read_excel(DB_PATH, sheet_name="Resep")

def convert_image_to_base64(uploaded_file):
    """Mengubah file foto yang diupload di Streamlit menjadi teks string Base64."""
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            # Kompres gambar agar ukuran file Excel tidak terlalu membengkak
            image.thumbnail((500, 500)) 
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            print(f"Gagal mengonversi gambar: {e}")
            return ""
    return ""

def convert_base64_to_image(base64_str):
    """Mengubah kembali teks Base64 dari Excel menjadi objek Gambar untuk ditampilkan."""
    if base64_str and str(base64_str).strip() != "" and str(base64_str) != "nan":
        try:
            img_data = base64.b64decode(base64_str)
            return Image.open(io.BytesIO(img_data))
        except Exception as e:
            print(f"Gagal memuat gambar dari Base64: {e}")
            return None
    return None

def add_resep(nama, kategori, waktu, bahan, cara, kalori, uploaded_file):
    """Menambahkan data resep baru beserta fotonya ke dalam Excel."""
    df = load_data()
    
    # Generate ID baru secara berurutan
    new_id = int(df["ID"].max() + 1) if not df.empty else 1
    
    # Konversi foto ke base64 jika ada
    foto_b64 = convert_image_to_base64(uploaded_file)
    
    # Buat baris baru
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
    
    # Gabungkan ke DataFrame lama dan simpan kembali ke Excel
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    with pd.ExcelWriter(DB_PATH, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resep")
    return True
