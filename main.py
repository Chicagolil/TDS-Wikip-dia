import requests
import pandas as pd
import datetime
import argparse
from collections import defaultdict
from pretraitement import nettoyer_texte
from clustering import vectoriser_articles, clustering_kmeans,afficher_themes_principaux

# récupère les articles les plus consultés
def recuperer_articles_plus_consultes(langue, date):
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{langue}/all-access/{date.year}/{date.month:02d}/{date.day:02d}"
    en_tetes = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    reponse = requests.get(url, headers=en_tetes)
    
    if reponse.status_code == 200:
        donnees = reponse.json()
        articles = donnees['items'][0]['articles']
        tableau = pd.DataFrame(articles)
        return tableau[['article', 'views']]  # On garde seulement les colonnes article et vues
    else:
        print(f"Erreur : {reponse.status_code}")
        return None




#récupère le contenu complet d'un article par son titre
def recuperer_contenu_article(langue, titre):
    url = f"https://{langue}.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&titles={titre}&explaintext"
    en_tetes = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    reponse = requests.get(url, headers=en_tetes)
    
    if reponse.status_code == 200:
        donnees = reponse.json()
        pages = donnees['query']['pages']
        page = next(iter(pages.values()))  # Il n'y a qu'une seule page donc on récupère son contenu
        return page.get('extract', 'Contenu non disponible')  # Récupérer l'extrait complet
    else:
        print(f"Erreur lors de la récupération de l'article '{titre}' : {reponse.status_code}")
        return None

def principal():
    # récupérer les dates et la limite d'articles
    parser = argparse.ArgumentParser(description='Obtenez les articles les plus consultés sur Wikipédia pour une période donnée.')
    parser.add_argument('date_debut', type=str, help="La date de début (ou la seule date) au format AAAA-MM-JJ (ex: 2024-10-01)")
    parser.add_argument('--date_fin', type=str, help="La date de fin au format AAAA-MM-JJ (ex: 2024-10-07). Si non spécifiée, la date de début sera utilisée.", default=None)
    parser.add_argument('--limite', type=int, help="Nombre maximum d'articles à afficher à la fin.", default=None)

    args = parser.parse_args()  # Récupérer les arguments de la ligne de commande
    
    # Convertir les dates en objets datetime.date
    try:
        date_debut = datetime.datetime.strptime(args.date_debut, '%Y-%m-%d').date()
        if args.date_fin:
            date_fin = datetime.datetime.strptime(args.date_fin, '%Y-%m-%d').date()
        else:
            date_fin = date_debut  # Si aucune date de fin n'est spécifiée, utiliser la date de début
    except ValueError:
        print("Erreur : Les dates doivent être au format AAAA-MM-JJ (ex: 2024-10-01).")
        return
    
    # Vérifier que la date de début est avant la date de fin
    if date_debut > date_fin:
        print("Erreur : La date de début doit être antérieure ou égale à la date de fin.")
        return
    
    # Dictionnaire pour accumuler les vues par article sur toute la période
    vues_par_article = defaultdict(int)

    # Boucle sur chaque jour entre date_debut et date_fin
    date_courante = date_debut
    while date_courante <= date_fin:
        print(f"Récupération des articles pour la date : {date_courante}")
        articles_jour = recuperer_articles_plus_consultes('fr.wikipedia', date_courante)
        
        if articles_jour is not None:
            for _, row in articles_jour.iterrows():
                titre = row['article']
                vues = row['views']
                vues_par_article[titre] += vues  # Ajouter les vues de l'article à son total
        
        # Passer au jour suivant
        date_courante += datetime.timedelta(days=1)
    
    # Convertir le dictionnaire en DataFrame et trier par le nombre total de vues
    tableau_final = pd.DataFrame(list(vues_par_article.items()), columns=['article', 'views'])
    tableau_final = tableau_final.sort_values(by='views', ascending=False).reset_index(drop=True)
    
    # Limiter le nombre d'articles si une limite est spécifiée
    if args.limite:
        tableau_final = tableau_final.head(args.limite)
    
    # Récupérer le contenu de chaque article dans la limite
    tableau_final['contenu'] = tableau_final['article'].apply(lambda titre: recuperer_contenu_article('fr', titre))
    tableau_final['contenu_nettoye'] = tableau_final['contenu'].apply(nettoyer_texte)

    # Étape de vectorisation
    vecteurs, vectorizer = vectoriser_articles(tableau_final['contenu_nettoye'])
    print("Vecteurisation terminée. Dimensions des vecteurs :", vecteurs.shape)



    # Clustering
    clusters, kmeans = clustering_kmeans(vecteurs, n_clusters=5)
    tableau_final['cluster'] = clusters

    # Afficher les thèmes principaux de chaque cluster
    afficher_themes_principaux(vecteurs, clusters, vectorizer, top_n=10)

    # Sauvegarder les articles et leurs contenus dans un fichier JSON
    if not tableau_final.empty:
        tableau_final.to_json(f'articles_wikipedia_{date_debut}_a_{date_fin}.json', orient='records', lines=True, force_ascii=False)
        print(f"Les données ont été sauvegardées dans 'articles_wikipedia_{date_debut}_a_{date_fin}.json'.")
    else:
        print("Aucune donnée à sauvegarder.")

# Appel de la fonction principale
if __name__ == "__main__":
    principal()
