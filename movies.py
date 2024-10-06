import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import time
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Load API key from environment variable
API_KEY = os.getenv('TMDB_API_KEY')

# Base URL for TMDb API
BASE_URL = 'https://api.themoviedb.org/3/'

# Function to get movies by genre, with retry logic for robustness
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
                print(f"Error {response.status_code} on page {page}, attempt {attempt+1}/{retries}")
                time.sleep(2)  # Wait before retrying
    return pd.DataFrame(all_movies)

# Function to get movie details by ID with retry logic
def get_movie_details(movie_id):
    url = f"{BASE_URL}movie/{movie_id}?api_key={API_KEY}"
    retries = 3
    for attempt in range(retries):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code} for movie ID {movie_id}, attempt {attempt+1}/{retries}")
            time.sleep(2)  # Wait before retrying
    return None

# Enrich movies with budget and revenue details
def enrich_movies_with_details(movies_df):
    budgets = []
    revenues = []
    for movie_id in movies_df['id']:
        details = get_movie_details(movie_id)
        if details:
            budgets.append(details.get('budget', 0))
            revenues.append(details.get('revenue', 0))
        else:
            budgets.append(0)
            revenues.append(0)
    
    movies_df['budget'] = budgets
    movies_df['revenue'] = revenues
    return movies_df

# Genres mapping
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
    'Documentary': 99,
    'Family': 10751,
    'Musical': 10402,
    'Mystery': 9648
}

# Collect data for each genre
all_movies = pd.DataFrame()

for genre_name, genre_id in genres.items():
    df = get_movies_by_genre(genre_id, total_pages=3)  # Limited to 3 pages for each genre
    df['genre'] = genre_name
    all_movies = pd.concat([all_movies, df])

# Enrich movies with budget and revenue details
all_movies = enrich_movies_with_details(all_movies)

# Data cleaning: Remove rows where budget or revenue is 0 or missing
all_movies = all_movies.dropna(subset=['budget', 'revenue'])
all_movies = all_movies[(all_movies['budget'] > 0) & (all_movies['revenue'] > 0)]

# Calculate ROI for each movie
all_movies['roi'] = (all_movies['revenue'] - all_movies['budget']) / all_movies['budget']

# Calculate average ROI per genre
genre_roi = all_movies.groupby('genre')['roi'].mean().sort_values(ascending=False)

# Streamlit Dashboard
st.title("Most Profitable Movie Genres - Dashboard")

# Display raw data
st.subheader("Raw Data")
st.write(all_movies[['title', 'genre', 'budget', 'revenue', 'roi']].head(10))

# Display average ROI by genre
st.subheader("Average ROI by Genre")
st.dataframe(genre_roi)

# Bar chart of most profitable genres
st.subheader("Most Profitable Genres Chart")
plt.figure(figsize=(10, 6))
plt.barh(genre_roi.index, genre_roi.values, color='skyblue')
plt.xlabel('Average ROI')
plt.ylabel('Genres')
plt.title('Most Profitable Genres')
st.pyplot(plt)

# Filters to explore data by budget and genre
st.subheader("Explore Data by Budget and Genre")
min_budget = st.slider("Minimum Budget", min_value=int(all_movies['budget'].min()), max_value=int(all_movies['budget'].max()), value=int(all_movies['budget'].min()))
max_budget = st.slider("Maximum Budget", min_value=min_budget, max_value=int(all_movies['budget'].max()), value=int(all_movies['budget'].max()))

# Filter movies by budget
filtered_movies = all_movies[(all_movies['budget'] >= min_budget) & (all_movies['budget'] <= max_budget)]

# Add genre filtering option
selected_genres = st.multiselect("Select Genres", options=list(genres.keys()), default=list(genres.keys()))
filtered_movies = filtered_movies[filtered_movies['genre'].isin(selected_genres)]

# Display filtered movies
st.write(filtered_movies[['title', 'genre', 'budget', 'revenue', 'roi']].head(10))

# Recalculate average ROI for filtered movies
filtered_genre_roi = filtered_movies.groupby('genre')['roi'].mean().sort_values(ascending=False)
st.subheader("Average ROI for Filtered Genres")
st.dataframe(filtered_genre_roi)

# Download filtered data as CSV
csv = filtered_movies.to_csv(index=False)
st.download_button(label="Download Filtered Data as CSV", data=csv, mime="text/csv")

# Train a Linear Regression model to predict ROI based on budget
st.subheader("Predict ROI Based on Budget")
X = all_movies[['budget']]  # Features
y = all_movies['roi']  # Target

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Display model performance metrics
st.write(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.2f}")
st.write(f"R² Score: {r2_score(y_test, y_pred):.2f}")

# Predict ROI based on user input budget
user_budget = st.number_input("Enter a movie budget to predict ROI", min_value=int(all_movies['budget'].min()), max_value=int(all_movies['budget'].max()), value=10000000)
predicted_roi = model.predict([[user_budget]])[0]

st.write(f"Predicted ROI for a movie with a budget of ${user_budget:,}: {predicted_roi:.2f}")
all_movies.to_csv('movies_data.csv', index=False)