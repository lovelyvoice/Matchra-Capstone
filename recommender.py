import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import joblib
import json

class MatchraRecommender:
    def __init__(self,
                 data_path="data/processed/clean_matchra_dataset.csv",
                 vectorizer_path="data/model/matchra_vectorizer.pkl",
                 svd_path="data/model/matchra_svd.pkl",
                 lsa_matrix_path="data/model/matchra_lsa_matrix.pkl",
                 report_path="data/model/training_report.json"):
        self.data_path = data_path
        self.vectorizer_path = vectorizer_path
        self.svd_path = svd_path
        self.lsa_matrix_path = lsa_matrix_path
        self.report_path = report_path

        self.df = None
        self.lsa_matrix = None
        self.vectorizer = None
        self.svd_pipeline = None
        self.training_report = None
        self.is_loaded = False

    def load_data(self):
        """Memuat dataset dan MODEL FISIK (.pkl) hasil training LSA/SVD"""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError("Dataset tidak ditemukan. Jalankan data_preprocessing.py.")

        required_models = [self.vectorizer_path, self.svd_path, self.lsa_matrix_path]
        missing = [p for p in required_models if not os.path.exists(p)]
        if missing:
            raise FileNotFoundError(
                f"File model tidak ditemukan: {missing}\n"
                "Harap jalankan: python train_model.py"
            )

        self.df = pd.read_csv(self.data_path)
        self.df['platforms'] = self.df['platforms'].fillna('')
        self.df['playtime_hours'] = self.df['playtime_hours'].fillna(0)
        self.df['all_tags'] = self.df['all_tags'].fillna('')
        self.df['metacritic'] = self.df['metacritic'].fillna(0)

        print("Memuat model LSA (Vectorizer + SVD Pipeline + LSA Matrix)...")
        self.vectorizer = joblib.load(self.vectorizer_path)
        self.svd_pipeline = joblib.load(self.svd_path)
        self.lsa_matrix = joblib.load(self.lsa_matrix_path)

        if os.path.exists(self.report_path):
            with open(self.report_path, 'r') as f:
                self.training_report = json.load(f)

        self.is_loaded = True
        print("✅ Model LSA berhasil dimuat ke memori!")

    def _calculate_similarity(self, input_text):
        """
        Menghitung cosine similarity di ruang LSA (laten semantik).
        Model TIDAK sekedar mencocokkan kata — ia memahami KONSEP
        berdasarkan pola yang dipelajari saat training (SVD).
        """
        tfidf_vec = self.vectorizer.transform([input_text])
        # Proyeksikan query ke ruang laten yang dipelajari saat training
        lsa_vec = self.svd_pipeline.transform(tfidf_vec)
        # Hitung cosine similarity di ruang laten
        cosine_sim = cosine_similarity(lsa_vec, self.lsa_matrix).flatten()
        cosine_sim = np.clip(cosine_sim * 3.5, 0, 0.99)
        return cosine_sim

    def _calculate_score_breakdown(self, game_row, budget_idr, time_hours_per_day,
                                    preferred_genres, context="budget_time"):
        """
        Hitung breakdown 4 faktor penyumbang skor rekomendasi (untuk XAI).
        Setiap faktor dinormalisasi ke 0–100.
        """
        # 1. Genre Relevance — berdasarkan cosine similarity laten
        genre_score = round(float(game_row['match_score']) * 100, 1)

        # 2. Budget Score — seberapa "murah" game relatif terhadap budget user
        if context == "budget_time":
            price = game_row.get('price_idr', 0)
            if price == 0:
                budget_score = 100.0
            elif budget_idr > 0:
                budget_score = round(max(0, (1 - price / budget_idr) * 100), 1)
                budget_score = min(budget_score, 100.0)
            else:
                budget_score = 50.0
        else:
            budget_score = 80.0  # onboarding tidak filter budget ketat

        # 3. Playtime Score — seberapa "pas" durasi game dengan waktu user
        playtime = game_row.get('playtime_hours', 0)
        if context == "budget_time":
            max_time = time_hours_per_day * 7
            if playtime == 0:
                playtime_score = 75.0
            elif max_time > 0:
                ratio = playtime / max_time
                if ratio <= 1.0:
                    playtime_score = round((1 - abs(ratio - 0.7)) * 100, 1)
                else:
                    playtime_score = max(0, round((1 - (ratio - 1)) * 50, 1))
                playtime_score = min(max(playtime_score, 0), 100)
            else:
                playtime_score = 50.0
        else:
            playtime_score = 75.0

        # 4. Quality Score — berdasarkan metacritic + positive ratings
        metacritic = game_row.get('metacritic', 0)
        pos_ratings = game_row.get('positive_ratings', 0)
        mc_score = min(metacritic, 100) if metacritic > 0 else 50
        rating_score = min(np.log1p(pos_ratings) / np.log1p(500000) * 100, 100)
        quality_score = round((mc_score * 0.5 + rating_score * 0.5), 1)

        return {
            "genre_relevance": float(genre_score),
            "budget_fit":      float(budget_score),
            "playtime_fit":    float(playtime_score),
            "quality_score":   float(quality_score)
        }

    def _extract_matched_tags(self, game_row, user_input):
        """Ekstrak tag game yang cocok dengan input user (untuk XAI chips)."""
        tags_raw = str(game_row.get('all_tags', ''))
        tag_list = [t.strip() for t in tags_raw.split(',') if t.strip()]
        user_words = [w.strip().lower() for w in user_input.replace(',', ' ').split() if len(w.strip()) > 2]
        matched = [t for t in tag_list if any(uw in t.lower() for uw in user_words)]
        return list(dict.fromkeys(matched))[:6]  # max 6 tag unik

    def generate_explanation(self, game_row, context="budget_time", user_input="",
                              budget_idr=500000, time_hours_per_day=2):
        judul = game_row['name']
        match_score = int(game_row['match_score'] * 100)
        harga = game_row['price_formatted']
        waktu = game_row['playtime_hours']
        pos_ratings = int(game_row.get('positive_ratings', 0))

        matched_tags = self._extract_matched_tags(game_row, user_input)
        score_breakdown = self._calculate_score_breakdown(
            game_row, budget_idr, time_hours_per_day, user_input, context
        )

        if matched_tags:
            tag_text = f" Cocok karena elemen [{', '.join(matched_tags[:3])}] terdeteksi kuat dalam profil game ini."
        else:
            tag_text = ""

        if context == "budget_time":
            harga_text = ("game ini GRATIS!" if game_row.get('price_idr', 1) == 0
                          else f"harga {harga} sangat aman di budgetmu.")
            waktu_text = ("Durasi bebas" if waktu == 0
                          else f"Durasinya ~{waktu} jam")
            explanation = (f"Match Score {match_score}% — {waktu_text}, {harga_text}"
                           f"{tag_text}")
        elif context == "onboarding":
            explanation = (f"Match Score {match_score}% — Mahakarya dengan "
                           f"{pos_ratings:,} ulasan positif. Sangat ramah pemula.{tag_text}")
        else:
            explanation = f"Match Score {match_score}%.{tag_text}"

        return {
            "text": explanation,
            "score_breakdown": score_breakdown,
            "matched_tags": matched_tags
        }

    def get_model_info(self):
        """Mengembalikan informasi model untuk ditampilkan di UI."""
        if self.training_report:
            return {
                "status": "trained",
                "algorithm": self.training_report.get("algorithm", "TF-IDF + SVD (LSA)"),
                "total_games": self.training_report["dataset"]["total_games"],
                "vocabulary_size": self.training_report["tfidf_config"]["vocabulary_size"],
                "latent_components": self.training_report["svd_config"]["n_components"],
                "explained_variance_pct": self.training_report["training_results"]["explained_variance_pct"],
                "training_date": self.training_report.get("training_date", "N/A"),
                "total_training_time_seconds": self.training_report["training_results"]["total_training_time_seconds"],
                "top5_variance": self.training_report["training_results"].get("top5_components_variance_pct", [])
            }
        else:
            # Fallback jika training_report belum ada
            return {
                "status": "loaded",
                "algorithm": "TF-IDF + SVD (LSA)",
                "total_games": len(self.df) if self.df is not None else 0,
                "vocabulary_size": len(self.vectorizer.vocabulary_) if self.vectorizer else 0,
                "latent_components": 150,
                "explained_variance_pct": 0,
                "training_date": "N/A",
                "total_training_time_seconds": 0,
                "top5_variance": []
            }

    def get_time_budget_recommendations(self, time_hours_per_day, budget_idr, platform_choice,
                                         preferred_genres, min_metacritic=0,
                                         multiplayer_pref="both", top_n=5):
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

        # Filter Metacritic score minimum
        if min_metacritic > 0:
            df_rec = df_rec[
                (df_rec['metacritic'] >= min_metacritic) | (df_rec['metacritic'] == 0)
            ]

        # Filter multiplayer preference berdasarkan tags
        if multiplayer_pref == "multiplayer":
            df_rec = df_rec[df_rec['all_tags'].str.lower().str.contains('multi', na=False)]
        elif multiplayer_pref == "singleplayer":
            df_rec = df_rec[df_rec['all_tags'].str.lower().str.contains('single', na=False)]

        df_rec = df_rec.sort_values(by=['match_score', 'positive_ratings'], ascending=[False, False])
        top_games = df_rec.head(top_n).copy()

        results = []
        for _, row in top_games.iterrows():
            expl = self.generate_explanation(
                row, "budget_time", preferred_genres, budget_idr, time_hours_per_day
            )
            results.append({
                'name': row['name'],
                'header_image': str(row.get('header_image', '')),
                'metacritic': int(row.get('metacritic', 0)),
                'price_formatted': row['price_formatted'],
                'playtime_hours': row['playtime_hours'],
                'positive_ratings': int(row.get('positive_ratings', 0)),
                'all_tags': str(row.get('all_tags', '')),
                'match_score': int(row['match_score'] * 100),
                'explanation': expl['text'],
                'score_breakdown': expl['score_breakdown'],
                'matched_tags': expl['matched_tags']
            })
        return results

    def get_onboarding_recommendations(self, experience_type, platform_choice,
                                        intensity="medium", top_n=5):
        if not self.is_loaded:
            self.load_data()

        experience_map = {
            'cerita': 'Story Rich RPG Adventure Great Soundtrack Deep Story Narrative',
            'aksi':   'Action Fast-paced Shooter Fighting Beat em up Combat',
            'puzzle': 'Puzzle Logic Strategy Brain Point Click Mystery',
            'santai': 'Casual Relaxing Family Friendly Simulation Cozy Atmospheric'
        }
        intensity_map = {
            'light':  {'max_playtime': 20,  'min_ratings': 5000},
            'medium': {'max_playtime': 60,  'min_ratings': 10000},
            'heavy':  {'max_playtime': 999, 'min_ratings': 20000},
        }

        experience_type = experience_type.lower()
        search_tags = experience_map.get(experience_type, experience_type)
        intensity_cfg = intensity_map.get(intensity, intensity_map['medium'])

        similarity_scores = self._calculate_similarity(search_tags)

        df_rec = self.df.copy()
        df_rec['match_score'] = similarity_scores

        platform_choice = platform_choice.lower()
        df_rec = df_rec[df_rec['platforms'].str.lower().str.contains(platform_choice)]
        df_rec = df_rec[df_rec['positive_ratings'] > intensity_cfg['min_ratings']]
        if intensity != 'heavy':
            df_rec = df_rec[
                (df_rec['playtime_hours'] <= intensity_cfg['max_playtime']) |
                (df_rec['playtime_hours'] == 0)
            ]

        df_rec = df_rec.sort_values(by=['match_score', 'positive_ratings'], ascending=[False, False])
        top_games = df_rec.head(top_n).copy()

        results = []
        for _, row in top_games.iterrows():
            expl = self.generate_explanation(row, "onboarding", search_tags)
            results.append({
                'name': row['name'],
                'header_image': str(row.get('header_image', '')),
                'metacritic': int(row.get('metacritic', 0)),
                'price_formatted': row['price_formatted'],
                'playtime_hours': row['playtime_hours'],
                'positive_ratings': int(row.get('positive_ratings', 0)),
                'all_tags': str(row.get('all_tags', '')),
                'match_score': int(row['match_score'] * 100),
                'explanation': expl['text'],
                'score_breakdown': expl['score_breakdown'],
                'matched_tags': expl['matched_tags']
            })
        return results

    def get_showcase_games(self, n=16):
        """Mengambil n game acak yang memiliki header_image valid untuk keperluan showcase (marquee)."""
        if not self.is_loaded:
            self.load_data()
            
        # Filter game dengan gambar valid
        df_valid = self.df[self.df['header_image'].notna() & (self.df['header_image'] != 'nan') & (self.df['header_image'] != '')]
        
        # Ambil acak
        if len(df_valid) >= n:
            df_sample = df_valid.sample(n)
        else:
            df_sample = df_valid
            
        results = []
        for _, row in df_sample.iterrows():
            tags = str(row.get('all_tags', '')).split(',')
            main_genre = tags[0].strip() if tags and len(tags[0].strip()) > 0 else "Game"
            results.append({
                'name': row['name'],
                'header_image': row['header_image'],
                'genre': f"Genre · {main_genre}"
            })
        return results

# ==== BLOK PENGUJIAN ====
if __name__ == '__main__':
    recommender = MatchraRecommender()
    print("Testing Load Data...")
    recommender.load_data()
    print("Model Info:", recommender.get_model_info())
    print("Success!")
