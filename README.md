# Matchra - AI Game Recommendation System

Matchra adalah sistem rekomendasi game cerdas yang dirancang untuk mengatasi masalah kebingungan memilih game akibat waktu luang yang terbatas dan *backlog* game yang menumpuk. Proyek ini dibangun sebagai bagian dari Capstone Project PJK-GM094 (AI for Smart Recommendation Systems).

## 🚀 Fitur Utama
1. **Time & Budget Recommender:** Mencari game ideal berdasarkan waktu luang mingguan, sisa budget (dompet), dan genre favorit.
2. **First-Time Gamer Onboarding:** Panduan khusus pemula untuk mencari game pertama berdasarkan tipe pengalaman (Cerita, Aksi, Puzzle, Santai).
3. **Explainable AI (XAI):** Setiap game yang direkomendasikan memiliki alasan logis dan terpersonalisasi.

## 🛠️ Arsitektur Teknologi
- **Algoritma Machine Learning:** Content-Based Filtering (TF-IDF Vectorizer & Cosine Similarity)
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS (Glassmorphism), Vanilla JS
- **Dataset:** Integrasi Steam Store Games & RAWG Video Games Database

## 💻 Cara Menjalankan Proyek (Setup)

**1. Instalasi Dependensi**
Pastikan Python sudah terinstal, lalu jalankan:
```bash
pip install -r requirements.txt
```

**2. Unduh Dataset**
(Pastikan Anda sudah mengatur Kaggle API Token `kaggle.json` di komputer Anda).
```bash
python download_dataset.py
```

**3. Preprocessing & Exploratory Data Analysis (EDA)**
Skrip ini akan menggabungkan dataset Steam dan RAWG, membersihkan data, dan mengekspor grafik visualisasi ke folder `data/eda/`.
```bash
python data_preprocessing.py
```

**4. Latih Model AI (Export ke .pkl)**
Skrip ini akan membangun matriks kecerdasan TF-IDF dan mengekspor model fisiknya ke folder `data/model/` agar mempercepat proses server.
```bash
python train_model.py
```

**5. Jalankan Web Server**
```bash
python app.py
```
Akses aplikasi melalui browser pada alamat: **http://127.0.0.1:5000**
