/* ============================================================
   Matchra — Frontend Logic
   Handles: tab switching, form submission, card rendering,
            XAI bars, score ring animation, model info widget
============================================================ */

// ── Tab Switch ────────────────────────────────────────────
function goHome() {
    // Aktifkan mode Landing Page (menyembunyikan sidebar via CSS)
    document.querySelector('.app-container').classList.add('is-landing');
    
    // Tampilkan About Section, sembunyikan elemen App
    document.getElementById('about-section').style.display = 'flex';
    document.querySelector('.input-card').style.display = 'none';
    document.querySelector('.header').style.display = 'none';
    
    // Reset status aktif menu
    document.getElementById('btn-tab-tb').classList.remove('active');
    document.getElementById('btn-tab-ob').classList.remove('active');
    document.getElementById('btn-tab-home').classList.add('active');
    
    clearResults();
}

function switchTab(tabId) {
    // Matikan mode Landing Page (memunculkan sidebar & app UI)
    document.querySelector('.app-container').classList.remove('is-landing');
    document.querySelector('.header').style.display = 'block';
    document.getElementById('about-section').style.display = 'none';
    document.querySelector('.input-card').style.display = 'block';

    // Update sidebar buttons
    document.getElementById('btn-tab-home').classList.remove('active');
    document.getElementById('btn-tab-tb').classList.toggle('active', tabId === 'time-budget');
    document.getElementById('btn-tab-ob').classList.toggle('active', tabId === 'onboarding');

    const titles = {
        'time-budget': {
            eyebrow: 'TF-IDF + Latent Semantic Analysis',
            title:   'Time &amp; Budget Recommender',
            desc:    'Temukan game sempurna yang sesuai dengan waktu luang dan dompetmu.'
        },
        'onboarding': {
            eyebrow: 'Cosine Similarity · LSA Vector Space',
            title:   'First-Time Gamer Guide',
            desc:    'Pemula? Temukan game pertamamu berdasarkan pengalaman yang kamu inginkan.'
        }
    };

    if (titles[tabId]) {
        const t = titles[tabId];
        document.getElementById('eyebrow-text').innerHTML  = t.eyebrow;
        document.getElementById('page-title').innerHTML    = t.title;
        document.getElementById('page-desc').innerText     = t.desc;
    }

    document.getElementById('time-budget-form').classList.toggle('active', tabId === 'time-budget');
    document.getElementById('onboarding-form').classList.toggle('active', tabId === 'onboarding');
    
    clearResults();
}

function goToGame(gameName) {
    switchTab('time-budget');
    document.getElementById('tb-genres').value = gameName;
}

// ── Slider label helpers ──────────────────────────────────
function updateBudgetLabel(val) {
    const num = parseInt(val);
    const label = num === 0
        ? 'Gratis'
        : 'Rp ' + num.toLocaleString('id-ID');
    document.getElementById('budget-val').innerText = label;
}

function updateMetaLabel(val) {
    const num = parseInt(val);
    document.getElementById('meta-val').innerText = num === 0 ? 'Semua' : num + '+';
}

// ── Clear results ─────────────────────────────────────────
function clearResults() {
    document.getElementById('results-container').innerHTML = '';
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('loader').style.display = 'none';
}

// ── Score ring helper ─────────────────────────────────────
function buildScoreRing(score) {
    const circumference = 176; // 2π × r=28
    const offset = circumference - (score / 100) * circumference;
    const cls = score >= 75 ? 'high' : score >= 50 ? 'mid' : 'low';

    return `
    <div class="score-ring-wrap">
        <div class="score-ring">
            <svg viewBox="0 0 72 72">
                <circle class="ring-bg"   cx="36" cy="36" r="28"/>
                <circle class="ring-fill ${cls}"
                        cx="36" cy="36" r="28"
                        stroke-dasharray="${circumference}"
                        stroke-dashoffset="${circumference}"
                        data-offset="${offset}"/>
            </svg>
            <div class="score-text-wrap">
                <span class="score-num">${score}</span>
                <span class="score-pct">%</span>
            </div>
        </div>
        <span class="score-label">Match<br>Score</span>
    </div>`;
}

