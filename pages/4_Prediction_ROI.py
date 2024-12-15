import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib

st.title("🤖 Prédiction de la rentabilité des films")

# Charger les données et modèles pré-entrainés
all_movies = pd.read_csv("data/all_movies_clean.csv")
model = joblib.load("data/roi_prediction_model.pkl")
label_enc_director = joblib.load("data/director_encoder.pkl")
label_enc_season = joblib.load("data/season_encoder.pkl")

# Interface utilisateur pour la prédiction
user_budget = st.number_input("Entrez le budget du film", min_value=1000, value=10000000, step=1000000)
user_director = st.selectbox("Sélectionnez un réalisateur", options=label_enc_director.classes_)
user_season = st.selectbox("Sélectionnez une saison", options=label_enc_season.classes_)

# Encodage
director_encoded = label_enc_director.transform([user_director])[0]
season_encoded = label_enc_season.transform([user_season])[0]

# Prédiction
predicted_roi = model.predict([[user_budget, director_encoded, season_encoded]])[0]
st.subheader(f"Prédiction du ROI : {predicted_roi:.2f}")
