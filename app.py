from flask import Flask, render_template, request, jsonify
from recommender import MatchraRecommender

app = Flask(__name__)

print("Memuat Model ML Matchra (TF-IDF + LSA/SVD)...")
recommender = MatchraRecommender()
recommender.load_data()
print("Model siap digunakan!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/model_info', methods=['GET'])
def api_model_info():
    """Endpoint untuk menampilkan informasi model di UI (XAI transparency)."""
    info = recommender.get_model_info()
    return jsonify({"status": "success", "data": info})

@app.route('/api/time_budget', methods=['POST'])
def api_time_budget():
    data = request.json
    time_hours     = float(data.get('time_hours', 2.0))
    budget_idr     = int(data.get('budget', 500000))
    platform       = data.get('platform', 'windows')
    genres         = data.get('genres', '')
    min_metacritic = int(data.get('min_metacritic', 0))
    multiplayer    = data.get('multiplayer', 'both')

    results = recommender.get_time_budget_recommendations(
        time_hours, budget_idr, platform, genres,
        min_metacritic=min_metacritic,
        multiplayer_pref=multiplayer
    )
    return jsonify({"status": "success", "data": results})

@app.route('/api/onboarding', methods=['POST'])
def api_onboarding():
    data       = request.json
    experience = data.get('experience', 'cerita')
    platform   = data.get('platform', 'windows')
    intensity  = data.get('intensity', 'medium')

    results = recommender.get_onboarding_recommendations(
        experience, platform, intensity=intensity
    )
    return jsonify({"status": "success", "data": results})

@app.route('/api/showcase_games', methods=['GET'])
def api_showcase_games():
    """Endpoint untuk mengambil data game dinamis untuk conveyor/marquee di landing page."""
    n = request.args.get('n', 16, type=int)
    results = recommender.get_showcase_games(n=n)
    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
