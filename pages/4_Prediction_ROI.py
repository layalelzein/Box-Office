import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib

st.title("🤖 Prédiction de la rentabilité des films")

# Charger les données et modèles pré-entrainés
all_movies = pd.read_csv("data/all_movies_clean.csv")
model = joblib.load("data/roi_prediction_model.pkl")
label_enc_director = joblib.load("data/director_encoder.pkl")
label_enc_season = joblib.load("data/season_encoder.pkl")
label_enc_genre = joblib.load("data/genre_encoder.pkl")
label_enc_studio = joblib.load("data/studio_encoder.pkl")
label_enc_actor = joblib.load("data/actors_encoder.pkl")

# Interface utilisateur pour la prédiction
st.header("Prédiction simple")
user_budget = st.number_input("Entrez le budget du film (USD)", min_value=1000, value=10000000, step=1000000)
user_director = st.selectbox("Choisissez un réalisateur", options=label_enc_director.classes_)
user_season = st.selectbox("Choisissez une saison", options=label_enc_season.classes_)
user_genre = st.selectbox("Choisissez un genre", options=label_enc_genre.classes_)
user_studio = st.selectbox("Choisissez un studio", options=label_enc_studio.classes_)
user_actor = st.selectbox("Choisissez un acteur principal", options=label_enc_actor.classes_)

# Encodage des choix
director_encoded = label_enc_director.transform([user_director])[0]
season_encoded = label_enc_season.transform([user_season])[0]
genre_encoded = label_enc_genre.transform([user_genre])[0]
studio_encoded = label_enc_studio.transform([user_studio])[0]
actor_encoded = label_enc_actor.transform([user_actor])[0]

# Prédiction
predicted_roi = model.predict([[user_budget, director_encoded, season_encoded, genre_encoded, studio_encoded, actor_encoded]])[0]
st.subheader(f"Prédiction du ROI : {predicted_roi:.2f}")

# Top réalisateurs
st.header("Top réalisateurs")
top_directors = all_movies.groupby('director')['roi'].mean().sort_values(ascending=False).head(10)
st.dataframe(top_directors)

# Impact du budget sur le ROI pour un acteur sélectionné
st.header("Impact du budget sur le ROI (par acteur)")

# Sélection d'un acteur pour visualiser l'impact
selected_actor = st.selectbox("Choisissez un acteur principal pour visualiser l'impact du budget", options=label_enc_actor.classes_)
selected_actor_encoded = label_enc_actor.transform([selected_actor])[0]

# Générer une plage de budgets
budgets = range(1000000, 500000001, 10000000)  # Plage de budgets (1M à 500M)

# Calculer le ROI prédit pour chaque budget
predicted_rois_actor = [
    model.predict([[budget, director_encoded, season_encoded, genre_encoded, studio_encoded, selected_actor_encoded]])[0]
    for budget in budgets
]

# Graphique interactif
fig_actor = px.line(
    x=budgets,
    y=predicted_rois_actor,
    title=f"Impact du budget sur le ROI pour {selected_actor}",
    labels={"x": "Budget (USD)", "y": "Predicted ROI"},
    line_shape="linear",
)

st.plotly_chart(fig_actor)

# Résumé des résultats
st.subheader(f"Résumé des résultats pour {selected_actor}")
st.markdown(
    f"""
    - **Acteur sélectionné :** {selected_actor}
    - **Budget minimum :** {min(budgets):,} USD
    - **Budget maximum :** {max(budgets):,} USD
    - **ROI maximum prédit :** {max(predicted_rois_actor):.2f}
    - **ROI minimum prédit :** {min(predicted_rois_actor):.2f}
    """
)
