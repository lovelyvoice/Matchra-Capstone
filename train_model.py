import pandas as pd
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_PATH = "data/processed/clean_matchra_dataset.csv"
MODEL_DIR = "data/model"

def train_and_export_model():
    print("🚀 Memulai Pelatihan Model AI (TF-IDF)...")
    
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Dataset {DATA_PATH} tidak ditemukan! Jalankan data_preprocessing.py dulu.")
        return
        
    df = pd.read_csv(DATA_PATH)
    df['soup'] = df['soup'].fillna('')
    
    print(f"Memproses {len(df)} game untuk dipelajari...")
    
    # Inisialisasi Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Proses Training (Fitting)
    print("Membangun matriks kecerdasan (TF-IDF Matrix)...")
    tfidf_matrix = vectorizer.fit_transform(df['soup'])
    
    # Buat direktori model jika belum ada
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    # Ekspor (Simpan) Model ke dalam format fisik
    vectorizer_path = os.path.join(MODEL_DIR, "matchra_vectorizer.pkl")
    matrix_path = os.path.join(MODEL_DIR, "matchra_matrix.pkl")
    
    print("Menyimpan file model (.pkl)...")
    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(tfidf_matrix, matrix_path)
    
    print(f"✅ Training Selesai! Model fisik berhasil diekspor ke:")
    print(f"   - {vectorizer_path}")
    print(f"   - {matrix_path}")
    print("Sekarang server web bisa berjalan lebih cepat tanpa perlu training dari awal!")

if __name__ == "__main__":
    train_and_export_model()
