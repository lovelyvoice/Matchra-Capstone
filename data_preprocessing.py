import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Path
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
EDA_DIR = "data/eda"

def clean_html(raw_html):
    if pd.isna(raw_html):
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    cleantext = re.sub(r'\s+', ' ', cleantext).strip()
    return cleantext

def perform_eda(df):
    """Fungsi untuk membuat grafik EDA dan menyimpannya"""
    print("\n📊 Memulai Exploratory Data Analysis (EDA)...")
    if not os.path.exists(EDA_DIR):
        os.makedirs(EDA_DIR)
        
    # Set style seaborn
    sns.set_theme(style="darkgrid")
    
    # 1. Distribusi Harga (Hanya yang berbayar)
    plt.figure(figsize=(10, 6))
    df_paid = df[df['price_idr'] > 0]
    sns.histplot(df_paid['price_idr'], bins=50, kde=True, color='purple')
    plt.title('Distribusi Harga Game (Berbayar)')
    plt.xlabel('Harga (Rupiah)')
    plt.ylabel('Jumlah Game')
    plt.xlim(0, 1000000) # Batasi X-axis ke Rp 1 Juta agar grafik rapi
    plt.savefig(os.path.join(EDA_DIR, 'price_distribution.png'))
    plt.close()
    
    # 2. Distribusi Waktu Main
    plt.figure(figsize=(10, 6))
    df_playtime = df[(df['playtime_hours'] > 0) & (df['playtime_hours'] < 100)]
    sns.histplot(df_playtime['playtime_hours'], bins=40, kde=True, color='cyan')
    plt.title('Distribusi Waktu Main Rata-Rata (< 100 Jam)')
    plt.xlabel('Waktu Main (Jam)')
    plt.ylabel('Jumlah Game')
    plt.savefig(os.path.join(EDA_DIR, 'playtime_distribution.png'))
    plt.close()
    
    # 3. Top 10 Genre Populer
    plt.figure(figsize=(12, 6))
    # Pecah string tag menjadi list of tags
    all_genres = df['all_tags'].str.split(', ').explode()
    top_genres = all_genres.value_counts().head(10)
    
    sns.barplot(x=top_genres.values, y=top_genres.index, hue=top_genres.index, legend=False, palette='viridis')
    plt.title('Top 10 Genre Paling Populer di Dataset')
    plt.xlabel('Jumlah Game')
    plt.ylabel('Genre / Tag')
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'top_genres.png'))
    plt.close()
    
    print(f"✅ Grafik EDA berhasil disimpan di folder '{EDA_DIR}'")

def preprocess_data():
    print("⏳ Memulai Preprocessing Data (Integrasi Steam + RAWG)...")
    
    # 1. Membaca Data STEAM
    steam_path = os.path.join(RAW_DIR, "steam.csv")
    desc_path = os.path.join(RAW_DIR, "steam_description_data.csv")
    rawg_path = os.path.join(RAW_DIR, "game_info.csv") 
    media_path = os.path.join(RAW_DIR, "steam_media_data.csv") 
    
    df_steam = pd.read_csv(steam_path)
    df_desc = pd.read_csv(desc_path)
    df_media = pd.read_csv(media_path)
    
    # 2. Membaca Data RAWG
    try:
        df_rawg = pd.read_csv(rawg_path, usecols=['name', 'metacritic', 'rating'])
        df_rawg = df_rawg.drop_duplicates(subset=['name'], keep='first')
    except Exception as e:
        df_rawg = pd.DataFrame(columns=['name', 'metacritic', 'rating'])
    
    # 3. Penggabungan Data (Merge)
    df = pd.merge(df_steam, df_desc, left_on='appid', right_on='steam_appid', how='inner')
    df = pd.merge(df, df_media[['steam_appid', 'header_image']], on='steam_appid', how='left')
    
    df['name_lower'] = df['name'].str.lower()
    df_rawg['name_lower'] = df_rawg['name'].str.lower()
    df = pd.merge(df, df_rawg[['name_lower', 'metacritic', 'rating']], on='name_lower', how='left')
    
    df['metacritic'] = df['metacritic'].fillna(0)
    df.rename(columns={'rating': 'rawg_rating'}, inplace=True)
    df['rawg_rating'] = df['rawg_rating'].fillna(0)
    
    # 4. Data Cleaning (Filtering)
    df = df[df['english'] == 1].copy()
    df = df[df['positive_ratings'] > 200].copy()
    
    # 5. Feature Engineering
    KURS_RUPIAH = 20000
    df['price_idr'] = df['price'] * KURS_RUPIAH
    df['price_formatted'] = df['price_idr'].apply(lambda x: f"Rp {int(x):,}".replace(',', '.') if x > 0 else "Gratis")
    df['playtime_hours'] = (df['average_playtime'] / 60).round(1)
    
    df['genres'] = df['genres'].fillna('')
    df['categories'] = df['categories'].fillna('')
    df['steamspy_tags'] = df['steamspy_tags'].fillna('')
    
    df['all_tags'] = df['genres'].str.replace(';', ', ') + ", " + \
                     df['categories'].str.replace(';', ', ') + ", " + \
                     df['steamspy_tags'].str.replace(';', ', ')
                     
    df['all_tags'] = df['all_tags'].apply(lambda x: ", ".join(sorted(set([t.strip() for t in x.split(',') if t.strip()]))))
    df['clean_description'] = df['about_the_game'].apply(clean_html)
    df['soup'] = df['all_tags'] + " " + df['clean_description']
    
    # 6. Export Data Bersih
    cols_to_keep = [
        'appid', 'name', 'developer', 'platforms', 'header_image',
        'price_idr', 'price_formatted', 'playtime_hours', 
        'positive_ratings', 'metacritic', 'rawg_rating', 'all_tags', 'soup'
    ]
    df_clean = df[cols_to_keep]
    
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
        
    output_path = os.path.join(PROCESSED_DIR, "clean_matchra_dataset.csv")
    df_clean.to_csv(output_path, index=False)
    
    print("✅ PREPROCESSING SELESAI (Steam + RAWG Terintegrasi)!")
    
    # 7. Jalankan EDA di akhir
    perform_eda(df_clean)

if __name__ == "__main__":
    preprocess_data()
