import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# ── Page config MUST be the very first Streamlit call ──────────────────────────
st.set_page_config(page_title="Hybrid Movie Recommender", page_icon="🎬", layout="wide")

# ── Download fresh model files ─────────────────────────────────────────────────
for file in ["similarity.pkl", "movies.pkl", "movies_dict.pkl"]:
    if os.path.exists(file):
        os.remove(file)

def download_file(file_id, output):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    gdown.download(url, output, quiet=False, fuzzy=True)

with st.spinner("Downloading model files…"):
    download_file("1W1PX6EGqIVxNxUnlg8I54yx2PR9GFfaC", "similarity.pkl")
    download_file("1hmal9e3tbE9kBFvYH4Q5pKFksi8e61rp", "movies.pkl")
    download_file("1p5IbvXBBtdakG9Sz1azeUT20E1SIzsyF", "movies_dict.pkl")

# ── Load files ─────────────────────────────────────────────────────────────────
with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

with open("movies.pkl", "rb") as f:
    movies = pickle.load(f)

with open("movies_dict.pkl", "rb") as f:
    movies_dict = pickle.load(f)

# ── TMDB API key ───────────────────────────────────────────────────────────────
api_key = st.secrets["TMDB_API_KEY"]

# ── Fetch movie details from TMDB ──────────────────────────────────────────────
def fetch_movie_details_by_title(title):
    try:
        search_url = (
            f"https://api.themoviedb.org/3/search/movie"
            f"?api_key={api_key}&query={title}"
        )
        search_response = requests.get(search_url, timeout=5)
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data["results"]:
                movie = search_data["results"][0]

                poster_path = movie.get("poster_path")
                poster = (
                    f"https://image.tmdb.org/t/p/w500{poster_path}"
                    if poster_path
                    else "https://via.placeholder.com/300x450?text=No+Poster"
                )

                overview = movie.get("overview", "No overview available.")
                rating   = movie.get("vote_average", "N/A")
                movie_id = movie["id"]

                details_url = (
                    f"https://api.themoviedb.org/3/movie/{movie_id}"
                    f"?api_key={api_key}&language=en-US"
                )
                details_response = requests.get(details_url, timeout=5)
                genres = "N/A"
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    genres = ", ".join(
                        [g["name"] for g in details_data.get("genres", [])]
                    )

                return poster, overview, rating, genres

    except Exception:
        pass

    return (
        "https://via.placeholder.com/300x450?text=No+Poster",
        "Error fetching details.",
        "N/A",
        "N/A",
    )

# ── Recommend function ─────────────────────────────────────────────────────────
def recommend(movie):
    # Convert to DataFrame if movies is a plain dict
    movies_df = movies if isinstance(movies, pd.DataFrame) else pd.DataFrame(movies)

    matches = movies_df[movies_df["title"] == movie].index
    if len(matches) == 0:
        return ["Movie not found"]

    movie_index = matches[0]
    if movie_index >= len(similarity):
        return ["Data mismatch error"]

    distances  = similarity[movie_index]
    movie_list = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]
    return [movies_df.iloc[i[0]].title for i in movie_list]


# ── UI ──────────────────────────────────────────────────────────
import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="CineMatch AI", page_icon="🎬", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
#  FULL PAGE CSS — Premium Dark Cinema Theme
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&display=swap');

/* ─ Reset & Base ─ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main { background: #080810 !important; }

[data-testid="stHeader"]          { background: transparent !important; }
[data-testid="stToolbar"]         { display: none !important; }
[data-testid="stDecoration"]      { display: none !important; }
#MainMenu, footer                 { display: none !important; }
[data-testid="stSidebar"]         { display: none !important; }

/* ─ Animated mesh background ─ */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background:
        radial-gradient(ellipse 900px 600px at 15% 20%,  rgba(220,38,127,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 700px 500px at 85% 75%,  rgba(99,102,241,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 500px 400px at 50% 50%,  rgba(6,182,212,0.07)  0%, transparent 70%),
        #080810;
    animation: meshShift 12s ease-in-out infinite alternate;
    pointer-events: none;
}
@keyframes meshShift {
    0%   { opacity: 1; }
    50%  { opacity: 0.75; }
    100% { opacity: 1; }
}

/* ─ Grain overlay ─ */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed; inset: 0; z-index: 1;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none; opacity: 0.35;
}

