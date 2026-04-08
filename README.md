# 🎬 AI-Powered Hybrid Movie Recommendation System

A content-based movie recommendation web app built with **Python** and **Streamlit**, deployed on Streamlit Cloud. It suggests 5 similar movies based on your selection and fetches live posters, ratings, genres, and overviews from the TMDB API.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aimovierecommendationbyme.streamlit.app)

---

## 🚀 Features

- 🔍 Select any movie from a list of thousands
- 🎯 Get 5 personalised recommendations instantly
- 🖼️ Live movie posters fetched from TMDB
- ⭐ Ratings, genres, and overview for each recommendation
- ☁️ Deployed on Streamlit Cloud — no setup needed to use it

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Language | Python 3 |
| ML / Similarity | Cosine similarity (precomputed `.pkl`) |
| Movie Data | TMDB API |
| Model Storage | Google Drive (via `gdown`) |
| Deployment | Streamlit Cloud |

---

## 📁 Project Structure

```
Ai_Movies_Recommendation/
│
├── app.py               # Main Streamlit app
├── requirements.txt     # Python dependencies
├── setup.sh             # Shell setup script
├── Procfile             # Process file for deployment
├── .gitignore
└── README.md
```

> **Note:** The `.pkl` model files (`similarity.pkl`, `movies.pkl`, `movies_dict.pkl`) are too large for GitHub and are downloaded automatically from Google Drive when the app starts.

---

## ⚙️ How It Works

1. On startup, the app downloads 3 precomputed pickle files from Google Drive:
   - `movies.pkl` — DataFrame of movie titles and metadata
   - `movies_dict.pkl` — Dictionary of movie titles for the dropdown
   - `similarity.pkl` — Precomputed cosine similarity matrix

2. The user selects a movie from the dropdown.

3. The app finds the movie's index and retrieves the top 5 most similar movies using the similarity matrix.

4. For each recommended movie, it calls the TMDB API to fetch the poster, rating, genres, and overview.

---

## 🔧 Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/Akrist3/Ai_Movies_Recommendation.git
cd Ai_Movies_Recommendation
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your TMDB API key

Create a `.streamlit/secrets.toml` file:

```toml
TMDB_API_KEY = "your_api_key_here"
```

Get a free API key at [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)

### 4. Run the app

```bash
streamlit run app.py
```

---

## ☁️ Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set `app.py` as the main file
4. Add your TMDB API key in **Secrets** under the app settings:
   ```
   TMDB_API_KEY = "your_api_key_here"
   ```
5. Click **Deploy**

---

## 📦 Requirements

```
streamlit
requests
pandas
scikit-learn
gdown
```

---

## 🙌 Acknowledgements

- [TMDB API](https://www.themoviedb.org/) for movie data and posters
- [Streamlit](https://streamlit.io/) for the web framework
- Dataset based on the TMDB 5000 Movies dataset

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
