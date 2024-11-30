import requests
import pandas as pd
import datetime
import argparse
from collections import defaultdict
from pretraitement import nettoyer_texte
from clustering import vectoriser_articles, clustering_kmeans,afficher_themes_principaux
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import ttk

def recuperer_articles_plus_consultes(langue, date):
    print(f"[DEBUG] Récupération des articles les plus consultés pour la date : {date}")
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{langue}/all-access/{date.year}/{date.month:02d}/{date.day:02d}"
    en_tetes = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    reponse = requests.get(url, headers=en_tetes)
    
    if reponse.status_code == 200:
        donnees = reponse.json()
        articles = donnees['items'][0]['articles']
        print(f"[DEBUG] Nombre d'articles récupérés : {len(articles)}")

        # Liste des articles à exclure
        articles_a_exclure = ["Spécial:Recherche", "Main_Page", "Accueil", "Wikipedia:Accueil"]

        # Filtrer les articles à exclure
        articles_filtrés = [article for article in articles if article['article'] not in articles_a_exclure]
        print(f"[DEBUG] Nombre d'articles après filtrage : {len(articles_filtrés)}")

        tableau = pd.DataFrame(articles_filtrés)
        return tableau[['article', 'views']]  # On garde seulement les colonnes article et vues
    else:
        print(f"Erreur : {reponse.status_code}")
        return None

def recuperer_contenu_article(langue, titre):
    print(f"[DEBUG] Récupération du contenu de l'article : {titre}")
    url = f"https://{langue}.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&titles={titre}&explaintext"
    en_tetes = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    reponse = requests.get(url, headers=en_tetes)
    
    if reponse.status_code == 200:
        donnees = reponse.json()
        pages = donnees['query']['pages']
        page = next(iter(pages.values()))  # Il n'y a qu'une seule page donc on récupère son contenu
        print(f"[DEBUG] Contenu récupéré pour l'article '{titre}' : {len(page.get('extract', 'Contenu non disponible'))} caractères")
        return page.get('extract', 'Contenu non disponible')  # Récupérer l'extrait complet
    else:
        print(f"Erreur lors de la récupération de l'article '{titre}' : {reponse.status_code}")
        return None

