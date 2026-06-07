from flask import Flask, render_template, request, jsonify
from recommender import MatchraRecommender

app = Flask(__name__)

print("Memuat Model ML Matchra...")
recommender = MatchraRecommender()
recommender.load_data()
print("Model siap digunakan!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/time_budget', methods=['POST'])
def api_time_budget():
    data = request.json
    time_hours = float(data.get('time_hours', 2.0))
    budget_idr = int(data.get('budget', 500000))
    platform = data.get('platform', 'windows')
    genres = data.get('genres', '')
    
    results_df = recommender.get_time_budget_recommendations(time_hours, budget_idr, platform, genres)
    
    games = []
    for _, row in results_df.iterrows():
        games.append({
            'name': row['name'],
            'header_image': str(row.get('header_image', '')),
            'metacritic': int(row.get('metacritic', 0)),
            'price_formatted': row['price_formatted'],
            'playtime_hours': row['playtime_hours'],
            'match_score': int(row['match_score'] * 100),
            'explanation': row['explanation']
        })
    return jsonify({"status": "success", "data": games})

@app.route('/api/onboarding', methods=['POST'])
def api_onboarding():
    data = request.json
    experience = data.get('experience', 'cerita')
    platform = data.get('platform', 'windows')
    
    results_df = recommender.get_onboarding_recommendations(experience, platform)
    
    games = []
    for _, row in results_df.iterrows():
        games.append({
            'name': row['name'],
            'header_image': str(row.get('header_image', '')),
            'metacritic': int(row.get('metacritic', 0)),
            'price_formatted': row['price_formatted'],
            'playtime_hours': row['playtime_hours'],
            'match_score': int(row['match_score'] * 100),
            'explanation': row['explanation']
        })
    return jsonify({"status": "success", "data": games})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
