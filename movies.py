import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import seaborn as sns

API_KEY = '2062561ae58c6832246075755f884642'
BASE_URL = 'https://api.themoviedb.org/3/'

# Fonction pour obtenir les films par genre, avec la gestion des tentatives
def get_movies_by_genre(genre_id, total_pages=5):
    all_movies = []
    for page in range(1, total_pages + 1):
        url = f"{BASE_URL}discover/movie?api_key={API_KEY}&with_genres={genre_id}&page={page}"
        retries = 3
        for attempt in range(retries):
            response = requests.get(url)
            if response.status_code == 200:
                all_movies.extend(response.json()['results'])
                break
            else:
                print(f"Erreur {response.status_code} à la page {page}, tentative {attempt+1}/{retries}")
                time.sleep(2)
    return pd.DataFrame(all_movies)

# Fonction pour obtenir les détails d'un film par son ID
def get_movie_details(movie_id):
    url = f"{BASE_URL}movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
    retries = 3
    for attempt in range(retries):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur {response.status_code} pour l'ID du film {movie_id}, tentative {attempt+1}/{retries}")
            time.sleep(2)
    return None

# Enrichir les films avec le budget, les revenus, le réalisateur, les acteurs, la durée, et la date de sortie
def enrich_movies_with_details(movies_df):
    budgets = []
    revenues = []
    directors = []
    actors = []
    release_dates = []
    
    for movie_id in movies_df['id']:
        details = get_movie_details(movie_id)
        if details:
            budgets.append(details.get('budget', 0))
            revenues.append(details.get('revenue', 0))
            release_dates.append(details.get('release_date', 'Unknown'))  # Date de sortie
            
            # Récupérer le réalisateur
            director = next((crew['name'] for crew in details['credits']['crew'] if crew['job'] == 'Director'), 'Unknown')
            directors.append(director)
            
            # Récupérer les 3 principaux acteurs
            top_actors = [actor['name'] for actor in details['credits']['cast'][:3]] if 'credits' in details and 'cast' in details['credits'] else []
            actors.append(', '.join(top_actors))
        else:
            budgets.append(0)
            revenues.append(0)
            release_dates.append('Unknown')
            directors.append('Unknown')
            actors.append('')
    
    movies_df['budget'] = budgets
    movies_df['revenue'] = revenues
    movies_df['director'] = directors
    movies_df['actors'] = actors
    movies_df['release_date'] = release_dates
    return movies_df

# Convertir la date de sortie en saison
def get_season(release_date):
    if isinstance(release_date, str) and len(release_date.split('-')) == 3:
        try:
            month = int(release_date.split('-')[1])
        except (ValueError, IndexError):
            return 'Unknown'
    else:
        return 'Unknown'
    
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Fall'
    else:
        return 'Unknown'

# Collecte des données pour chaque genre
genres = {
    'Action': 28,
    'Comedy': 35,
    'Drama': 18,
    'Adventure': 12,
    'Horror': 27,
    'Science Fiction': 878,
    'Romance': 10749,
    'Thriller': 53,
    'Animation': 16,
    'Documentary': 99
}

all_movies = pd.DataFrame()

for genre_name, genre_id in genres.items():
    df = get_movies_by_genre(genre_id, total_pages=3)
    df['genre'] = genre_name
    all_movies = pd.concat([all_movies, df])

# Enrichir les films avec des détails supplémentaires
all_movies = enrich_movies_with_details(all_movies)

# Ajouter la saison de sortie
all_movies['season'] = all_movies['release_date'].apply(get_season)

# Nettoyage des données
all_movies = all_movies.dropna(subset=['budget', 'revenue'])
all_movies = all_movies[(all_movies['budget'] > 0) & (all_movies['revenue'] > 0)]

# Calcul du ROI pour chaque film
all_movies['roi'] = (all_movies['revenue'] - all_movies['budget']) / all_movies['budget']

# Nettoyage des données : exclure les films avec des budgets ou des revenus égaux à 0 ou trop faibles
all_movies = all_movies[(all_movies['budget'] > 1000) & (all_movies['revenue'] > 1000)]

# Limiter les ROI à une valeur raisonnable (ex : ROI <= 10000)
all_movies = all_movies[all_movies['roi'] <= 10000]

# Sélection de variables : Encodage des variables catégorielles
label_enc_director = LabelEncoder()
all_movies['director_encoded'] = label_enc_director.fit_transform(all_movies['director'])

label_enc_season = LabelEncoder()
all_movies['season_encoded'] = label_enc_season.fit_transform(all_movies['season'])

