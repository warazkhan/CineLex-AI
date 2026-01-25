import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class MovieRecommender:
    def __init__(self, df):
        self.df = df.copy()
        # Precompute movie features
        self.df['features'] = (
            self.df['Genre'].fillna('') + ' ' +
            self.df['Director'].fillna('') + ' ' +
            self.df['Stars'].fillna('')
        )
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.feature_matrix = self.vectorizer.fit_transform(self.df['features'])

    def recommend(self, movie_title, top_n=3):
        if movie_title not in self.df['Title'].values:
            return f"Movie '{movie_title}' not found in database."
        
        idx = self.df[self.df['Title'] == movie_title].index[0]
        sim_scores = cosine_similarity(self.feature_matrix[idx], self.feature_matrix).flatten()
        # Exclude the movie itself
        sim_scores[idx] = 0
        top_indices = sim_scores.argsort()[-top_n:][::-1]
        recommendations = self.df.iloc[top_indices][['Title', 'IMDB Rating', 'Director']].to_dict(orient='records')
        return recommendations
