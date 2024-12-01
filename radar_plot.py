import matplotlib.pyplot as plt
import numpy as np

def tracer_graphes_radars(themes_principaux_tfidf, themes_principaux_distance):
    """
    Affiche deux lignes de graphiques radars pour chaque cluster :
    - Ligne 1 : Basée sur les scores TF-IDF.
    - Ligne 2 : Basée sur la distance par rapport au centre du cluster.

    :param themes_principaux_tfidf: Liste des thèmes principaux pour chaque cluster (par scores TF-IDF).
    :param themes_principaux_distance: Liste des thèmes principaux pour chaque cluster (par distance).
    """
    num_clusters = len(themes_principaux_tfidf)
    fig, axes = plt.subplots(2, num_clusters, figsize=(4 * num_clusters, 10), subplot_kw=dict(polar=True))

    if num_clusters == 1:
        axes = np.array([[axes[0]], [axes[1]]])  # Assurer une structure matricielle même pour un cluster

    for cluster_id in range(num_clusters):
        # Ligne 1 : Basée sur les scores TF-IDF
        mots_tfidf = [mot[0] for mot in themes_principaux_tfidf[cluster_id]]
        valeurs_tfidf = [mot[1] for mot in themes_principaux_tfidf[cluster_id]]
        mots_tfidf += [mots_tfidf[0]]  # Bouclage
        valeurs_tfidf += [valeurs_tfidf[0]]
        angles = np.linspace(0, 2 * np.pi, len(mots_tfidf), endpoint=True)

        ax = axes[0, cluster_id]
        ax.plot(angles, valeurs_tfidf, color='blue', linewidth=2, linestyle='solid')
        ax.fill(angles, valeurs_tfidf, color='blue', alpha=0.25)
        ax.set_xticks(angles)
        ax.set_xticklabels(mots_tfidf)
        ax.set_yticklabels([])
        ax.set_title(f"Cluster {cluster_id} (TF-IDF)", fontsize=14, pad=20)

        # Ligne 2 : Basée sur la distance au centre
        mots_distance = [mot[0] for mot in themes_principaux_distance[cluster_id]]
        valeurs_distance = [mot[1] for mot in themes_principaux_distance[cluster_id]]
        mots_distance += [mots_distance[0]]  # Bouclage
        valeurs_distance += [valeurs_distance[0]]
        angles = np.linspace(0, 2 * np.pi, len(mots_distance), endpoint=True)

        ax = axes[1, cluster_id]
        ax.plot(angles, valeurs_distance, color='green', linewidth=2, linestyle='solid')
        ax.fill(angles, valeurs_distance, color='green', alpha=0.25)
        ax.set_xticks(angles)
        ax.set_xticklabels(mots_distance)
        ax.set_yticklabels([])
        ax.set_title(f"Cluster {cluster_id} (Distance)", fontsize=14, pad=20)

    plt.tight_layout()
    plt.show()
