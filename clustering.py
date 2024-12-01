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
    """
    Retourne les thèmes principaux de chaque cluster.

    :param vecteurs: Matrice TF-IDF.
    :param clusters: Numpy array des identifiants de clusters.
    :param vectorizer: Modèle TF-IDF vectorizer.
    :param top_n: Nombre de termes principaux à extraire.
    :return: Liste de listes, chaque sous-liste contient des tuples (mot, score) pour chaque cluster.
    """
    # Récupérer les noms des mots caractéristiques
    termes = vectorizer.get_feature_names_out()
    
    # Structure pour stocker les mots-clés et leurs scores pour chaque cluster
    themes_principaux = []
    
    # Parcourir chaque cluster pour extraire les mots principaux
    for cluster in np.unique(clusters):
        print(f"\n[DEBUG] Thèmes principaux pour le cluster {cluster}:")
        
        # Obtenir les indices des articles dans ce cluster
        indices_cluster = np.where(clusters == cluster)[0]
        
        # Extraire les vecteurs TF-IDF des articles de ce cluster et calculer la moyenne
        vecteurs_cluster = vecteurs[indices_cluster]
        moyenne_tfidf = np.mean(vecteurs_cluster, axis=0).A1  # Convertir en tableau 1D
        
        # Obtenir les indices des termes les plus importants
        indices_top_termes = moyenne_tfidf.argsort()[::-1][:top_n]
        top_termes = [(termes[i], moyenne_tfidf[i]) for i in indices_top_termes]
        
        # Ajouter les thèmes principaux à la liste
        themes_principaux.append(top_termes)
        
        print(", ".join([terme for terme, _ in top_termes]))
    
    return themes_principaux

def afficher_themes_principaux_par_distance(vecteurs, clusters, vectorizer, top_n=10):
    """
    Retourne les thèmes principaux de chaque cluster en se basant sur la distance au centre du cluster.

    :param vecteurs: Matrice TF-IDF.
    :param clusters: Numpy array des identifiants de clusters.
    :param vectorizer: Modèle TF-IDF vectorizer.
    :param top_n: Nombre de termes principaux à extraire.
    :return: Liste de listes, chaque sous-liste contient des tuples (mot, distance) pour chaque cluster.
    """
    termes = vectorizer.get_feature_names_out()
    themes_principaux = []

    for cluster in np.unique(clusters):
        print(f"\n[DEBUG] Thèmes principaux pour le cluster {cluster} (par distance au centre) :")
        
        indices_cluster = np.where(clusters == cluster)[0]
        vecteurs_cluster = vecteurs[indices_cluster]
        
        # Calculer le centre du cluster
        centre_cluster = vecteurs_cluster.mean(axis=0).A1
        
        # Calculer la distance de chaque mot par rapport au centre
        distances = np.abs(centre_cluster)
        
        # Sélectionner les mots les plus proches du centre
        indices_top_termes = distances.argsort()[::-1][:top_n]
        top_termes = [(termes[i], distances[i]) for i in indices_top_termes]
        
        themes_principaux.append(top_termes)
        print(", ".join([terme for terme, _ in top_termes]))

    return themes_principaux
