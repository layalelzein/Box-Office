import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Remplace par ta clé API TMDb
API_KEY = '2062561ae58c6832246075755f884642'
BASE_URL = 'https://api.themoviedb.org/3/'

# Fonction pour obtenir les films par genre
def get_movies_by_genre(genre_id, total_pages=5):
    all_movies = []
    for page in range(1, total_pages + 1):
        url = f"{BASE_URL}discover/movie?api_key={API_KEY}&with_genres={genre_id}&page={page}"
        response = requests.get(url)
        if response.status_code == 200:
            all_movies.extend(response.json()['results'])
        else:
            print(f"Erreur {response.status_code}")
    return pd.DataFrame(all_movies)

# Fonction pour obtenir les détails d'un film avec son ID (pour récupérer budget et revenu)
def get_movie_details(movie_id):
    url = f"{BASE_URL}movie/{movie_id}?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code} pour le film ID {movie_id}")
        return None

# Ajouter une boucle pour enrichir les films avec les détails du budget et des revenus
def enrich_movies_with_details(movies_df):
    budgets = []
    revenues = []
    for movie_id in movies_df['id']:
        details = get_movie_details(movie_id)
        if details:
            budgets.append(details.get('budget', 0))  # Si pas disponible, on met 0
            revenues.append(details.get('revenue', 0))  # Idem pour les revenus
        else:
            budgets.append(0)
            revenues.append(0)
    
    movies_df['budget'] = budgets
    movies_df['revenue'] = revenues
    return movies_df

# Collecte des données pour plusieurs genres
genres = {
    'Action': 28,
    'Comedy': 35,
    'Drama': 18,
    'Adventure': 12
}

# Initialisation des DataFrames pour chaque genre
all_movies = pd.DataFrame()

for genre_name, genre_id in genres.items():
    df = get_movies_by_genre(genre_id, total_pages=3)  # Limité à 3 pages pour chaque genre
    df['genre'] = genre_name
    all_movies = pd.concat([all_movies, df])

# Enrichir les films avec les détails du budget et des revenus
all_movies = enrich_movies_with_details(all_movies)

# Nettoyage des données
# Supprimer les lignes où 'budget' ou 'revenue' est manquant ou égal à 0
all_movies = all_movies.dropna(subset=['budget', 'revenue'])
all_movies = all_movies[(all_movies['budget'] > 0) & (all_movies['revenue'] > 0)]

# Calculer le ROI pour chaque film
all_movies['roi'] = (all_movies['revenue'] - all_movies['budget']) / all_movies['budget']

# Calculer la moyenne du ROI par genre
genre_roi = all_movies.groupby('genre')['roi'].mean().sort_values(ascending=False)

# Création du tableau de bord avec Streamlit
st.title("Genres les plus rentables - Tableau de bord")

# Afficher les données brutes
st.subheader("Données brutes")
st.write(all_movies[['title', 'genre', 'budget', 'revenue', 'roi']].head(10))

# Afficher le ROI moyen par genre
st.subheader("ROI moyen par genre")
st.dataframe(genre_roi)

# Graphique des genres les plus rentables
st.subheader("Graphique des genres les plus rentables")
plt.figure(figsize=(10,6))
plt.barh(genre_roi.index, genre_roi.values, color='skyblue')
plt.xlabel('ROI moyen')
plt.ylabel('Genres')
plt.title('Genres les plus rentables')
st.pyplot(plt)

# Ajout d'une projection (exemple basique)
st.subheader("Projection de la rentabilité future (exemple)")
st.write("**Note :** Ceci est une projection hypothétique basée sur les données actuelles.")
projected_genres = genre_roi * 1.1  # Exemple de projection : augmentation de 10%
st.write(projected_genres)

