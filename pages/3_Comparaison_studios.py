import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🏢 Comparaison de la rentabilité par studio")

# Charger les données
all_movies = pd.read_csv("data/all_movies_clean.csv")

# Calcul du ROI moyen par studio
studio_roi = all_movies.groupby('studio')['roi'].mean().reset_index()

# Trier et afficher les 10 meilleurs studios
top_studios = studio_roi.sort_values(by='roi', ascending=False).head(10)
st.subheader("Top 10 des studios les plus rentables")
st.dataframe(top_studios)

# Visualisation avec Plotly
fig = px.bar(top_studios, x="studio", y="roi", title="Top 10 des studios par ROI", labels={"studio": "Studio", "roi": "ROI moyen"})
st.plotly_chart(fig)

# Exploration d'un studio spécifique
st.subheader("Performance par genre pour un studio sélectionné")
selected_studio = st.selectbox("Choisissez un studio", options=all_movies['studio'].unique())
studio_data = all_movies[all_movies['studio'] == selected_studio].groupby('genre')['roi'].mean().reset_index()
fig2 = px.bar(studio_data, x="genre", y="roi", title=f"Performance par genre pour {selected_studio}")
st.plotly_chart(fig2)
