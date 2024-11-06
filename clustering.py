from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt

# Vecteurisation des articles avec TF-IDF
def vectoriser_articles(contenus, max_features=1000):
    vectorizer = TfidfVectorizer(max_features=max_features)
    vecteurs = vectorizer.fit_transform(contenus)
    return vecteurs, vectorizer

# Clustering des articles avec K-Means
def clustering_kmeans(vecteurs, n_clusters=5):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(vecteurs)
    return clusters, kmeans




import numpy as np

def afficher_themes_principaux(vecteurs, clusters, vectorizer, top_n=10):
    # Récupérer les noms des mots caractéristiques
    termes = vectorizer.get_feature_names_out()
    
    # Parcourir chaque cluster pour afficher les mots principaux
    for cluster in np.unique(clusters):
        print(f"\nThèmes principaux pour le cluster {cluster}:")
        
        # Obtenir les indices des articles dans ce cluster
        indices_cluster = np.where(clusters == cluster)[0]
        
        # Extraire les vecteurs TF-IDF des articles de ce cluster et calculer la moyenne
        vecteurs_cluster = vecteurs[indices_cluster]
        moyenne_tfidf = np.mean(vecteurs_cluster, axis=0).A1  # Convertir en tableau 1D
        
        # Obtenir les indices des termes les plus importants
        indices_top_termes = moyenne_tfidf.argsort()[::-1][:top_n]
        top_termes = [termes[i] for i in indices_top_termes]
        
        print(", ".join(top_termes))