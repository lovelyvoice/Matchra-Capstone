import os
import zipfile
import subprocess
import sys

# Konfigurasi Dataset Kaggle yang akan diunduh
DATASETS = [
    # Dataset 1: Steam Store Games (Sangat lengkap: ada harga, tags, genre, description)
    "nikdavis/steam-store-games",
    # Dataset 2: RAWG API Data (sebagai cadangan / pelengkap gambar jika butuh)
    "jummyegg/rawg-game-dataset" 
]

DATA_DIR = "data/raw"

def install_kaggle():
    try:
        import kaggle
        print("✅ Library 'kaggle' sudah terinstal.")
    except ImportError:
        print("⚙️ Menginstal library 'kaggle'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle"])
        print("✅ Library 'kaggle' berhasil diinstal!")

def check_kaggle_auth():
    # Cek apakah kaggle.json ada di direktori default
    user_home = os.path.expanduser("~")
    kaggle_path = os.path.join(user_home, ".kaggle", "kaggle.json")
    
    if not os.path.exists(kaggle_path):
        print(f"❌ KESALAHAN: File '{kaggle_path}' tidak ditemukan.")
        print("\n--- CARA MENDAPATKAN KAGGLE.JSON ---")
        print("1. Buka https://www.kaggle.com/ dan login.")
        print("2. Klik foto profilmu di kanan atas -> Pilih 'Settings' (Pengaturan).")
        print("3. Scroll ke bawah ke bagian 'API'.")
        print("4. Klik 'Create New Token'. File 'kaggle.json' akan terunduh otomatis.")
        print(f"5. Pindahkan file 'kaggle.json' tersebut ke dalam folder: {os.path.join(user_home, '.kaggle')}")
        print("   (Buat folder '.kaggle' jika belum ada)")
        print("------------------------------------\n")
        return False
    return True

def download_and_extract(dataset_name):
    print(f"\n⏳ Memulai unduhan: {dataset_name}...")
    import kaggle
    
    # Authenticate via kaggle API
    kaggle.api.authenticate()
    
    try:
        # Download dataset
        kaggle.api.dataset_download_files(dataset_name, path=DATA_DIR, unzip=True)
        print(f"✅ Berhasil mengunduh dan mengekstrak: {dataset_name} ke folder '{DATA_DIR}'")
    except Exception as e:
        print(f"❌ Gagal mengunduh {dataset_name}. Error: {e}")

def main():
    print("=== SCRIPT UNDUH OTOMATIS DATASET MATCHRA ===\n")
    
    # 1. Pastikan folder data siap
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 Folder '{DATA_DIR}' berhasil dibuat.")
        
    # 2. Instal kaggle jika belum ada
    install_kaggle()
    
    # 3. Cek Autentikasi Kaggle
    if not check_kaggle_auth():
        sys.exit(1)
        
    # 4. Unduh semua dataset
    for dataset in DATASETS:
        download_and_extract(dataset)
        
    print("\n🎉 SEMUA SELESAI! Data sudah siap di folder 'data/raw'.")
    print("Langkah selanjutnya adalah membuat skrip Preprocessing!")

if __name__ == "__main__":
    main()
