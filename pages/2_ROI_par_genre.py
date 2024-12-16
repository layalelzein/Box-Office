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

from sklearn.linear_model import LinearRegression
import numpy as np

st.subheader("Filtre dynamique : ROI par genre")

# Récupérer les années disponibles
all_movies['release_year'] = all_movies['release_year'].astype(int)
historical_years = sorted(all_movies['release_year'].unique())

# Étendre les années jusqu'à 2035
future_years = list(range(2025, 2036))
all_years = historical_years + future_years

# Initialiser un DataFrame pour les prédictions
genre_predictions = pd.DataFrame({'release_year': all_years})

# Prédire le ROI futur par genre
for genre in all_movies['genre'].unique():
    # Extraire les données historiques pour le genre en question
    genre_data = all_movies[all_movies['genre'] == genre].groupby('release_year')['roi'].mean().reset_index()

    # Vérifier s'il y a suffisamment de données pour entraîner un modèle
    if len(genre_data) > 1:
        # Modèle de régression linéaire
        model = LinearRegression()
        X = genre_data['release_year'].values.reshape(-1, 1)
        y = genre_data['roi'].values
        model.fit(X, y)

        # Prédire les ROI pour toutes les années (historiques + futures)
        predicted_roi = model.predict(np.array(all_years).reshape(-1, 1))
        genre_predictions[genre] = predicted_roi
    else:
        # Si pas assez de données, remplir avec NaN
        genre_predictions[genre] = np.nan

# Interface utilisateur
selected_year = st.selectbox("Sélectionnez une année", options=all_years)

# Afficher les ROI pour l'année sélectionnée
if selected_year in genre_predictions['release_year'].values:
    roi_for_year = genre_predictions[genre_predictions['release_year'] == selected_year].set_index('release_year').T
    st.bar_chart(roi_for_year)
else:
    st.write("Aucune donnée disponible pour l'année sélectionnée.")
