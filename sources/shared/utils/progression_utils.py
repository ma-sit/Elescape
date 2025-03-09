import json

# Fonction pour charger la progression des niveaux
def charger_progression():
    try:
        with open("data/progression.json", "r") as f:
            progression = json.load(f)
            # Assurer la compatibilité avec les anciennes sauvegardes
            if "elements_decouverts" not in progression:
                progression["elements_decouverts"] = []
            return progression
    except:
        # Si le fichier n'existe pas, créer une progression par défaut
        progression = {"niveaux_debloques": [1], "elements_decouverts": []}
        sauvegarder_progression(progression)
        return progression

# Fonction pour sauvegarder la progression
def sauvegarder_progression(progression):
    try:
        with open("data/progression.json", "w") as f:
            json.dump(progression, f)
        return True
    except:
        print("Erreur lors de la sauvegarde de la progression")
        return False

# Fonction pour débloquer le niveau suivant
def debloquer_niveau_suivant(niveau_actuel):
    progression = charger_progression()
    if niveau_actuel + 1 not in progression["niveaux_debloques"]:
        progression["niveaux_debloques"].append(niveau_actuel + 1)
        sauvegarder_progression(progression)
        return True
    return False

# Fonction pour réinitialiser la progression
def reinitialiser_progression():
    progression = {"niveaux_debloques": [1], "elements_decouverts": []}
    return sauvegarder_progression(progression)

# Fonction pour ajouter des éléments découverts à la progression
def ajouter_elements_decouverts(elements):
    progression = charger_progression()
    # Convertir en ensemble pour éliminer les doublons
    elements_actuels = set(progression.get("elements_decouverts", []))
    elements_actuels.update(elements)
    progression["elements_decouverts"] = list(elements_actuels)
    return sauvegarder_progression(progression)