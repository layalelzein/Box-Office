import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 ROI moyen par genre")

# Charger les données
all_movies = pd.read_csv("data/all_movies_clean.csv")

# Calcul du ROI par genre
genre_roi = all_movies.groupby('genre')['roi'].mean().sort_values(ascending=False)

# Afficher sous forme de graphique interactif
st.subheader("Rentabilité par genre")
fig = px.bar(genre_roi, x=genre_roi.index, y=genre_roi.values, title="Genres les plus rentables", labels={'x': 'Genre', 'y': 'ROI moyen'})
st.plotly_chart(fig)

# Affichage des valeurs
st.dataframe(genre_roi.reset_index().rename(columns={"genre": "Genre", "roi": "ROI moyen"}))
