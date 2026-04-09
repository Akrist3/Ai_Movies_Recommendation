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

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🎬 CineMatch AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">✦ Discover your next favourite film ✦</p>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

_, col_mid, _ = st.columns([1, 3, 1])
with col_mid:
    titles         = list(movies_dict["title"])
    selected_movie = st.selectbox("🎞️ Pick a movie you love", titles)
    st.markdown("<br>", unsafe_allow_html=True)
    go = st.button("🔍  FIND MY MOVIES")

st.markdown("<hr>", unsafe_allow_html=True)

if go:
    with st.spinner("🍿  Finding perfect matches..."):
        recommended_titles = recommend(selected_movie)

    st.markdown('<div class="section-header">🎯 Your Picks Are Ready!</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for i, title in enumerate(recommended_titles):
        poster, overview, rating, genres = fetch_movie_details_by_title(title)

        genre_badges = "".join(
            f'<span class="card-badge badge-genre">{g.strip()}</span>'
            for g in genres.split(",")[:2]
        ) if genres != "N/A" else ""

        card_html = f"""
        <div class="card-wrap-{i}">
          <div class="movie-card">
            <img class="card-poster" src="{poster}" alt="{title}"
                 onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'"/>
            <div class="card-body">
              <div class="card-title">{title}</div>
              <span class="card-badge badge-rating">⭐ {rating}</span>
              {genre_badges}
              <div class="card-overview">{overview}</div>
            </div>
          </div>
        </div>
        """
        with cols[i % 5]:
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:rgba(255,255,255,0.2);font-size:0.8rem;letter-spacing:2px;">POWERED BY TMDB · BUILT WITH STREAMLIT</p>',
        unsafe_allow_html=True
    )
