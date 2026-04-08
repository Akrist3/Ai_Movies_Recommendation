import streamlit as st
import pickle
import requests
import os
import gdown

# -------------------------------
# DOWNLOAD FILES (ONLY IF NOT EXIST)
# -------------------------------
def download_file(file_id, output):
    if not os.path.exists(output):
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        gdown.download(url, output, quiet=False, fuzzy=True)

download_file("1W1PX6EGqIVxNxUnlg8I54yx2PR9GFfaC", "similarity.pkl")
download_file("1hmal9e3tbE9kBFvYH4Q5pKFksi8e61rp", "movies.pkl")
download_file("1p5IbvXBBtdakG9Sz1azeUT20E1SIzsyF", "movies_dict.pkl")

# -------------------------------
# LOAD FILES
# -------------------------------
similarity = pickle.load(open("similarity.pkl", "rb"))
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))

# -------------------------------
# API KEY
# -------------------------------
api_key = st.secrets["TMDB_API_KEY"]

# -------------------------------
# FETCH MOVIE DETAILS
# -------------------------------
def fetch_movie_details_by_title(title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
        response = requests.get(search_url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data['results']:
                movie = data['results'][0]

                poster_path = movie.get('poster_path')
                poster = (
                    f"https://image.tmdb.org/t/p/w500{poster_path}"
                    if poster_path else
                    "https://via.placeholder.com/300x450?text=No+Poster"
                )

                overview = movie.get('overview', "No overview available.")
                rating = movie.get('vote_average', "N/A")
                movie_id = movie['id']

                # Fetch genres
                details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
                details_response = requests.get(details_url, timeout=5)

                genres = "N/A"
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    genres = ", ".join([g['name'] for g in details_data.get('genres', [])])

                return poster, overview, rating, genres

        return "https://via.placeholder.com/300x450?text=No+Poster", "No overview available.", "N/A", "N/A"

    except:
        return "https://via.placeholder.com/300x450?text=No+Poster", "Error fetching details", "N/A", "N/A"


# -------------------------------
# RECOMMEND FUNCTION (DICT BASED)
# -------------------------------
def recommend(movie):
    if movie not in movies_dict['title']:
        return ["Movie not found"]

    movie_index = movies_dict['title'].index(movie)

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    for i in movie_list:
        recommended_movies.append(movies_dict['title'][i[0]])

    return recommended_movies


# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="Hybrid Movie Recommender", page_icon="🎬", layout="wide")

st.title("🎬 AI-Powered Hybrid Movie Recommendation System")
st.markdown("##### Get personalized movie suggestions combining content similarity and popularity scores!")

# Dropdown
selected_movie = st.selectbox(
    "🎞️ Select a movie you like:",
    movies_dict['title']
)

# Button
if st.button('🔍 Show Recommendations'):
    recommended_movie_titles = recommend(selected_movie)

    st.subheader("🎯 Recommended Movies for You:")
    cols = st.columns(5)

    for i, title in enumerate(recommended_movie_titles):
        poster, overview, rating, genres = fetch_movie_details_by_title(title)

        with cols[i % 5]:
            st.image(poster, use_container_width=True)
            st.markdown(f"**🎬 {title}**")
            st.markdown(f"⭐ **Rating:** {rating}")
            st.markdown(f"🎭 **Genres:** {genres}")
            st.markdown(f"📝 {overview[:120]}...")