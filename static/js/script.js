function switchTab(tabId) {
    document.querySelectorAll('.menu-item').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');

    const title = document.getElementById('page-title');
    const desc = document.getElementById('page-desc');

    if(tabId === 'time-budget') {
        title.innerText = 'Time & Budget Recommender';
        desc.innerText = 'Temukan game sempurna yang sesuai dengan waktu luang dan dompetmu.';
        document.getElementById('time-budget-form').style.display = 'flex';
        document.getElementById('onboarding-form').style.display = 'none';
    } else {
        title.innerText = 'First-Time Gamer Onboarding';
        desc.innerText = 'Pemula? Mari temukan game pertamamu berdasarkan pengalaman yang kamu cari.';
        document.getElementById('time-budget-form').style.display = 'none';
        document.getElementById('onboarding-form').style.display = 'flex';
    }

    document.getElementById('results-container').innerHTML = '';
}

function createGameCard(game, delay) {
    const accentColor = game.match_score > 80 ? 'var(--primary)' : 'var(--accent)';
    
    // Tampilkan logo Metacritic jika ada skornya dari RAWG
    const metacriticBadge = game.metacritic > 0 
        ? `<span class="meta-tag meta-mc">MC ${game.metacritic}</span>` 
        : '';
        
    // Gambar Cover
    const imageUrl = game.header_image && game.header_image !== 'nan' 
        ? game.header_image 
        : 'https://via.placeholder.com/460x215.png?text=No+Image';

    return `
    <div class="game-card" style="animation-delay: ${delay}s">
        <div class="game-cover">
            <img src="${imageUrl}" alt="${game.name}">
        </div>
        <div class="game-content-wrap">
            <div class="game-info">
                <h3>${game.name}</h3>
                <div class="game-meta">
                    <span class="meta-tag"><i class="ph ph-tag"></i> ${game.price_formatted}</span>
                    <span class="meta-tag"><i class="ph ph-clock"></i> ${game.playtime_hours} Jam</span>
                    ${metacriticBadge}
                </div>
                <p class="game-explainer">
                    <strong>💡 Alasan AI:</strong><br>
                    ${game.explanation}
                </p>
            </div>
            <div class="score-circle" style="border-color: ${accentColor}; color: ${accentColor}">
                ${game.match_score}%
            </div>
        </div>
    </div>
    `;
}

document.getElementById('time-budget-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    fetchRecommendations('/api/time_budget', {
        time_hours: document.getElementById('tb-time').value,
        budget: document.getElementById('tb-budget').value,
        platform: document.getElementById('tb-platform').value,
        genres: document.getElementById('tb-genres').value
    });
});

document.getElementById('onboarding-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const expRadio = document.querySelector('input[name="ob-exp"]:checked');
    fetchRecommendations('/api/onboarding', {
        experience: expRadio.value,
        platform: document.getElementById('ob-platform').value
    });
});

async function fetchRecommendations(url, payload) {
    const resultsContainer = document.getElementById('results-container');
    const loader = document.getElementById('loader');
    resultsContainer.innerHTML = '';
    loader.style.display = 'block';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const resData = await response.json();
        loader.style.display = 'none';
        
        if(resData.data.length === 0) {
            resultsContainer.innerHTML = '<p style="text-align:center; color: var(--text-muted)">Maaf, tidak ada game yang memenuhi kriteria.</p>';
            return;
        }

        resData.data.forEach((game, index) => {
            resultsContainer.innerHTML += createGameCard(game, index * 0.1);
        });
    } catch (err) {
        loader.style.display = 'none';
        resultsContainer.innerHTML = '<p style="color:red;">Terjadi kesalahan saat memuat rekomendasi.</p>';
        console.error(err);
    }
}
