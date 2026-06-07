import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import joblib

class MatchraRecommender:
    def __init__(self, 
                 data_path="data/processed/clean_matchra_dataset.csv",
                 vectorizer_path="data/model/matchra_vectorizer.pkl",
                 matrix_path="data/model/matchra_matrix.pkl"):
        self.data_path = data_path
        self.vectorizer_path = vectorizer_path
        self.matrix_path = matrix_path
        
        self.df = None
        self.tfidf_matrix = None
        self.vectorizer = None
        self.is_loaded = False
        
    def load_data(self):
        """Memuat dataset dan MODEL FISIK (.pkl) yang sudah dilatih"""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError("Dataset tidak ditemukan. Jalankan preprocessing.")
            
        if not os.path.exists(self.vectorizer_path) or not os.path.exists(self.matrix_path):
            raise FileNotFoundError("File Model (.pkl) tidak ditemukan! Harap jalankan 'python train_model.py' terlebih dahulu.")
            
        self.df = pd.read_csv(self.data_path)
        self.df['platforms'] = self.df['platforms'].fillna('')
        self.df['playtime_hours'] = self.df['playtime_hours'].fillna(0)
        
        print("Memuat file model (Vectorizer & Matrix)...")
        self.vectorizer = joblib.load(self.vectorizer_path)
        self.tfidf_matrix = joblib.load(self.matrix_path)
        
        self.is_loaded = True
        print("✅ Model Fisik berhasil dimuat ke memori!")

    def _calculate_similarity(self, input_text):
        """Menghitung cosine similarity antara input user dan dataset"""
        user_vector = self.vectorizer.transform([input_text])
        cosine_sim = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        
        # Normalisasi Skor (UX Scaling)
        cosine_sim = np.clip(cosine_sim * 3.5, 0, 0.99)
        return cosine_sim

    def generate_explanation(self, game_row, context="budget_time", user_input=""):
        judul = game_row['name']
        match_score = int(game_row['match_score'] * 100)
        harga = game_row['price_formatted']
        waktu = game_row['playtime_hours']
        tags = str(game_row.get('all_tags', '')).lower()
        
        # Ekstrak alasan keyword (XAI)
        matched_keywords = []
        if user_input:
            user_words = [w.strip().lower() for w in user_input.replace(',', ' ').split()]
            for w in user_words:
                if len(w) > 2 and w in tags:
                    matched_keywords.append(w.capitalize())
        
        # Buat teks keyword dinamis
        keyword_text = ""
        if matched_keywords:
            top_keywords = list(set(matched_keywords))[:3]
            keyword_text = f" AI kami mendeteksi elemen kuat pada [{', '.join(top_keywords)}] yang sangat relevan dengan pencarianmu."
        
        if context == "budget_time":
            harga_text = "karena game ini sepenuhnya GRATIS!" if game_row.get('price_idr', 1) == 0 else f"harganya ({harga}) sangat aman di budgetmu."
            waktu_text = "Bisa dimainkan santai tanpa target tamat" if waktu == 0 else f"Durasinya ({waktu} jam) sangat pas diselesaikan dalam seminggu"
            return f"Tingkat Kecocokan: {match_score}%. '{judul}' adalah pilihan cerdas! {waktu_text}, dan {harga_text}{keyword_text}"
            
        elif context == "onboarding":
            return f"Tingkat Kecocokan: {match_score}%. '{judul}' adalah mahakarya dengan {game_row['positive_ratings']:,} ulasan positif. Ini langkah pertama yang luar biasa karena sangat ramah pemula.{keyword_text}"
        return ""

    def get_time_budget_recommendations(self, time_hours_per_day, budget_idr, platform_choice, preferred_genres, top_n=5):
        if not self.is_loaded:
            self.load_data()
            
        max_playtime_target = time_hours_per_day * 7
        similarity_scores = self._calculate_similarity(preferred_genres)
        
        df_rec = self.df.copy()
        df_rec['match_score'] = similarity_scores
        
        platform_choice = platform_choice.lower()
        df_rec = df_rec[
            (df_rec['price_idr'] <= budget_idr) & 
            (df_rec['platforms'].str.lower().str.contains(platform_choice))
        ]
        
        df_rec = df_rec[
            (df_rec['playtime_hours'] <= max_playtime_target) | 
            (df_rec['playtime_hours'] == 0)
        ]
        
        df_rec = df_rec.sort_values(by=['match_score', 'positive_ratings'], ascending=[False, False])
        top_games = df_rec.head(top_n).copy()
        top_games['explanation'] = top_games.apply(lambda row: self.generate_explanation(row, "budget_time", preferred_genres), axis=1)
        
        return top_games

    def get_onboarding_recommendations(self, experience_type, platform_choice, top_n=5):
        if not self.is_loaded:
            self.load_data()
            
        experience_map = {
            'cerita': 'Story Rich, RPG, Adventure, Great Soundtrack, Deep Story',
            'aksi': 'Action, Fast-paced, Shooter, Fighting, Beat em up',
            'puzzle': 'Puzzle, Logic, Strategy, Brain, Point & Click',
            'santai': 'Casual, Relaxing, Family Friendly, Simulation, Cozy'
        }
        
        experience_type = experience_type.lower()
        search_tags = experience_map.get(experience_type, experience_type) 
        
        similarity_scores = self._calculate_similarity(search_tags)
        
        df_rec = self.df.copy()
        df_rec['match_score'] = similarity_scores
        
        platform_choice = platform_choice.lower()
        df_rec = df_rec[df_rec['platforms'].str.lower().str.contains(platform_choice)]
        df_rec = df_rec[df_rec['positive_ratings'] > 10000]
        
        df_rec = df_rec.sort_values(by=['match_score', 'positive_ratings'], ascending=[False, False])
        top_games = df_rec.head(top_n).copy()
        top_games['explanation'] = top_games.apply(lambda row: self.generate_explanation(row, "onboarding", search_tags), axis=1)
        
        return top_games

# ==== BLOK PENGUJIAN ====
if __name__ == '__main__':
    recommender = MatchraRecommender()
    print("Testing Load Data...")
    recommender.load_data()
    print("Success!")