[data-testid="stMain"] { position: relative; z-index: 2; }

/* ─ Main content padding ─ */
.block-container { padding: 2rem 3rem 4rem !important; max-width: 1400px !important; }

/* ─ Hero title ─ */
.hero-wrap {
    text-align: center;
    padding: 3rem 1rem 1rem;
    animation: heroIn 1s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes heroIn {
    from { opacity: 0; transform: translateY(-40px) scale(0.95); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem; font-weight: 700;
    letter-spacing: 5px; text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 0.6rem;
    animation: fadeUp 0.7s ease 0.2s both;
}

.hero-title {
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(4rem, 10vw, 8rem);
    line-height: 0.9; letter-spacing: 6px;
    background: linear-gradient(135deg, #f472b6 0%, #818cf8 40%, #22d3ee 80%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: titlePop 1s cubic-bezier(0.34,1.56,0.64,1) 0.1s both;
    filter: drop-shadow(0 0 60px rgba(244,114,182,0.3));
}
@keyframes titlePop {
    0%   { transform: scale(0.4) rotate(-3deg); opacity: 0; }
    65%  { transform: scale(1.06) rotate(0.5deg); }
    100% { transform: scale(1) rotate(0); opacity: 1; }
}

.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem; font-weight: 500;
    color: rgba(255,255,255,0.38);
    letter-spacing: 1px; margin-top: 0.8rem;
    animation: fadeUp 0.7s ease 0.4s both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ─ Divider ─ */
.fancy-divider {
    height: 1px; margin: 2rem 0;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(244,114,182,0.5) 25%,
        rgba(129,140,248,0.5) 50%,
        rgba(34,211,238,0.5) 75%,
        transparent 100%);
    animation: fadeUp 0.5s ease 0.6s both;
}

/* ─ Select label ─ */
[data-testid="stSelectbox"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important; font-weight: 700 !important;
    letter-spacing: 3px !important; text-transform: uppercase !important;
    color: rgba(255,255,255,0.4) !important;
}

/* ─ Selectbox ─ */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(244,114,182,0.3) !important;
    border-radius: 14px !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.05rem !important; font-weight: 600 !important;
    backdrop-filter: blur(16px) !important;
    transition: border-color 0.3s, box-shadow 0.3s, transform 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    animation: fadeUp 0.6s ease 0.7s both;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(129,140,248,0.6) !important;
    box-shadow: 0 0 0 3px rgba(129,140,248,0.12), 0 8px 32px rgba(129,140,248,0.15) !important;
    transform: translateY(-2px) !important;
}

/* ─ Button ─ */
[data-testid="stButton"] { text-align: center; }
[data-testid="stButton"] > button {
    display: inline-block !important;
    background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #06b6d4 100%) !important;
    background-size: 200% 200% !important;
    color: white !important;
    font-family: 'Bebas Neue', cursive !important;
    font-size: 1.4rem !important; letter-spacing: 4px !important;
    padding: 0.75rem 3.5rem !important;
    border: none !important; border-radius: 100px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 24px rgba(236,72,153,0.35), 0 0 0 0 rgba(236,72,153,0) !important;
    animation: fadeUp 0.6s ease 0.9s both, btnGlow 3s ease-in-out 2s infinite !important;
    transition: transform 0.2s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.3s !important;
}
@keyframes btnGlow {
    0%,100% { box-shadow: 0 4px 24px rgba(236,72,153,0.35), 0 0 0 0 rgba(236,72,153,0); }
    50%      { box-shadow: 0 8px 40px rgba(236,72,153,0.55), 0 0 0 8px rgba(236,72,153,0); }
}
[data-testid="stButton"] > button:hover {
    transform: scale(1.07) translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(236,72,153,0.5) !important;
}
[data-testid="stButton"] > button:active {
    transform: scale(0.96) !important;
}

/* ─ Results header ─ */
.results-header {
    font-family: 'Bebas Neue', cursive;
    font-size: 2.8rem; letter-spacing: 5px;
    text-align: center; margin: 2.5rem 0 1.8rem;
    background: linear-gradient(90deg, #f472b6, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: bounceIn 0.7s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes bounceIn {
    0%  { transform: scale(0.5) translateY(20px); opacity: 0; }
    70% { transform: scale(1.05) translateY(-4px); }
    100%{ transform: scale(1) translateY(0); opacity: 1; }
}

/* ─ Card grid ─ */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    padding: 0 0 3rem;
}

/* ─ Individual card ─ */
.cine-card {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    background: rgba(15,15,30,0.8);
    border: 1px solid rgba(255,255,255,0.07);
    transition: transform 0.4s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.4s ease,
                border-color 0.3s;
    cursor: pointer;
    backdrop-filter: blur(10px);
}
.cine-card:hover {
    transform: translateY(-16px) scale(1.03);
    box-shadow: 0 30px 60px rgba(0,0,0,0.5),
                0 0 0 1px rgba(244,114,182,0.4),
                0 0 40px rgba(244,114,182,0.15);
    border-color: rgba(244,114,182,0.35);
}
.cine-card:hover .card-overlay { opacity: 1; }
.cine-card:hover .card-img     { transform: scale(1.06); }

/* Poster */
.poster-wrap { position: relative; overflow: hidden; aspect-ratio: 2/3; }
.card-img {
    width: 100%; height: 100%;
    object-fit: cover; display: block;
    transition: transform 0.5s ease;
}

/* Gradient overlay on hover */
.card-overlay {
    position: absolute; inset: 0; opacity: 0;
    background: linear-gradient(to top, rgba(8,8,16,0.95) 0%, rgba(8,8,16,0.4) 50%, transparent 100%);
    transition: opacity 0.3s ease;
}

/* Rating pill on top-right */
.rating-pill {
    position: absolute; top: 10px; right: 10px;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,214,10,0.4);
    border-radius: 20px;
    padding: 4px 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem; font-weight: 700;
    color: #FFD60A;
    display: flex; align-items: center; gap: 4px;
}

