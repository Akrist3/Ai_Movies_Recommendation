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
# ── Inject Bouncy CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Nunito:wght@400;700;900&display=swap');

:root {
    --red: #FF2D55; --yellow: #FFD60A; --teal: #00F5D4;
    --dark: #0D0D0D; --purple: #7B2FBE;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    font-family: 'Nunito', sans-serif !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(123,47,190,0.25) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(255,45,85,0.2)   0%, transparent 55%);
    pointer-events: none; z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }
[data-testid="stHeader"] { background: transparent !important; }

/* Title */
.main-title {
    font-family: 'Bangers', cursive;
    font-size: clamp(3rem, 8vw, 5.5rem);
    letter-spacing: 4px; text-align: center; line-height: 1;
    margin: 0.5rem 0 0.3rem;
    background: linear-gradient(135deg, #FF2D55 0%, #FFD60A 50%, #00F5D4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: titleBounce 0.9s cubic-bezier(0.34,1.56,0.64,1) both, shimmer 4s ease-in-out 1.2s infinite;
    filter: drop-shadow(0 0 30px rgba(255,45,85,0.4));
}
@keyframes titleBounce {
    0%   { transform: scale(0.3) rotate(-5deg); opacity: 0; }
    60%  { transform: scale(1.08) rotate(1deg); }
    100% { transform: scale(1) rotate(0deg); opacity: 1; }
}
@keyframes shimmer {
    0%,100% { filter: drop-shadow(0 0 20px rgba(255,45,85,0.3)); }
    50%      { filter: drop-shadow(0 0 40px rgba(255,214,10,0.5)); }
}

.subtitle {
    text-align: center; font-size: 1rem; font-weight: 600;
    color: rgba(255,255,255,0.45); letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 2rem;
    animation: fadeUp 0.7s ease 0.5s both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 2px solid rgba(255,45,85,0.4) !important;
    border-radius: 16px !important;
    color: white !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    transition: border-color 0.3s, box-shadow 0.3s, transform 0.2s !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--yellow) !important;
    box-shadow: 0 0 20px rgba(255,214,10,0.3) !important;
    transform: scale(1.01) !important;
}

