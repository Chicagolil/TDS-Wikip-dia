import re
import spacy
from nltk.corpus import stopwords
from unidecode import unidecode

# Charger le modèle français de spacy
nlp = spacy.load("fr_core_news_sm")
stop_words = set(stopwords.words("french"))

def nettoyer_texte(texte):
    texte = re.sub(r"\b\w['’]", '', texte)
    

    # Retirer les caractères spéciaux, les chiffres, et passer en minuscules
    texte = re.sub(r'[^a-zA-Z\s]', '', texte)  # Garder seulement les lettres et espaces
    texte = texte.lower()

    # Appliquer le modèle de Spacy pour tokenizer et lemmatiser
    doc = nlp(texte)
    mots_nettoyes = [
        token.lemma_ for token in doc 
        if token.text not in stop_words and not token.is_punct and not token.is_space
        and len(token.text) > 1 
    ]

    # Rejoindre les mots nettoyés en un seul texte
    texte_nettoye = " ".join(mots_nettoyes)
    return texte_nettoye
