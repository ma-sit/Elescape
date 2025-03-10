import json
from shared.utils.user_progression_handler import (
    charger_progression as charger_progression_utilisateur,
    sauvegarder_progression as sauvegarder_progression_utilisateur,
    debloquer_niveau_suivant as debloquer_niveau_suivateur,
    reinitialiser_progression as reinitialiser_progression_utilisateur,
    ajouter_elements_decouverts as ajouter_elements_decouverts_utilisateur
)

"""
Ce module sert d'adaptateur pour la compatibilité avec le code existant.
Il redirige les appels de fonctions vers le nouveau système de gestion des progressions 
par utilisateur.
"""

# Fonction pour charger la progression des niveaux
def charger_progression():
    """
    Charge la progression depuis le système de gestion par utilisateur.
    """
    return charger_progression_utilisateur()

# Fonction pour sauvegarder la progression
def sauvegarder_progression(progression):
    """
    Sauvegarde la progression dans le système de gestion par utilisateur.
    """
    return sauvegarder_progression_utilisateur(progression)

# Fonction pour débloquer le niveau suivant
def debloquer_niveau_suivant(niveau_actuel):
    """
    Débloque le niveau suivant dans le système de gestion par utilisateur.
    """
    return debloquer_niveau_suivateur(niveau_actuel)

# Fonction pour réinitialiser la progression
def reinitialiser_progression():
    """
    Réinitialise la progression dans le système de gestion par utilisateur.
    """
    return reinitialiser_progression_utilisateur()

# Fonction pour ajouter des éléments découverts à la progression
def ajouter_elements_decouverts(elements):
    """
    Ajoute des éléments découverts à la progression dans le système de gestion par utilisateur.
    """
    return ajouter_elements_decouverts_utilisateur(elements)