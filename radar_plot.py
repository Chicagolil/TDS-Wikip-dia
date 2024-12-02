from tkinter import Tk, Toplevel, Frame, Scrollbar, Text, Canvas, VERTICAL, RIGHT, BOTH, END
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

def afficher_fenetres_clusters_interpretations(themes_principaux_tfidf, interpretations):
    """
    Crée deux fenêtres distinctes :
    - Une fenêtre pour les graphiques radars des clusters, organisés avec 5 par ligne.
    - Une autre fenêtre pour afficher les interprétations, avec une ligne de séparation sous chaque interprétation.

    :param themes_principaux_tfidf: Liste des thèmes principaux pour chaque cluster (par scores TF-IDF).
    :param interpretations: Liste des interprétations textuelles pour chaque cluster.
    """
    # Fenêtre principale pour les graphiques radars
    root_graphiques = Tk()
    root_graphiques.title("Graphiques Radars des Clusters")
    root_graphiques.geometry("1400x800")

    # Fenêtre secondaire pour les interprétations
    root_interpretations = Toplevel(root_graphiques)
    root_interpretations.title("Interprétations des Clusters")
    root_interpretations.geometry("800x600")

    # =====================
    # Fenêtre 1 : Clusters
    # =====================
    frame_graphiques = Frame(root_graphiques)
    frame_graphiques.pack(fill="both", expand=True)

    num_clusters = len(themes_principaux_tfidf)
    cols = 5  # Nombre de graphiques par ligne
    rows = (num_clusters // cols) + (num_clusters % cols > 0)

    fig, axes = plt.subplots(rows, cols, figsize=(20, 4 * rows), subplot_kw=dict(polar=True))

    # Si un seul cluster, transformer axes en une liste
    if num_clusters == 1:
        axes = [axes]
    else:
        axes = axes.flatten()  # Aplatir si plusieurs lignes

    # Tracer les graphiques radars
    for cluster_id in range(num_clusters):
        mots_tfidf = [mot[0] for mot in themes_principaux_tfidf[cluster_id]]
        valeurs_tfidf = [mot[1] for mot in themes_principaux_tfidf[cluster_id]]
        mots_tfidf += [mots_tfidf[0]]  # Bouclage
        valeurs_tfidf += [valeurs_tfidf[0]]
        angles = np.linspace(0, 2 * np.pi, len(mots_tfidf), endpoint=True)

        ax = axes[cluster_id]
        ax.plot(angles, valeurs_tfidf, color='blue', linewidth=2, linestyle='solid')
        ax.fill(angles, valeurs_tfidf, color='blue', alpha=0.25)
        ax.set_xticks(angles)
        ax.set_xticklabels(mots_tfidf, fontsize=10, ha='center')
        ax.set_yticklabels([])
        ax.set_title(f"Cluster {cluster_id}", fontsize=14, pad=20)

    # Supprimer les axes inutilisés s'il y a moins de graphiques que de cases
    for i in range(num_clusters, len(axes)):
        fig.delaxes(axes[i])

    # Ajuster les espaces entre graphiques
    plt.subplots_adjust(wspace=0.5, hspace=0.8)

    # Intégrer les graphiques Matplotlib dans Tkinter
    canvas_graphiques = FigureCanvasTkAgg(fig, master=frame_graphiques)
    canvas_graphiques.draw()
    canvas_graphiques.get_tk_widget().pack(fill="both", expand=True)

    # ==========================
    # Fenêtre 2 : Interprétations
    # ==========================
    frame_interpretations = Frame(root_interpretations)
    frame_interpretations.pack(fill="both", expand=True)

    # Ajouter une zone de texte avec un scrollbar
    scrollbar = Scrollbar(frame_interpretations, orient=VERTICAL)
    text_area = Text(frame_interpretations, wrap="word", yscrollcommand=scrollbar.set, font=("Helvetica", 12))
    scrollbar.config(command=text_area.yview)
    scrollbar.pack(side=RIGHT, fill="y")
    text_area.pack(side="left", fill=BOTH, expand=True)

    # Ajouter les interprétations dans la zone de texte avec une ligne en dessous
    for cluster_id, interpretation in enumerate(interpretations):
        interpretation_text = f"{interpretation if interpretation else '[Pas d\'interprétation]'}"
        text_area.insert(END, interpretation_text + "\n")
        text_area.insert(END, "-" * 100 + "\n")  # Ligne de séparation

    # Lancer les deux fenêtres
    root_graphiques.mainloop()
