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

# ── Load files (only once) ─────────────────────────────────────────────────────
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

                # FIX: 'overview' was missing — now fetched from search result
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
    matches = movies[movies["title"] == movie].index
    if len(matches) == 0:
        return ["Movie not found"]

    movie_index = matches[0]
    if movie_index >= len(similarity):
        return ["Data mismatch error"]

    distances  = similarity[movie_index]
    movie_list = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]
    return [movies.iloc[i[0]].title for i in movie_list]

# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("🎬 AI-Powered Hybrid Movie Recommendation System")
st.markdown("##### Get personalised movie suggestions combining content similarity and popularity scores!")

# FIX: safe access — movies_dict may be a plain dict or a DataFrame-like object
titles = (
    movies_dict["title"]
    if isinstance(movies_dict, dict)
    else movies_dict.get("title", movies["title"].tolist())
)

selected_movie = st.selectbox("🎞️ Select a movie you like:", titles)

if st.button("🔍 Show Recommendations"):
    recommended_titles = recommend(selected_movie)

    st.subheader("🎯 Recommended Movies for You:")
    cols = st.columns(5)

    for i, title in enumerate(recommended_titles):
        poster, overview, rating, genres = fetch_movie_details_by_title(title)
        with cols[i % 5]:
            st.image(poster, use_container_width=True)
            st.markdown(f"**🎬 {title}**")
            st.markdown(f"⭐ **Rating:** {rating}")
            st.markdown(f"🎭 **Genres:** {genres}")
            st.markdown(f"📝 {overview[:150]}...")