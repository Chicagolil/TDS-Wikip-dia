import requests
import pandas as pd
import datetime
import argparse

# récupère les articles les plus consultés
def recuperer_articles_plus_consultes(langue, date, limite=None):
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{langue}/all-access/{date.year}/{date.month:02d}/{date.day:02d}"
    en_tetes = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    reponse = requests.get(url, headers=en_tetes)
    
    if reponse.status_code == 200:
        donnees = reponse.json()
        articles = donnees['items'][0]['articles']
        tableau = pd.DataFrame(articles)
        tableau = tableau[['article', 'views']]  # On garde seulement les colonnes article et vues

        # Limiter le nombre d'articles si une limite est spécifiée
        if limite:
            tableau = tableau.head(limite)
            
        return tableau
    else:
        print(f"Erreur : {reponse.status_code}")
        return None

#récupère le contenu complet d'un article par son titre
def recuperer_contenu_article(langue, titre):
    url = f"https://{langue}.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&titles={titre}&exintro&explaintext"
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
    parser.add_argument('--limite', type=int, help="Nombre maximum d'articles à récupérer par jour.", default=None)

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
    
    # Créer un DataFrame pour accumuler les résultats de tous les jours
    tous_les_articles = pd.DataFrame()

    # Boucle sur chaque jour entre date_debut et date_fin
    date_courante = date_debut
    while date_courante <= date_fin:
        print(f"Récupération des articles pour la date : {date_courante}")
        articles_jour = recuperer_articles_plus_consultes('fr.wikipedia', date_courante, args.limite)
        
        if articles_jour is not None:
            # Récupérer le contenu de chaque article
            articles_jour['contenu'] = articles_jour['article'].apply(lambda titre: recuperer_contenu_article('fr', titre))
            articles_jour['date'] = date_courante  # Ajouter la date à chaque article
            tous_les_articles = pd.concat([tous_les_articles, articles_jour], ignore_index=True)
        
        # Passer au jour suivant
        date_courante += datetime.timedelta(days=1)
    
    # Sauvegarder les articles et leurs contenus dans un fichier JSON au format AUJSON (JSONLines) avec encodage UTF-8
    if not tous_les_articles.empty:
        tous_les_articles.to_json(f'articles_wikipedia_{date_debut}_a_{date_fin}.json', orient='records', lines=True, force_ascii=False)
        print(f"Les données ont été sauvegardées dans 'articles_wikipedia_{date_debut}_a_{date_fin}.json'.")
    else:
        print("Aucune donnée à sauvegarder.")

# Appel de la fonction principale
if __name__ == "__main__":
    principal()