# Variables pour la prédiction (budget, directeur, saison)
X = all_movies[['budget', 'director_encoded', 'season_encoded']]

# Target (ROI)
y = all_movies['roi']


# Split des données
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Modèle de régression linéaire
model = LinearRegression()
model.fit(X_train, y_train)

# Prédiction
y_pred = model.predict(X_test)

# Streamlit Dashboard
st.title("Dashboard de rentabilité des films")

# Section 1: Données brutes
st.subheader("Données brutes")
st.write(all_movies[['title', 'genre', 'budget', 'revenue', 'roi', 'director', 'actors', 'release_date', 'season']].head(10))

# Section 2: ROI par genre
st.subheader("ROI moyen par genre")
genre_roi = all_movies.groupby('genre')['roi'].mean().sort_values(ascending=False)
st.dataframe(genre_roi)

# Section 3: Bar chart des genres les plus rentables
st.subheader("Graphique des genres les plus rentables")
plt.figure(figsize=(10, 6))
plt.barh(genre_roi.index, genre_roi.values, color='skyblue')
plt.xlabel('ROI moyen')
plt.ylabel('Genres')
plt.title('Genres les plus rentables')
plt.gca().invert_yaxis()  # Inverser l'axe des y pour avoir le genre le plus rentable en haut
st.pyplot(plt)

# Section 4: Tendances de rentabilité par genre
st.subheader("Tendances de rentabilité par genre")
# Extraire l'année de la date de sortie
all_movies['release_year'] = all_movies['release_date'].apply(lambda x: x.split('-')[0] if isinstance(x, str) and len(x.split('-')) == 3 else 'Unknown')
roi_per_year = all_movies[all_movies['release_year'] != 'Unknown'].groupby(['release_year', 'genre'])['roi'].mean().unstack()
st.line_chart(roi_per_year)

# Section 5: Matrice de corrélation
st.subheader("Corrélation entre les facteurs")
corr_matrix = all_movies[['budget', 'roi', 'director_encoded', 'season_encoded']].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
st.pyplot(plt)

# Section 6: Exploration par budget et genre
st.subheader("Explorez les films par budget et genre")
min_budget = int(all_movies['budget'].min())
max_budget = int(all_movies['budget'].max())
default_budget = min(500000000, max_budget)  # Ajuster la valeur par défaut

user_budget = st.number_input(
    "Entrez le budget du film",
    min_value=min_budget,
    max_value=max_budget,
    value=min_budget
)

selected_genres = st.multiselect(
    "Sélectionnez des genres",
    options=list(genres.keys()),
    default=list(genres.keys())
)

filtered_movies = all_movies[
    (all_movies['budget'] >= user_budget) &
    (all_movies['budget'] <= max_budget) &
    (all_movies['genre'].isin(selected_genres))
]

st.write(filtered_movies[['title', 'genre', 'budget', 'revenue', 'roi']].head(10))

# Recalculer le ROI moyen pour les genres filtrés
filtered_genre_roi = filtered_movies.groupby('genre')['roi'].mean().sort_values(ascending=False)
st.subheader("ROI moyen pour les genres filtrés")
st.dataframe(filtered_genre_roi)

# Section 7: Téléchargement des données filtrées
csv = filtered_movies.to_csv(index=False)
st.download_button(label="Télécharger les données filtrées en CSV", data=csv, mime="text/csv")

# Section 8: Prédiction du ROI basé sur plusieurs caractéristiques
st.subheader("Prédire le ROI en fonction de plusieurs caractéristiques")

user_director = st.selectbox("Sélectionnez un réalisateur", options=label_enc_director.classes_)
user_season = st.selectbox("Sélectionnez une saison", options=label_enc_season.classes_)

# Encodage des entrées utilisateur
try:
    user_director_encoded = label_enc_director.transform([user_director])[0]
except ValueError:
    user_director_encoded = 0  # Valeur par défaut si le réalisateur n'est pas trouvé

try:
    user_season_encoded = label_enc_season.transform([user_season])[0]
except ValueError:
    user_season_encoded = 0  # Valeur par défaut si la saison n'est pas trouvée

# Prédiction
predicted_roi = model.predict([[user_budget, user_director_encoded, user_season_encoded]])[0]
st.write(f"Prédiction du ROI pour un film avec un budget de ${user_budget:,} et réalisé par {user_director}: {predicted_roi:.2f}")

# Section 9: Importance des variables avec RandomForest
st.subheader("Importance des variables")
rf = RandomForestRegressor(random_state=42)
rf.fit(X, y)
feature_importances = pd.Series(rf.feature_importances_, index=X.columns)
st.bar_chart(feature_importances.sort_values(ascending=False))