// ── XAI breakdown bars ────────────────────────────────────
const BAR_DEFS = [
    { key: 'genre_relevance', label: 'Relevansi Genre', color: 'high' },
    { key: 'budget_fit',      label: 'Kesesuaian Budget', color: 'mid'  },
    { key: 'playtime_fit',    label: 'Kesesuaian Durasi', color: 'mid'  },
    { key: 'quality_score',   label: 'Kualitas Game',     color: 'high' },
];

function buildXaiBars(breakdown) {
    const rows = BAR_DEFS.map(def => {
        const val = Math.round(breakdown[def.key] || 0);
        return `
        <div class="xai-bar-row">
            <span class="xai-bar-label">${def.label}</span>
            <div class="xai-bar-track">
                <div class="xai-bar-fill ${def.color}" data-width="${val}"></div>
            </div>
            <span class="xai-bar-val">${val}%</span>
        </div>`;
    }).join('');

    return `
    <div class="xai-section">
        <div class="xai-title">
            <i class="ph ph-chart-bar"></i> Faktor Penyumbang Rekomendasi
        </div>
        <div class="xai-bars">${rows}</div>
    </div>`;
}

// ── Matched tag chips ─────────────────────────────────────
function buildTagChips(tags) {
    if (!tags || tags.length === 0) return '';
    const chips = tags.slice(0, 5).map(t =>
        `<span class="tag-chip"><i class="ph ph-check-circle"></i>${t}</span>`
    ).join('');
    return `<div class="matched-tags">${chips}</div>`;
}

// ── Game Card Builder ─────────────────────────────────────
function createGameCard(game, index) {
    const imageUrl = (game.header_image && game.header_image !== 'nan')
        ? game.header_image
        : 'https://placehold.co/220x140/FFF0E4/007979?text=No+Image&font=montserrat';

    const mcBadge = game.metacritic > 0
        ? `<span class="meta-pill mc"><i class="ph ph-medal"></i>MC ${game.metacritic}</span>`
        : '';

    const ratingText = game.positive_ratings > 0
        ? game.positive_ratings.toLocaleString('id-ID') + ' ★'
        : '—';

    const animDelay = index * 0.08;

    return `
<div class="game-card" style="animation-delay:${animDelay}s">
    <div class="game-cover">
        <img src="${imageUrl}" alt="${escHtml(game.name)}" loading="lazy">
        <div class="cover-gradient"></div>
    </div>
    <div class="game-body">
        <div class="card-top">
            <div class="card-top-left">
                <div class="game-title">${escHtml(game.name)}</div>
                <div class="meta-pills">
                    <span class="meta-pill"><i class="ph ph-tag"></i>${escHtml(game.price_formatted)}</span>
                    <span class="meta-pill"><i class="ph ph-clock"></i>${game.playtime_hours > 0 ? game.playtime_hours + ' Jam' : 'Bebas'}</span>
                    <span class="meta-pill"><i class="ph ph-thumbs-up"></i>${ratingText}</span>
                    ${mcBadge}
                </div>
            </div>
            ${buildScoreRing(game.match_score)}
        </div>

        ${buildTagChips(game.matched_tags)}

        ${buildXaiBars(game.score_breakdown)}

        <div class="game-explanation">
            <strong>💡 Analisis AI:</strong> ${escHtml(game.explanation)}
        </div>
    </div>
</div>`;
}

// ── HTML Escape helper ────────────────────────────────────
function escHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// ── Animate bars & rings after DOM insert ─────────────────
function animateCards() {
    // Score rings
    document.querySelectorAll('.ring-fill').forEach(el => {
        const offset = el.getAttribute('data-offset');
        requestAnimationFrame(() => {
            el.style.strokeDashoffset = offset;
        });
    });
    // XAI bars
    document.querySelectorAll('.xai-bar-fill').forEach(el => {
        const w = el.getAttribute('data-width');
        requestAnimationFrame(() => {
            el.style.width = w + '%';
        });
    });
}