/* Card body */
.card-info {
    padding: 14px 14px 16px;
}
.card-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem; font-weight: 700;
    color: #ffffff; line-height: 1.3;
    margin-bottom: 8px;
    display: -webkit-box;
    -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.genre-row { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
.genre-tag {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.5px;
    padding: 2px 8px; border-radius: 20px;
    background: rgba(99,102,241,0.15);
    color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.25);
}
.card-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem; line-height: 1.5;
    color: rgba(255,255,255,0.38);
    display: -webkit-box;
    -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}

/* ─ Staggered pop-in ─ */
.pop-0 { animation: cardPop 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.05s both; }
.pop-1 { animation: cardPop 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.15s both; }
.pop-2 { animation: cardPop 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.25s both; }
.pop-3 { animation: cardPop 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.35s both; }
.pop-4 { animation: cardPop 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.45s both; }
@keyframes cardPop {
    0%   { opacity: 0; transform: scale(0.65) translateY(50px) rotate(-2deg); }
    65%  { opacity: 1; transform: scale(1.04) translateY(-6px) rotate(0.3deg); }
    100% { opacity: 1; transform: scale(1) translateY(0) rotate(0); }
}

/* ─ Footer ─ */
.cine-footer {
    text-align: center; padding: 2rem 0 1rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem; letter-spacing: 3px; text-transform: uppercase;
    color: rgba(255,255,255,0.15);
}

