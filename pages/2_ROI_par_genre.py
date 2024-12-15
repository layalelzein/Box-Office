from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns

st.title("📊 ROI moyen par genre")

# Charger les données
all_movies = pd.read_csv("data/all_movies_clean.csv")

# Créer la colonne 'release_year' si elle n'existe pas
if 'release_year' not in all_movies.columns:
    all_movies['release_year'] = all_movies['release_date'].apply(
        lambda x: x.split('-')[0] if isinstance(x, str) and len(x.split('-')) == 3 else 'Unknown'
    )

# Filtrer les films ayant une année valide
filtered_movies = all_movies[all_movies['release_year'] != 'Unknown']

# Calcul du ROI par genre
st.subheader("Rentabilité par genre")
genre_roi = all_movies.groupby('genre')['roi'].mean().sort_values(ascending=False)

# Afficher sous forme de graphique interactif
fig = px.bar(
    genre_roi,
    x=genre_roi.index,
    y=genre_roi.values,
    title="Genres les plus rentables",
    labels={'x': 'Genre', 'y': 'ROI moyen'},
    color=genre_roi.index
)
st.plotly_chart(fig)

# Affichage des valeurs
st.dataframe(genre_roi.reset_index().rename(columns={"genre": "Genre", "roi": "ROI moyen"}))

# Évolution du ROI par genre dans le temps
st.subheader("Évolution du ROI par genre dans le temps")

# Calculer le ROI par année et par genre
genre_roi_time = filtered_movies.groupby(['release_year', 'genre'])['roi'].mean().unstack()

# Interface utilisateur pour sélectionner les genres
unique_genres = all_movies['genre'].unique()
selected_genres = st.multiselect(
    "Sélectionnez les genres à visualiser",
    options=unique_genres,
    default=['Action', 'Comedy']
)

# Afficher les données filtrées
if selected_genres:
    filtered_genre_roi_time = genre_roi_time[selected_genres]
    st.line_chart(filtered_genre_roi_time)
else:
    st.warning("Veuillez sélectionner au moins un genre.")

# Filtre dynamique : ROI par genre pour une année spécifique
st.subheader("Filtre dynamique : ROI par genre")
available_years = sorted(filtered_movies['release_year'].unique())
selected_year = st.selectbox("Sélectionnez une année", options=available_years)

# Filtrer les données pour l'année sélectionnée
filtered_data = filtered_movies[filtered_movies['release_year'] == selected_year]

# Calculer le ROI moyen pour chaque genre
roi_by_genre = filtered_data.groupby('genre')['roi'].mean().sort_values(ascending=False)

# Afficher le graphique
st.bar_chart(roi_by_genre)

# Afficher les données
st.dataframe(roi_by_genre.reset_index().rename(columns={"roi": "ROI moyen"}))
