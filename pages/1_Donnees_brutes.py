import streamlit as st
import pandas as pd

st.title("📄 Données brutes des films")

# Charger les données pré-nettoyées
all_movies = pd.read_csv("data/all_movies_clean.csv")

# Affichage des données brutes
st.write("Voici un aperçu des films collectés :")
# Afficher uniquement certaines colonnes
columns_to_display = ['title', 'genre', 'budget', 'revenue', 'roi', 'release_date', 'studio']
st.dataframe(all_movies[columns_to_display].head(10))

# Option pour télécharger les données complètes
st.subheader("Télécharger les données complètes")
csv = all_movies.to_csv(index=False)
st.download_button(label="Télécharger les données en CSV", data=csv, mime="text/csv")
