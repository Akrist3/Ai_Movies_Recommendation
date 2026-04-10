import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG — must be FIRST
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="CineMatch AI", page_icon="🎬", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS (page bg, fonts, button, selectbox — NOT card styles)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main { background: #080810 !important; }

[data-testid="stHeader"]     { background: transparent !important; }
[data-testid="stToolbar"]    { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebar"]    { display: none !important; }
#MainMenu, footer            { display: none !important; }

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background:
        radial-gradient(ellipse 900px 600px at 15% 20%, rgba(220,38,127,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 700px 500px at 85% 75%, rgba(99,102,241,0.18) 0%, transparent 65%),
        #080810;
    animation: meshShift 12s ease-in-out infinite alternate;
    pointer-events: none;
}
@keyframes meshShift {
    0%   { opacity: 1; }
    50%  { opacity: 0.75; }
    100% { opacity: 1; }
}
[data-testid="stMain"] { position: relative; z-index: 2; }
.block-container { padding: 2rem 3rem 4rem !important; max-width: 1400px !important; }

/* Selectbox */
[data-testid="stSelectbox"] label {
    font-family: 'DM Sans', sans-serif !important; font-size: 0.8rem !important;
    font-weight: 700 !important; letter-spacing: 3px !important;
    text-transform: uppercase !important; color: rgba(255,255,255,0.4) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(244,114,182,0.4) !important;
    border-radius: 14px !important; color: white !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.05rem !important; font-weight: 600 !important;
}

/* Button */
[data-testid="stButton"] { text-align: center; }
[data-testid="stButton"] > button {
    display: inline-block !important;
    background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #06b6d4 100%) !important;
    color: white !important; font-family: 'Bebas Neue', cursive !important;
    font-size: 1.4rem !important; letter-spacing: 4px !important;
    padding: 0.75rem 3.5rem !important; border: none !important;
    border-radius: 100px !important; cursor: pointer !important;
    transition: transform 0.2s, box-shadow 0.3s !important;
    box-shadow: 0 4px 24px rgba(236,72,153,0.4) !important;
}
[data-testid="stButton"] > button:hover {
    transform: scale(1.07) translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(236,72,153,0.55) !important;
}
[data-testid="stButton"] > button:active { transform: scale(0.96) !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080810; }
::-webkit-scrollbar-thumb { background: linear-gradient(#ec4899,#8b5cf6); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DOWNLOAD & LOAD
# ══════════════════════════════════════════════════════════════════════════════
for file in ["similarity.pkl", "movies.pkl", "movies_dict.pkl"]:
    if os.path.exists(file):
        os.remove(file)

def download_file(file_id, output):
    gdown.download(f"https://drive.google.com/uc?export=download&id={file_id}",
                   output, quiet=False, fuzzy=True)

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
            timeout=5)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                m      = results[0]
                poster = (f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
                          if m.get("poster_path") else "https://via.placeholder.com/300x450/0f0f1e/666?text=No+Poster")
                overview = m.get("overview", "No overview available.")
                rating   = round(float(m.get("vote_average", 0)), 1)
                dr = requests.get(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={api_key}", timeout=5)
                genres = []
                if dr.status_code == 200:
                    genres = [g["name"] for g in dr.json().get("genres", [])[:3]]
                return poster, overview, rating, genres
    except Exception:
        pass
    return ("https://via.placeholder.com/300x450/0f0f1e/666?text=No+Poster", "Error fetching details.", 0.0, [])

def recommend(movie):
    df      = movies if isinstance(movies, pd.DataFrame) else pd.DataFrame(movies)
    matches = df[df["title"] == movie].index
    if len(matches) == 0: return []
    idx = matches[0]
    if idx >= len(similarity): return []
    top5 = sorted(enumerate(similarity[idx]), key=lambda x: x[1], reverse=True)[1:6]
    return [df.iloc[i[0]].title for i in top5]

# ══════════════════════════════════════════════════════════════════════════════
#  HERO — inline styles only
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;padding:3rem 1rem 1rem;">
  <div style="font-family:'DM Sans',sans-serif;font-size:0.78rem;font-weight:700;
              letter-spacing:5px;text-transform:uppercase;color:#6366f1;margin-bottom:0.6rem;">
    ✦ AI Powered ✦
  </div>
  <div style="font-family:'Bebas Neue',cursive;font-size:clamp(4rem,10vw,8rem);
              line-height:0.9;letter-spacing:6px;
              background:linear-gradient(135deg,#f472b6 0%,#818cf8 40%,#22d3ee 80%);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    CineMatch
  </div>
  <div style="font-family:'DM Sans',sans-serif;font-size:1rem;font-weight:500;
              color:rgba(255,255,255,0.38);letter-spacing:1px;margin-top:0.8rem;">
    Tell us one film. We'll find your next five.
  </div>
</div>
""", unsafe_allow_html=True)

# Divider
st.markdown("""
<div style="height:1px;margin:1.5rem 0;
  background:linear-gradient(90deg,transparent,rgba(244,114,182,0.5) 25%,
  rgba(129,140,248,0.5) 50%,rgba(34,211,238,0.5) 75%,transparent);"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SELECTBOX + BUTTON  (Streamlit native widgets)
# ══════════════════════════════════════════════════════════════════════════════
_, mid_col, _ = st.columns([1, 2, 1])
with mid_col:
    titles         = list(movies_dict["title"])
    selected_movie = st.selectbox("🎬  Choose your favourite movie", titles)
    st.markdown("<br>", unsafe_allow_html=True)
    go = st.button("✦  Get Recommendations  ✦")

st.markdown("""
<div style="height:1px;margin:1.5rem 0;
  background:linear-gradient(90deg,transparent,rgba(244,114,182,0.5) 25%,
  rgba(129,140,248,0.5) 50%,rgba(34,211,238,0.5) 75%,transparent);"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS — every card uses 100% inline styles (no class names on cards)
# ══════════════════════════════════════════════════════════════════════════════
if go:
    with st.spinner("Finding your perfect matches…"):
        rec_titles = recommend(selected_movie)

    if not rec_titles:
        st.error("Movie not found. Please try another title.")
    else:
        # Fetch details
        movies_data = []
        for title in rec_titles:
            poster, overview, rating, genres = fetch_movie_details_by_title(title)
            movies_data.append({"title": title, "poster": poster,
                                 "overview": overview, "rating": rating, "genres": genres})

        # Results heading
        st.markdown("""
        <div style="font-family:'Bebas Neue',cursive;font-size:2.8rem;letter-spacing:5px;
                    text-align:center;margin:2rem 0 1.5rem;
                    background:linear-gradient(90deg,#f472b6,#818cf8);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
          ✦ Top Picks For You ✦
        </div>
        """, unsafe_allow_html=True)

        # Render each card in its own st.column (Streamlit-native columns)
        cols = st.columns(5)
        for i, m in enumerate(movies_data):
            overview_short = m["overview"][:150] + "…" if len(m["overview"]) > 150 else m["overview"]
            rating_txt     = f"⭐ {m['rating']}" if m["rating"] else "N/A"

            genre_pills = "".join(
                f'<span style="display:inline-block;font-family:DM Sans,sans-serif;'
                f'font-size:0.65rem;font-weight:700;letter-spacing:0.5px;padding:2px 8px;'
                f'border-radius:20px;background:rgba(99,102,241,0.18);color:#a5b4fc;'
                f'border:1px solid rgba(99,102,241,0.3);margin:2px 2px 2px 0;">{g}</span>'
                for g in m["genres"]
            )

            card = f"""
            <div style="border-radius:16px;overflow:hidden;
                        background:rgba(15,15,30,0.85);
                        border:1px solid rgba(255,255,255,0.08);
                        font-family:'DM Sans',sans-serif;
                        transition:transform 0.3s ease,box-shadow 0.3s ease;
                        margin-bottom:1rem;">
              <!-- Poster -->
              <div style="position:relative;width:100%;padding-top:150%;overflow:hidden;">
                <img src="{m['poster']}"
                     alt="{m['title']}"
                     onerror="this.src='https://via.placeholder.com/300x450/0f0f1e/666?text=No+Poster'"
                     style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;display:block;"/>
                <!-- Rating pill -->
                <div style="position:absolute;top:10px;right:10px;
                            background:rgba(0,0,0,0.78);border-radius:20px;
                            padding:4px 10px;border:1px solid rgba(255,214,10,0.45);
                            font-size:0.75rem;font-weight:700;color:#FFD60A;
                            font-family:'DM Sans',sans-serif;">
                  {rating_txt}
                </div>
                <!-- Bottom gradient -->
                <div style="position:absolute;bottom:0;left:0;right:0;height:60%;
                            background:linear-gradient(to top,rgba(8,8,16,0.9) 0%,transparent 100%);
                            pointer-events:none;"></div>
              </div>
              <!-- Info -->
              <div style="padding:12px 14px 16px;">
                <div style="font-weight:700;font-size:0.93rem;color:#fff;
                            line-height:1.35;margin-bottom:7px;
                            display:-webkit-box;-webkit-line-clamp:2;
                            -webkit-box-orient:vertical;overflow:hidden;">
                  {m['title']}
                </div>
                <div style="margin-bottom:7px;">{genre_pills}</div>
                <div style="font-size:0.73rem;color:rgba(255,255,255,0.38);
                            line-height:1.55;display:-webkit-box;
                            -webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;">
                  {overview_short}
                </div>
              </div>
            </div>
            """
            with cols[i]:
                st.markdown(card, unsafe_allow_html=True)

        # Footer
        st.markdown("""
        <div style="text-align:center;padding:2rem 0 1rem;font-family:'DM Sans',sans-serif;
                    font-size:0.72rem;letter-spacing:3px;text-transform:uppercase;
                    color:rgba(255,255,255,0.15);">
          Powered by TMDB &nbsp;·&nbsp; Built with Streamlit
        </div>
        """, unsafe_allow_html=True)