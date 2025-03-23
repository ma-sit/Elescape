#Projet : Elescape
#Auteurs : Mathis MENNESSIER ; Julien MONGENET ; Simon BILLE

import os
import json

# Chemin du fichier de profils
PROFILES_FILE = os.path.join("data", "profiles.json")

def load_profiles():
    """
    Charge les profils existants ou retourne une structure par défaut.
    """
    if not os.path.exists(PROFILES_FILE):
        return {"active_profile": None, "profiles": []}
    
    try:
        with open(PROFILES_FILE, "r") as f:
            profiles = json.load(f)
            return profiles
    except:
        return {"active_profile": None, "profiles": []}

def get_active_profile():
    """
    Récupère l'ID du profil actif.
    """
    profiles = load_profiles()
    return profiles.get("active_profile")

def charger_progression():
    """
    Charge la progression du profil actif.
    """
    profiles = load_profiles()
    active_profile_id = profiles.get("active_profile")
    
    if not active_profile_id:
        return {"niveaux_debloques": [1], "elements_decouverts": []}
    
    for profile in profiles.get("profiles", []):
        if profile["id"] == active_profile_id:
            return profile.get("progression", {"niveaux_debloques": [1], "elements_decouverts": []})
    
    return {"niveaux_debloques": [1], "elements_decouverts": []}

def sauvegarder_progression(progression):
    """
    Sauvegarde la progression pour le profil actif.
    """
    profiles = load_profiles()
    active_profile_id = profiles.get("active_profile")
    
    if not active_profile_id:
        return False
    
    for profile in profiles.get("profiles", []):
        if profile["id"] == active_profile_id:
            profile["progression"] = progression
            
            try:
                with open(PROFILES_FILE, "w") as f:
                    json.dump(profiles, f)
                return True
            except Exception as e:
                print(f"Erreur lors de la sauvegarde de la progression: {e}")
                return False
    
    return False

def debloquer_niveau_suivant(niveau_actuel):
    """
    Débloque le niveau suivant pour le profil actif.
    """
    progression = charger_progression()
    if niveau_actuel + 1 not in progression["niveaux_debloques"]:
        progression["niveaux_debloques"].append(niveau_actuel + 1)
        return sauvegarder_progression(progression)
    return False

def reinitialiser_progression():
    """
    Réinitialise la progression du profil actif.
    """
    progression = {"niveaux_debloques": [1], "elements_decouverts": []}
    return sauvegarder_progression(progression)

def ajouter_elements_decouverts(elements):
    """
    Ajoute des éléments découverts à la progression du profil.
    """
    progression = charger_progression()
    
    # Convertir en ensemble pour éliminer les doublons
    elements_actuels = set(progression.get("elements_decouverts", []))
    elements_actuels.update(elements)
    
    progression["elements_decouverts"] = list(elements_actuels)
    return sauvegarder_progression(progression)