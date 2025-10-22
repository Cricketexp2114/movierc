import pickle
import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import gdown
import os

# ------------------- Helper Functions -------------------

def fetch_poster(movie_id):
    """Fetches the movie poster URL from TMDB API."""
    api_key = st.secrets["tmdb_api_key"]
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        data = requests.get(url)
        data.raise_for_status()
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"


def recommend(movie):
    """Recommends 5 similar movies."""
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset. Please select another one.")
        return [], [], [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_years = []
    recommended_movie_ratings = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_years.append(movies.iloc[i[0]].year)
        recommended_movie_ratings.append(movies.iloc[i[0]].vote_average)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings


# ------------------- Streamlit Layout -------------------

st.set_page_config(layout="wide")
st.header('🎬 Movie Recommender System')

# ------------------- Load Files -------------------

# Load movie_dict.pkl locally (under 25 MB)
movies_dict = pickle.load(open('artifacts/movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Google Drive file ID for similarity
# Google Drive file ID for similarity.pkl
file_id = "1c2RzpfjydBFxudkEjwHW1auW2JCHhQVV"
output_file = "similarity.pkl"

# Download using gdown if not already downloaded
if not os.path.exists(output_file):
    with st.spinner('📥 Downloading similarity model from Google Drive...'):
        gdown.download(f"https://drive.google.com/uc?id={file_id}", output_file, quiet=False)

# Load similarity.pkl
with open(output_file, "rb") as f:
    similarity = pickle.load(f)

# ------------------- Movie Selection -------------------

movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    with st.spinner('🔍 Finding recommendations...'):
        recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings = recommend(selected_movie)

    if recommended_movie_names:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])
                year = recommended_movie_years[i]
                if pd.notna(year):
                    st.caption(f"📅 Year: {int(year)}")
                else:
                    st.caption("📅 Year: N/A")
                rating = recommended_movie_ratings[i]
                st.caption(f"⭐ Rating: {rating:.1f}")
