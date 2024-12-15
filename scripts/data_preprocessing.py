import requests
import pandas as pd
import time
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

API_KEY = '2062561ae58c6832246075755f884642'
BASE_URL = 'https://api.themoviedb.org/3/'

# Fonction pour obtenir les films par genre
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
            time.sleep(2)
    return pd.DataFrame(all_movies)

# Fonction pour obtenir les détails d'un film par ID
def get_movie_details(movie_id):
    url = f"{BASE_URL}movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
    retries = 3
    for attempt in range(retries):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        time.sleep(2)
    return None

def enrich_movies_with_details(movies_df):
    budgets, revenues, directors, actors, release_dates, studios = [], [], [], [], [], []

    for movie_id in movies_df['id']:
        details = get_movie_details(movie_id)
        if details:
            budgets.append(details.get('budget', 0))
            revenues.append(details.get('revenue', 0))
            release_dates.append(details.get('release_date', 'Unknown'))

            # Récupérer le réalisateur
            director = next((crew['name'] for crew in details['credits']['crew'] if crew['job'] == 'Director'), 'Unknown')
            directors.append(director)

            # Récupérer le principal acteur
            if 'credits' in details and 'cast' in details['credits'] and details['credits']['cast']:
                main_actor = details['credits']['cast'][0]['name']  # Prendre le premier acteur uniquement
            else:
                main_actor = 'Unknown'
            actors.append(main_actor)


            # Récupérer le studio principal avec gestion des cas vides
            production_companies = details.get('production_companies', [])
            studio = production_companies[0]['name'] if production_companies else 'Unknown'
            studios.append(studio)
        else:
            budgets.append(0), revenues.append(0), directors.append('Unknown')
            studios.append('Unknown'), release_dates.append('Unknown'), actors.append('')

    movies_df['budget'], movies_df['revenue'], movies_df['director'] = budgets, revenues, directors
    movies_df['actors'], movies_df['release_date'], movies_df['studio'] = actors, release_dates, studios
    return movies_df


def get_season(release_date):
    if isinstance(release_date, str) and len(release_date.split('-')) == 3:
        month = int(release_date.split('-')[1])
        return ['Winter', 'Spring', 'Summer', 'Fall'][(month-1)//3]
    return 'Unknown'

# Collecter les données
genres = {'Action': 28, 'Comedy': 35, 'Drama': 18, 'Adventure': 12, 'Horror': 27, 'Science Fiction': 878, 'Romance': 10749, 'Thriller': 53, 'Animation': 16, 'Documentary': 99}
all_movies = pd.DataFrame()

for genre_name, genre_id in genres.items():
    df = get_movies_by_genre(genre_id, total_pages=3)
    df['genre'] = genre_name
    all_movies = pd.concat([all_movies, df])

all_movies = enrich_movies_with_details(all_movies)
all_movies['season'] = all_movies['release_date'].apply(get_season)
all_movies['roi'] = (all_movies['revenue'] - all_movies['budget']) / all_movies['budget']

# Nettoyage des données
all_movies = all_movies[(all_movies['budget'] > 1000) & (all_movies['revenue'] > 1000)]
all_movies = all_movies[all_movies['roi'] <= 10000]

# Encodage des colonnes catégorielles
label_enc_director = LabelEncoder()
all_movies['director_encoded'] = label_enc_director.fit_transform(all_movies['director'])
joblib.dump(label_enc_director, 'data/director_encoder.pkl')

label_enc_season = LabelEncoder()
all_movies['season_encoded'] = label_enc_season.fit_transform(all_movies['season'])
joblib.dump(label_enc_season, 'data/season_encoder.pkl')

label_enc_actors = LabelEncoder()
all_movies['actors_encoded'] = label_enc_actors.fit_transform(all_movies['actors'])
joblib.dump(label_enc_actors, 'data/actors_encoder.pkl')

label_enc_studio = LabelEncoder()
all_movies['studio_encoded'] = label_enc_studio.fit_transform(all_movies['studio'])
joblib.dump(label_enc_studio, 'data/studio_encoder.pkl')

label_enc_genre = LabelEncoder()
all_movies['genre_encoded'] = label_enc_genre.fit_transform(all_movies['genre'])
joblib.dump(label_enc_genre, 'data/genre_encoder.pkl')

# Entraînement du modèle
X = all_movies[['budget', 'director_encoded', 'season_encoded', 'actors_encoded', 'studio_encoded', 'genre_encoded']]
y = all_movies['roi']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)
print(f"Mean Squared Error: {mean_squared_error(y_test, model.predict(X_test)):.2f}")
print(f"R² Score: {r2_score(y_test, model.predict(X_test)):.2f}")

# Sauvegarder le modèle et les données
joblib.dump(model, "data/roi_prediction_model.pkl")
all_movies.to_csv("data/all_movies_clean.csv", index=False)
print("✅ Données sauvegardées dans all_movies_clean.csv et modèle dans roi_prediction_model.pkl")
