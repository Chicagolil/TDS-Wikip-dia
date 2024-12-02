from openai import OpenAI
client = OpenAI(api_key = "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"
)


def interpreter_themes_principaux(themes_principaux):
    """
    Utilise l'API ChatGPT pour interpréter les thèmes principaux de chaque cluster.

    :param themes_principaux: Liste de listes, où chaque sous-liste contient les thèmes principaux (mots-clés) d'un cluster.
    :return: Liste d'interprétations fournies par ChatGPT pour chaque cluster.
    """
    interpretations = []
    
    for cluster_id, mots_cles in enumerate(themes_principaux):
        # Préparer le message pour ChatGPT
        mots = [mot[0] for mot in mots_cles]
        prompt = (
            f"Voici une liste de mots-clés représentant les thèmes principaux d'un cluster d'articles Wikipédia :\n"
            f"{', '.join(mots)}.\n"
            f"Peux-tu interpréter ces mots et me donner une description concise du thème représenté ?"
        )

        # Appeler l'API ChatGPT
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui analyse les données thématiques."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            

            # Extraire l'interprétation
            interpretation = response.choices[0].message.content
            interpretations.append(f"Cluster {cluster_id}: {interpretation}")
        
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API pour le cluster {cluster_id}: {e}")
            interpretations.append(f"Cluster {cluster_id}: Impossible d'obtenir une interprétation.")
    
    return interpretations