import pandas as pd
import os
import joblib
import json
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline

DATA_PATH = "data/processed/clean_matchra_dataset.csv"
MODEL_DIR = "data/model"

def train_and_export_model():
    print("=" * 60)
    print("MATCHRA -- PROSES PELATIHAN MODEL ML (TF-IDF + LSA/SVD)")
    print("=" * 60)

    if not os.path.exists(DATA_PATH):
        print("ERROR: Dataset tidak ditemukan!")
        print("   Jalankan: python data_preprocessing.py")
        return

    # ---------------------------------------------------------
    # STEP 1: Muat Dataset
    # ---------------------------------------------------------
    print("\n[STEP 1/5] Memuat dataset...")
    df = pd.read_csv(DATA_PATH)
    df['soup'] = df['soup'].fillna('')
    total_games = len(df)
    print(f"   OK - {total_games:,} game berhasil dimuat.")

    # ---------------------------------------------------------
    # STEP 2: TF-IDF Vectorization
    # ---------------------------------------------------------
    print("\n[STEP 2/5] Menjalankan TF-IDF Vectorization...")
    t0 = time.time()
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=15000,
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    tfidf_matrix = vectorizer.fit_transform(df['soup'])
    tfidf_time = time.time() - t0
    vocab_size = len(vectorizer.vocabulary_)
    print(f"   OK - TF-IDF selesai dalam {tfidf_time:.2f}s")
    print(f"   Vocabulary Size : {vocab_size:,} kata unik")
    print(f"   Matrix Shape    : {tfidf_matrix.shape[0]} game x {tfidf_matrix.shape[1]} fitur")

    # ---------------------------------------------------------
    # STEP 3: TRAINING -- Truncated SVD (Latent Semantic Analysis)
    # SVD menemukan "konsep laten" dari pola kata di seluruh dataset.
    # Model ini BELAJAR representasi semantik, bukan sekadar counting.
    # ---------------------------------------------------------
    print("\n[STEP 3/5] Melatih model SVD (Latent Semantic Analysis)...")
    print("   INFO: SVD mempelajari dimensi konsep tersembunyi dari data...")
    t1 = time.time()

    N_COMPONENTS = 150
    svd = TruncatedSVD(n_components=N_COMPONENTS, random_state=42, n_iter=7)
    normalizer = Normalizer(copy=False)
    lsa_pipeline = make_pipeline(svd, normalizer)

    # ---- INI PROSES TRAINING SESUNGGUHNYA ----
    lsa_matrix = lsa_pipeline.fit_transform(tfidf_matrix)

    svd_time = time.time() - t1
    explained_variance = float(np.sum(svd.explained_variance_ratio_) * 100)
    variance_per_component = svd.explained_variance_ratio_.tolist()

    print(f"   OK - SVD Training selesai dalam {svd_time:.2f}s")
    print(f"   Komponen laten dipelajari : {N_COMPONENTS}")
    print(f"   Total Variance Explained  : {explained_variance:.2f}%")
    print(f"   Top-5 component variance  : {[round(v*100,2) for v in variance_per_component[:5]]}")

    # ---------------------------------------------------------
    # STEP 4: Simpan Model Fisik (.pkl)
    # ---------------------------------------------------------
    print("\n[STEP 4/5] Mengekspor model ke file .pkl...")
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    vectorizer_path = os.path.join(MODEL_DIR, "matchra_vectorizer.pkl")
    svd_path        = os.path.join(MODEL_DIR, "matchra_svd.pkl")
    lsa_matrix_path = os.path.join(MODEL_DIR, "matchra_lsa_matrix.pkl")
    matrix_path     = os.path.join(MODEL_DIR, "matchra_matrix.pkl")

    joblib.dump(vectorizer,   vectorizer_path)
    joblib.dump(lsa_pipeline, svd_path)
    joblib.dump(lsa_matrix,   lsa_matrix_path)
    joblib.dump(tfidf_matrix, matrix_path)

    print(f"   OK - matchra_vectorizer.pkl  ({os.path.getsize(vectorizer_path)//1024} KB)")
    print(f"   OK - matchra_svd.pkl          ({os.path.getsize(svd_path)//1024} KB)")
    print(f"   OK - matchra_lsa_matrix.pkl   ({os.path.getsize(lsa_matrix_path)//1024} KB)")

    # ---------------------------------------------------------
    # STEP 5: Simpan Training Report (JSON)
    # ---------------------------------------------------------
    print("\n[STEP 5/5] Menyimpan laporan training...")
    total_time = tfidf_time + svd_time

    training_report = {
        "model_name": "Matchra LSA Recommender",
        "algorithm": "TF-IDF Vectorization + Truncated SVD (Latent Semantic Analysis)",
        "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset": {
            "total_games": total_games,
            "source": "Steam + RAWG (merged)"
        },
        "tfidf_config": {
            "max_features": 15000,
            "ngram_range": "1-2 (unigram + bigram)",
            "sublinear_tf": True,
            "vocabulary_size": vocab_size
        },
        "svd_config": {
            "n_components": N_COMPONENTS,
            "n_iter": 7,
            "random_state": 42
        },
        "training_results": {
            "tfidf_time_seconds": round(tfidf_time, 3),
            "svd_time_seconds": round(svd_time, 3),
            "total_training_time_seconds": round(total_time, 3),
            "explained_variance_pct": round(explained_variance, 2),
            "top5_components_variance_pct": [round(v*100, 4) for v in variance_per_component[:5]],
            "all_components_variance_pct": [round(v*100, 4) for v in variance_per_component]
        },
        "model_files": {
            "vectorizer": vectorizer_path,
            "svd_pipeline": svd_path,
            "lsa_matrix": lsa_matrix_path
        }
    }

    report_path = os.path.join(MODEL_DIR, "training_report.json")
    with open(report_path, "w") as f:
        json.dump(training_report, f, indent=2)

    print(f"   OK - training_report.json tersimpan")

    print("\n" + "=" * 60)
    print("TRAINING SELESAI!")
    print(f"   - {total_games:,} game dipelajari")
    print(f"   - {vocab_size:,} kata unik dikenali")
    print(f"   - {N_COMPONENTS} konsep laten ditemukan oleh SVD")
    print(f"   - {explained_variance:.1f}% variance data berhasil dijelaskan")
    print(f"   - Total waktu training: {total_time:.2f} detik")
    print("=" * 60)
    print("\nServer siap dijalankan: python app.py")

if __name__ == "__main__":
    train_and_export_model()
