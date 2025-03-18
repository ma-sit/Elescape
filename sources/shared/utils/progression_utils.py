from shared.utils.user_account_manager import (
    get_current_user,
    load_progression as load_user_progression,
    save_progression as save_user_progression,
    initialize_system
)

# Initialisation du système
initialize_system()

def charger_progression():
    """
    Charge la progression de l'utilisateur actuel.
    """
    # Récupérer l'utilisateur actuel
    username = get_current_user()
    if not username:
        # Si aucun utilisateur n'est connecté, retourner une progression par défaut
        return {"niveaux_debloques": [1], "elements_decouverts": []}
    
    # Charger la progression de l'utilisateur
    return load_user_progression(username)

def sauvegarder_progression(progression):
    """
    Sauvegarde la progression pour l'utilisateur actuel.
    """
    # Récupérer l'utilisateur actuel
    username = get_current_user()
    if not username:
        # Si aucun utilisateur n'est connecté, ne rien faire
        return False
    
    # Sauvegarder la progression pour l'utilisateur actuel
    return save_user_progression(username, progression)

def debloquer_niveau_suivant(niveau_actuel):
    """
    Débloque le niveau suivant pour l'utilisateur actuel.
    """
    progression = charger_progression()
    if niveau_actuel + 1 not in progression["niveaux_debloques"]:
        progression["niveaux_debloques"].append(niveau_actuel + 1)
        return sauvegarder_progression(progression)
    return False

def reinitialiser_progression():
    """
    Réinitialise la progression de l'utilisateur actuel.
    """
    progression = {"niveaux_debloques": [1], "elements_decouverts": []}
    return sauvegarder_progression(progression)

def ajouter_elements_decouverts(elements):
    """
    Ajoute des éléments découverts à la progression de l'utilisateur.
    """
    progression = charger_progression()
    
    # Convertir en ensemble pour éliminer les doublons
    elements_actuels = set(progression.get("elements_decouverts", []))
    elements_actuels.update(elements)
    
    progression["elements_decouverts"] = list(elements_actuels)
    return sauvegarder_progression(progression)