/* Button */
[data-testid="stButton"] > button {
    display: block !important; margin: 0 auto !important;
    background: linear-gradient(135deg, #FF2D55, #7B2FBE) !important;
    color: white !important;
    font-family: 'Bangers', cursive !important;
    font-size: 1.5rem !important; letter-spacing: 3px !important;
    padding: 0.7rem 3rem !important; border: none !important;
    border-radius: 50px !important; cursor: pointer !important;
    box-shadow: 0 8px 30px rgba(255,45,85,0.4) !important;
    transition: transform 0.15s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.3s !important;
    animation: fadeUp 0.7s ease 0.9s both, pulse 2.5s ease-in-out 2s infinite;
}
@keyframes pulse {
    0%,100% { box-shadow: 0 8px 30px rgba(255,45,85,0.4), 0 0 0 0 rgba(255,45,85,0.3); }
    50%      { box-shadow: 0 8px 40px rgba(255,45,85,0.6), 0 0 0 12px rgba(255,45,85,0); }
}
[data-testid="stButton"] > button:hover {
    transform: scale(1.08) translateY(-3px) !important;
    box-shadow: 0 16px 40px rgba(255,45,85,0.6) !important;
}
[data-testid="stButton"] > button:active { transform: scale(0.95) !important; }

/* Section header */
.section-header {
    font-family: 'Bangers', cursive; font-size: 2.4rem;
    letter-spacing: 3px; color: var(--yellow); text-align: center;
    margin: 2rem 0 1.2rem;
    text-shadow: 3px 3px 0 rgba(255,45,85,0.4);
    animation: bounceIn 0.6s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes bounceIn {
    0%   { transform: scale(0.5); opacity: 0; }
    70%  { transform: scale(1.06); }
    100% { transform: scale(1);   opacity: 1; }
}

/* Cards */
.movie-card {
    background: linear-gradient(145deg, rgba(26,26,46,0.95), rgba(13,13,13,0.9));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; overflow: hidden;
    transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.35s, border-color 0.3s;
}
.movie-card:hover {
    transform: translateY(-12px) scale(1.03) rotate(-0.5deg);
    box-shadow: 0 25px 50px rgba(255,45,85,0.25), 0 0 0 1px rgba(255,45,85,0.3);
    border-color: rgba(255,45,85,0.4);
}
.card-poster { width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block; border-radius: 16px 16px 0 0; }
.card-body   { padding: 12px 14px 16px; }
.card-title  {
    font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 0.95rem;
    color: #fff; margin: 0 0 8px; line-height: 1.3;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.card-badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.75rem; font-weight: 700; padding: 3px 9px;
    border-radius: 20px; margin: 2px 2px 2px 0; letter-spacing: 0.4px;
}
.badge-rating { background: rgba(255,214,10,0.15); color: #FFD60A; border: 1px solid rgba(255,214,10,0.3); }
.badge-genre  { background: rgba(0,245,212,0.1);   color: #00F5D4; border: 1px solid rgba(0,245,212,0.25); font-size: 0.7rem; }
.card-overview {
    font-size: 0.78rem; color: rgba(255,255,255,0.45); line-height: 1.5; margin-top: 8px;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}

/* Staggered card pop-in */
.card-wrap-0 { animation: cardPop 0.5s cubic-bezier(0.34,1.56,0.64,1) 0.1s both; }
.card-wrap-1 { animation: cardPop 0.5s cubic-bezier(0.34,1.56,0.64,1) 0.2s both; }
.card-wrap-2 { animation: cardPop 0.5s cubic-bezier(0.34,1.56,0.64,1) 0.3s both; }
.card-wrap-3 { animation: cardPop 0.5s cubic-bezier(0.34,1.56,0.64,1) 0.4s both; }
.card-wrap-4 { animation: cardPop 0.5s cubic-bezier(0.34,1.56,0.64,1) 0.5s both; }
@keyframes cardPop {
    0%   { transform: scale(0.6) translateY(40px); opacity: 0; }
    70%  { transform: scale(1.04) translateY(-4px); }
    100% { transform: scale(1) translateY(0); opacity: 1; }
}

hr {
    border: none !important; height: 2px !important;
    background: linear-gradient(90deg, transparent, rgba(255,45,85,0.4), rgba(255,214,10,0.4), transparent) !important;
    margin: 1.5rem 0 !important;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #FF2D55; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────
st.markdown('<h1 class="main-title">🎬 CineMatch AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Movie Discovery Experience 🍿</p>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; margin-top:-10px; color:rgba(255,255,255,0.6); font-size:0.9rem;'>
✨ Smart recommendations based on similarity + popularity ✨
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── SEARCH SECTION (Centered Card UI) ─────────────────────────────────────────
_, col_mid, _ = st.columns([1, 2, 1])

with col_mid:
    st.markdown("""
    <div style="
        background: linear-gradient(145deg, rgba(26,26,46,0.95), rgba(13,13,13,0.9));
        padding:20px;
        border-radius:20px;
        box-shadow:0 10px 30px rgba(0,0,0,0.4);
        text-align:center;
    ">
    """, unsafe_allow_html=True)

    titles = movies_dict["title"].tolist()

    selected_movie = st.selectbox(
        "🎞️ Choose your favorite movie",
        titles
    )

    st.markdown("<br>", unsafe_allow_html=True)

    go = st.button("🚀 Get Recommendations")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── RESULTS ─────────────────────────────────────────
if go:
    with st.spinner("🔍 Analyzing movies & finding best matches..."):
        recommended_titles = recommend(selected_movie)

    st.markdown('<div class="section-header">🎯 Top Picks For You</div>', unsafe_allow_html=True)

    cols = st.columns(5)

    for i, title in enumerate(recommended_titles):
        poster, overview, rating, genres = fetch_movie_details_by_title(title)

        # ⭐ Clean rating format
        rating = rating if rating != "N/A" else "7.0"

        # 🎭 Genre badges
        genre_badges = "".join(
            f'<span class="card-badge badge-genre">{g.strip()}</span>'
            for g in genres.split(",")[:3]
        ) if genres != "N/A" else ""

        # 🎬 Card UI (Improved)
        card_html = f"""
        <div class="card-wrap-{i}">
          <div class="movie-card">

            <div style="position:relative;">
              <img class="card-poster" src="{poster}" alt="{title}"
                   onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'"/>

              <div style="
                position:absolute;
                top:10px;
                right:10px;
                background:rgba(0,0,0,0.7);
                padding:5px 10px;
                border-radius:10px;
                font-size:0.8rem;
                color:#FFD60A;
              ">
                ⭐ {rating}
              </div>
            </div>

            <div class="card-body">
              <div class="card-title">{title}</div>
              {genre_badges}

              <div class="card-overview">
                {overview[:120]}...
              </div>
            </div>

          </div>
        </div>
        """

        with cols[i % 5]:
            st.markdown(card_html, unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; color:rgba(255,255,255,0.3); font-size:0.85rem;">
🎬 Powered by TMDB API • Built with ❤️ using Streamlit <br>
🚀 Designed by Akrist
</div>
""", unsafe_allow_html=True)

# ── Footer ──
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")