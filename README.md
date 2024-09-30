D'accord, voici le contenu complet en **Markdown** avec la section qui continue après "Accédez au répertoire du projet" :

```markdown
# Box Office ROI Predictor

Ce projet est un système prédictif de rentabilité des films par genre. Il collecte des données sur les films via l'API de TMDb, calcule le retour sur investissement (ROI) pour chaque film, et visualise les genres les plus rentables dans un tableau de bord interactif créé avec **Streamlit**.

## Fonctionnalités

- **Collecte des données** : Utilisation de l'API de The Movie Database (TMDb) pour récupérer des informations sur les films (genre, budget, revenus, etc.).
- **Calcul du ROI** : Calcul du Retour sur Investissement (ROI) pour chaque film.
- **Tableau de bord interactif** : Visualisation des genres les plus rentables avec un graphique et une table des données brutes.
- **Projection** : Projection hypothétique de la rentabilité future par genre.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants :

- Python 3.x
- Une clé API TMDb. [Inscrivez-vous ici](https://www.themoviedb.org/) pour obtenir une clé API.

## Installation

1. Clonez le dépôt dans votre répertoire local :

   ```bash
   git clone https://github.com/votre-utilisateur/box-office-roi-predictor.git
   ```

2. Accédez au répertoire du projet :

   ```bash
   cd box-office-roi-predictor
   ```

3. Créez un environnement virtuel :

   ```bash
   python3 -m venv venv
   ```

4. Activez l'environnement virtuel :

   - Sur macOS/Linux :
     ```bash
     source venv/bin/activate
     ```
   - Sur Windows :
     ```bash
     venv\Scripts\activate
     ```

5. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Ajoutez votre clé API TMDb dans le fichier Python (`movies.py`) à la variable `API_KEY` :

   ```python
   API_KEY = 'votre_clé_api_tmdb'
   ```

## Exécution du projet

Pour lancer le tableau de bord avec **Streamlit**, exécutez la commande suivante :

```bash
streamlit run movies.py
```

Le tableau de bord s'ouvrira automatiquement dans votre navigateur.

## Aperçu

- **Genres les plus rentables** : Visualisez les genres les plus rentables avec un graphique à barres.
- **Projection hypothétique** : Une projection de la rentabilité future basée sur les données actuelles.

## Dépendances

Les principales bibliothèques utilisées dans ce projet sont :

- `requests` : Pour faire des requêtes à l'API TMDb.
- `pandas` : Pour manipuler et analyser les données.
- `matplotlib` : Pour la visualisation des données.
- `streamlit` : Pour créer le tableau de bord interactif.

## Auteurs

- Layal Elzein
- Léa Nassar