/* ─ Spinner ─ */
[data-testid="stSpinner"] > div { border-color: #ec4899 transparent transparent !important; }

/* ─ Scrollbar ─ */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080810; }
::-webkit-scrollbar-thumb { background: linear-gradient(#ec4899,#8b5cf6); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DOWNLOAD MODEL FILES
# ══════════════════════════════════════════════════════════════════════════════
for file in ["similarity.pkl", "movies.pkl", "movies_dict.pkl"]:
    if os.path.exists(file):
        os.remove(file)

def download_file(file_id, output):
    gdown.download(
        f"https://drive.google.com/uc?export=download&id={file_id}",
        output, quiet=False, fuzzy=True
    )

with st.spinner("Loading cinema engine…"):
    download_file("1W1PX6EGqIVxNxUnlg8I54yx2PR9GFfaC", "similarity.pkl")
    download_file("1hmal9e3tbE9kBFvYH4Q5pKFksi8e61rp",  "movies.pkl")
    download_file("1p5IbvXBBtdakG9Sz1azeUT20E1SIzsyF",  "movies_dict.pkl")

with open("similarity.pkl", "rb") as f: similarity  = pickle.load(f)
with open("movies.pkl",     "rb") as f: movies      = pickle.load(f)
with open("movies_dict.pkl","rb") as f: movies_dict = pickle.load(f)

api_key = st.secrets["TMDB_API_KEY"]


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def fetch_movie_details_by_title(title):
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}",
            timeout=5
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                m      = results[0]
                poster = (f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
                          if m.get("poster_path")
                          else "https://via.placeholder.com/300x450/080810/444?text=No+Poster")
                overview = m.get("overview", "No overview available.")
                rating   = round(float(m.get("vote_average", 0)), 1)
                mid = m["id"]
                dr = requests.get(
                    f"https://api.themoviedb.org/3/movie/{mid}?api_key={api_key}",
                    timeout=5
                )
                genres = []
                if dr.status_code == 200:
                    genres = [g["name"] for g in dr.json().get("genres", [])[:3]]
                return poster, overview, rating, genres
    except Exception:
        pass
    return ("https://via.placeholder.com/300x450/080810/444?text=No+Poster",
            "Error fetching details.", 0.0, [])


def recommend(movie):
    df = movies if isinstance(movies, pd.DataFrame) else pd.DataFrame(movies)
    matches = df[df["title"] == movie].index
    if len(matches) == 0: return []
    idx = matches[0]
    if idx >= len(similarity): return []
    top5 = sorted(enumerate(similarity[idx]), key=lambda x: x[1], reverse=True)[1:6]
    return [df.iloc[i[0]].title for i in top5]


# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">✦ AI Powered ✦</div>
  <div class="hero-title">CineMatch</div>
  <div class="hero-sub">Tell us one film. We'll find your next five.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

# ── Selectbox + button centred ─────────────────────────────────────────────────
_, mid_col, _ = st.columns([1, 2, 1])
with mid_col:
    titles         = list(movies_dict["title"])
    selected_movie = st.selectbox("🎬  Choose your favourite movie", titles)
    st.markdown("<br>", unsafe_allow_html=True)
    go = st.button("✦  Get Recommendations  ✦")

st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS  — rendered as ONE big HTML block (fixes the raw-HTML bug)
# ══════════════════════════════════════════════════════════════════════════════
if go:
    with st.spinner("Finding your perfect matches…"):
        rec_titles = recommend(selected_movie)

    if not rec_titles:
        st.error("Movie not found in our database. Please try another title.")
    else:
        # Fetch all details first
        movies_data = []
        for title in rec_titles:
            poster, overview, rating, genres = fetch_movie_details_by_title(title)
            movies_data.append({
                "title":    title,
                "poster":   poster,
                "overview": overview,
                "rating":   rating,
                "genres":   genres,
            })

        # Build genre tags HTML
        def genre_html(genres):
            return "".join(f'<span class="genre-tag">{g}</span>' for g in genres)

        # Build one single card grid — avoids Streamlit column HTML escaping
        cards_html = '<div class="results-header">✦ Top Picks For You ✦</div><div class="cards-grid">'
        for i, m in enumerate(movies_data):
            g_html   = genre_html(m["genres"]) if m["genres"] else ""
            overview = m["overview"][:160] + "…" if len(m["overview"]) > 160 else m["overview"]
            rating   = f"⭐ {m['rating']}" if m["rating"] else "N/A"
            cards_html += f"""
            <div class="cine-card pop-{i}">
              <div class="poster-wrap">
                <img class="card-img"
                     src="{m['poster']}"
                     alt="{m['title']}"
                     onerror="this.src='https://via.placeholder.com/300x450/080810/444?text=No+Poster'"/>
                <div class="card-overlay"></div>
                <div class="rating-pill">{rating}</div>
              </div>
              <div class="card-info">
                <div class="card-name">{m['title']}</div>
                <div class="genre-row">{g_html}</div>
                <div class="card-desc">{overview}</div>
              </div>
            </div>
            """
        cards_html += "</div>"

        st.markdown(cards_html, unsafe_allow_html=True)

        st.markdown(
            '<div class="cine-footer">Powered by TMDB &nbsp;·&nbsp; Built with Streamlit</div>',
            unsafe_allow_html=True
        )# ── Footer ──
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")