// ── Fetch & display recommendations ──────────────────────
async function fetchRecommendations(url, payload) {
    const container = document.getElementById('results-container');
    const loader    = document.getElementById('loader');
    const section   = document.getElementById('results-section');
    const countEl   = document.getElementById('results-count');

    container.innerHTML = '';
    section.style.display = 'none';
    loader.style.display  = 'flex';

    try {
        const res  = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        loader.style.display = 'none';

        const games = json.data || [];

        if (games.length === 0) {
            section.style.display = 'flex';
            container.innerHTML = `
            <div class="empty-state">
                <i class="ph ph-smiley-sad"></i>
                <p>Tidak ada game yang memenuhi kriteria.<br>Coba perluas filter pencarianmu.</p>
            </div>`;
            countEl.innerText = '0 game';
            return;
        }

        let html = '';
        games.forEach((g, i) => { html += createGameCard(g, i); });
        container.innerHTML = html;

        countEl.innerText = games.length + ' game';
        section.style.display = 'flex';

        // Trigger animations after paint
        requestAnimationFrame(() => setTimeout(animateCards, 50));

    } catch (err) {
        loader.style.display = 'none';
        section.style.display = 'flex';
        container.innerHTML = `
        <div class="empty-state">
            <i class="ph ph-warning-circle"></i>
            <p>Terjadi kesalahan saat memuat rekomendasi.<br>Pastikan server berjalan dengan benar.</p>
        </div>`;
        console.error('Fetch error:', err);
    }
}

// ── Form: Time & Budget ───────────────────────────────────
document.getElementById('time-budget-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const multiChecked = document.querySelector('input[name="tb-multi"]:checked');
    fetchRecommendations('/api/time_budget', {
        time_hours:     parseFloat(document.getElementById('tb-time').value),
        budget:         parseInt(document.getElementById('tb-budget').value),
        platform:       document.getElementById('tb-platform').value,
        genres:         document.getElementById('tb-genres').value.trim(),
        min_metacritic: parseInt(document.getElementById('tb-metacritic').value),
        multiplayer:    multiChecked ? multiChecked.value : 'both'
    });
});

// ── Form: Onboarding ─────────────────────────────────────
document.getElementById('onboarding-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const expChecked       = document.querySelector('input[name="ob-exp"]:checked');
    const intensityChecked = document.querySelector('input[name="ob-intensity"]:checked');
    fetchRecommendations('/api/onboarding', {
        experience: expChecked       ? expChecked.value       : 'cerita',
        platform:   document.getElementById('ob-platform').value,
        intensity:  intensityChecked ? intensityChecked.value : 'medium'
    });
});

// ── Fetch Showcase Games for Marquee ───────────────────────
async function fetchShowcaseGames() {
    const grid = document.getElementById('dynamic-marquee-grid');
    if (!grid) return;
    
    try {
        const res = await fetch('/api/showcase_games?n=12');
        const json = await res.json();
        const games = json.data || [];
        
        if (games.length === 0) return;
        
        let html = '';
        games.forEach(g => {
            html += `
            <div class="game-showcase-card modern-card" onclick="goToGame('${escHtml(g.name)}')">
                <div class="card-img-wrap">
                    <img src="${g.header_image}" alt="${escHtml(g.name)}" loading="lazy">
                </div>
                <div class="card-info">
                    <span class="game-showcase-title">${escHtml(g.name)}</span>
                    <span class="game-showcase-genre">${escHtml(g.genre)}</span>
                </div>
            </div>`;
        });
        
        // Duplicate set for seamless loop
        grid.innerHTML = html + html;
        
    } catch (e) {
        console.warn('Failed to load showcase games:', e);
    }
}

// ── Init ──────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
    fetchShowcaseGames();
    
    // Set initial budget label
    updateBudgetLabel(document.getElementById('tb-budget').value);
    
    // Set landing page on init
    goHome();
});