def lancer_programme(date_debut, date_fin, limite):
    print(f"[DEBUG] Lancement du programme avec date_debut={date_debut}, date_fin={date_fin}, limite={limite}")
    # Convertir les dates en objets datetime.date
    try:
        date_debut = datetime.datetime.strptime(date_debut, '%Y-%m-%d').date()
        if date_fin:
            date_fin = datetime.datetime.strptime(date_fin, '%Y-%m-%d').date()
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
        print(f"[DEBUG] Récupération des articles pour la date : {date_courante}")
        articles_jour = recuperer_articles_plus_consultes('fr.wikipedia', date_courante)
        
        if articles_jour is not None:
            for _, row in articles_jour.iterrows():
                titre = row['article']
                vues = row['views']
                vues_par_article[titre] += vues  # Ajouter les vues de l'article à son total
                print(f"[DEBUG] Article '{titre}' mis à jour avec {vues} vues. Total : {vues_par_article[titre]}")
        
        # Passer au jour suivant
        date_courante += datetime.timedelta(days=1)
    
    # Convertir le dictionnaire en DataFrame et trier par le nombre total de vues
    print("[DEBUG] Conversion des vues en DataFrame")
    tableau_final = pd.DataFrame(list(vues_par_article.items()), columns=['article', 'views'])
    tableau_final = tableau_final.sort_values(by='views', ascending=False).reset_index(drop=True)
    
    # Limiter le nombre d'articles si une limite est spécifiée
    if limite:
        tableau_final = tableau_final.head(limite)
    
    # Déterminer le nombre de clusters en fonction du nombre d'articles
    n_clusters = max(3, min(len(tableau_final) // 5, 10))
    print(f"[DEBUG] Nombre de clusters déterminé : {n_clusters}")
    
    # Récupérer le contenu de chaque article dans la limite
    print("[DEBUG] Récupération du contenu des articles sélectionnés")
    tableau_final['contenu'] = tableau_final['article'].apply(lambda titre: recuperer_contenu_article('fr', titre))
    tableau_final['contenu_nettoye'] = tableau_final['contenu'].apply(nettoyer_texte)

    # Étape de vectorisation
    print("[DEBUG] Début de la vectorisation des articles")
    vecteurs, vectorizer = vectoriser_articles(tableau_final['contenu_nettoye'])
    print("Vecteurisation terminée. Dimensions des vecteurs :", vecteurs.shape)

    # Clustering
    print("[DEBUG] Début du clustering des articles")
    clusters, kmeans = clustering_kmeans(vecteurs, n_clusters=n_clusters)
    tableau_final['cluster'] = clusters
    print("[DEBUG] Clustering terminé")

    # Afficher les thèmes principaux de chaque cluster
    print("[DEBUG] Affichage des thèmes principaux par cluster")
    afficher_themes_principaux(vecteurs, clusters, vectorizer, top_n=10)

    # Sauvegarder les articles et leurs contenus dans un fichier JSON
    if not tableau_final.empty:
        fichier_sauvegarde = f'articles_wikipedia_{date_debut}_a_{date_fin}.json'
        tableau_final.to_json(fichier_sauvegarde, orient='records', lines=True, force_ascii=False)
        print(f"Les données ont été sauvegardées dans '{fichier_sauvegarde}'.")
    else:
        print("Aucune donnée à sauvegarder.")

def interface_graphique():
    def on_valider():
        date_debut = entree_date_debut.get()
        date_fin = entree_date_fin.get()
        limite = entree_limite.get()
        
        if not date_debut:
            messagebox.showerror("Erreur", "Veuillez entrer une date de début.")
            return
        
        try:
            limite = int(limite)
        except ValueError:
            limite = None
        
        print(f"[DEBUG] Paramètres saisis : date_debut={date_debut}, date_fin={date_fin}, limite={limite}")
        lancer_programme(date_debut, date_fin, limite)

    # Créer la fenêtre principale
    fenetre = tk.Tk()
    fenetre.title("Paramètres de récupération des articles Wikipédia")
    fenetre.geometry("400x350")
    fenetre.configure(bg='#ffffff')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', font=('Helvetica', 12), background='#ffffff', foreground='#000000')
    style.configure('TButton', font=('Helvetica', 12), background='#000000', foreground='#ffffff')
    style.configure('TEntry', font=('Helvetica', 12))

    # Ajouter les champs de saisie
    label_debut = ttk.Label(fenetre, text="Date de début (AAAA-MM-JJ) :")
    label_debut.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
    entree_date_debut = DateEntry(fenetre, width=17, background='#000000', foreground='white', borderwidth=2, date_pattern='yyyy-MM-dd', font=('Helvetica', 12), selectbackground='#000000', selectforeground='white')
    entree_date_debut.grid(row=0, column=1, padx=10, pady=10)

    label_fin = ttk.Label(fenetre, text="Date de fin (AAAA-MM-JJ) :")
    label_fin.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
    entree_date_fin = DateEntry(fenetre, width=17, background='#000000', foreground='white', borderwidth=2, date_pattern='yyyy-MM-dd', font=('Helvetica', 12), selectbackground='#000000', selectforeground='white')
    entree_date_fin.grid(row=1, column=1, padx=10, pady=10)

    label_limite = ttk.Label(fenetre, text="Nombre maximum d'articles :")
    label_limite.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
    entree_limite = ttk.Entry(fenetre, width=20)
    entree_limite.grid(row=2, column=1, padx=10, pady=10)

    # Ajouter le bouton de validation
    bouton_valider = ttk.Button(fenetre, text="Valider", command=on_valider)
    bouton_valider.grid(row=3, column=0, columnspan=2, pady=20)

    # Lancer la boucle principale
    fenetre.mainloop()

# Appel de la fonction d'interface graphique
if __name__ == "__main__":
    interface_graphique()
