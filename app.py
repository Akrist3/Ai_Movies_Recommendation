import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# Download files if not present
def download_file(file_id, output):
    if not os.path.exists(output):
        st.warning(f"Downloading {output}...")
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output, quiet=False)

# Download all required files
download_file("1hmal9e3tbE9kBFvYH4Q5pKFksi8e61rp", "similarity.pkl")
download_file("1p5IbvXBBtdakG9Sz1azeUT20E1SIzsyF", "movies.pkl")
download_file("1W1PX6EGqIVxNxUnlg8I54yx2PR9GFfaC", "movies_dict.pkl")

# TMDB API Key
api_key = '0a194b7168a5cebbc31e5bec8fc2d58c'


# Fetch movie details using title instead of ID

def fetch_movie_details_by_title(title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
        search_response = requests.get(search_url)
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data['results']:
                movie = search_data['results'][0]
                poster = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get(
                    'poster_path') else "https://via.placeholder.com/300x450?text=No+Poster"
                overview = movie.get('overview', 'No overview available.')
                rating = movie.get('vote_average', 'N/A')
                movie_id = movie['id']
                details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
                details_response = requests.get(details_url)
                genres = "N/A"
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    genres = ", ".join([g['name'] for g in details_data.get('genres', [])])
                return poster, overview, rating, genres
        return "https://via.placeholder.com/300x450?text=No+Poster", "No overview available.", "N/A", "N/A"
    except:
        return "https://via.placeholder.com/300x450?text=No+Poster", "Error fetching details", "N/A", "N/A"


# Load Data

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


# Streamlit App Layout
st.set_page_config(page_title="Hybrid Movie Recommender", page_icon="🎬", layout="wide")

st.title("🎬 AI-Powered Hybrid Movie Recommendation System")
st.markdown("##### Get personalized movie suggestions combining content similarity and popularity scores!")

selected_movie = st.selectbox("🎞️ Select a movie you like:", movies['title'].values)


st.write("Movies:", movies.shape)
st.write("Similarity:", len(similarity))
# Recommend Function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index

    # Check if movie exists
    if len(movie_index) == 0:
        return ["Movie not found"]

    movie_index = movie_index[0]

    # Safety check for mismatch
    if movie_index >= len(similarity):
        return ["Data mismatch error"]

    distances = similarity[movie_index]

    movie_list = sorted(list(enumerate(distances)),
                        reverse=True,
                        key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movie_list:
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies

# Display Recommendations

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
            st.markdown(f"📝 {overview[:150]}...")
