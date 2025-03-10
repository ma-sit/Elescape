import os
import json
import uuid
import platform
import getpass
import socket
import hashlib

"""
Module pour gérer la progression par utilisateur dans Vitanox.
Ce module permet d'identifier l'appareil de façon unique et de stocker/récupérer
les données de progression spécifiques à chaque utilisateur.
"""

# Chemin du répertoire de données
DATA_DIR = "data"
USER_DATA_DIR = os.path.join(DATA_DIR, "users")
DEVICE_ID_FILE = os.path.join(DATA_DIR, "device_id.json")

def get_device_identifier():
    """
    Génère un identifiant unique pour l'appareil basé sur des informations matérielles.
    Retourne un hash qui sert d'identifiant d'appareil.
    """
    try:
        # Collecte des informations système pour créer un identifiant unique
        system_info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "username": getpass.getuser(),
            "machine": platform.machine(),
            "node": platform.node()
        }
        
        # Création d'une chaîne d'identification
        id_string = f"{system_info['hostname']}:{system_info['platform']}:{system_info['username']}"
        
        # Hachage de la chaîne pour obtenir un identifiant unique
        device_id = hashlib.md5(id_string.encode()).hexdigest()
        return device_id
    except Exception as e:
        print(f"Erreur lors de la génération de l'identifiant d'appareil: {e}")
        # Fallback au cas où la méthode standard échoue
        return str(uuid.uuid4())

def load_or_create_device_id():
    """
    Charge l'identifiant de l'appareil s'il existe, sinon en crée un nouveau.
    """
    try:
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, "r") as f:
                data = json.load(f)
                return data.get("device_id")
        
        # Si le fichier n'existe pas, générer un nouvel identifiant
        device_id = get_device_identifier()
        
        # Créer le répertoire data s'il n'existe pas
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Sauvegarder l'identifiant
        with open(DEVICE_ID_FILE, "w") as f:
            json.dump({"device_id": device_id}, f)
        
        return device_id
    except Exception as e:
        print(f"Erreur lors du chargement/création de l'identifiant d'appareil: {e}")
        return get_device_identifier()  # Fallback en cas d'erreur

def get_user_data_path():
    """
    Retourne le chemin vers le dossier de données de l'utilisateur courant.
    Crée le dossier s'il n'existe pas.
    """
    device_id = load_or_create_device_id()
    user_path = os.path.join(USER_DATA_DIR, device_id)
    os.makedirs(user_path, exist_ok=True)
    return user_path

def get_progression_file_path():
    """
    Retourne le chemin complet vers le fichier de progression de l'utilisateur.
    """
    return os.path.join(get_user_data_path(), "progression.json")

def charger_progression():
    """
    Charge la progression de l'utilisateur actuel.
    Remplace la fonction existante dans progression_utils.py.
    """
    try:
        progression_file = get_progression_file_path()
        if os.path.exists(progression_file):
            with open(progression_file, "r") as f:
                progression = json.load(f)
                # Assurer la compatibilité avec les anciennes sauvegardes
                if "elements_decouverts" not in progression:
                    progression["elements_decouverts"] = []
                return progression
        else:
            # Vérifier si une progression existe dans l'ancien emplacement
            old_progression_file = os.path.join(DATA_DIR, "progression.json")
            if os.path.exists(old_progression_file):
                # Migrer l'ancienne progression vers le nouveau système
                with open(old_progression_file, "r") as f:
                    progression = json.load(f)
                    if "elements_decouverts" not in progression:
                        progression["elements_decouverts"] = []
                    
                # Sauvegarder dans le nouveau chemin
                sauvegarder_progression(progression)
                return progression
        
        # Si aucune progression n'existe, créer une progression par défaut
        progression = {"niveaux_debloques": [1], "elements_decouverts": []}
        sauvegarder_progression(progression)
        return progression
    except Exception as e:
        print(f"Erreur lors du chargement de la progression: {e}")
        # En cas d'échec, retourner une progression par défaut
        return {"niveaux_debloques": [1], "elements_decouverts": []}

def sauvegarder_progression(progression):
    """
    Sauvegarde la progression de l'utilisateur actuel.
    Remplace la fonction existante dans progression_utils.py.
    """
    try:
        progression_file = get_progression_file_path()
        # S'assurer que le répertoire existe
        os.makedirs(os.path.dirname(progression_file), exist_ok=True)
        
        with open(progression_file, "w") as f:
            json.dump(progression, f)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la progression: {e}")
        return False

def migrate_all_users_from_old_system():
    """
    Fonction utilitaire pour migrer les données depuis l'ancien système.
    À utiliser lors de la première exécution après mise à jour.
    """
    try:
        old_progression_file = os.path.join(DATA_DIR, "progression.json")
        if os.path.exists(old_progression_file):
            # Charger l'ancienne progression
            with open(old_progression_file, "r") as f:
                progression = json.load(f)
            
            # Sauvegarder dans le nouveau système
            sauvegarder_progression(progression)
            
            # Renommer l'ancien fichier pour éviter de l'écraser
            os.rename(old_progression_file, os.path.join(DATA_DIR, "progression.json.old"))
            
            print("Migration réussie depuis l'ancien système de progression")
            return True
    except Exception as e:
        print(f"Erreur lors de la migration depuis l'ancien système: {e}")
    
    return False

def debloquer_niveau_suivant(niveau_actuel):
    """
    Débloque le niveau suivant pour l'utilisateur actuel.
    """
    progression = charger_progression()
    if niveau_actuel + 1 not in progression["niveaux_debloques"]:
        progression["niveaux_debloques"].append(niveau_actuel + 1)
        sauvegarder_progression(progression)
        return True
    return False

def reinitialiser_progression():
    """
    Réinitialise la progression de l'utilisateur actuel.
    """
    progression = {"niveaux_debloques": [1], "elements_decouverts": []}
    return sauvegarder_progression(progression)

def ajouter_elements_decouverts(elements):
    """
    Ajoute des éléments découverts à la progression de l'utilisateur actuel.
    """
    progression = charger_progression()
    # Convertir en ensemble pour éliminer les doublons
    elements_actuels = set(progression.get("elements_decouverts", []))
    elements_actuels.update(elements)
    progression["elements_decouverts"] = list(elements_actuels)
    return sauvegarder_progression(progression)

# Lors de l'importation du module, vérifier la migration
# Ce code ne s'exécute que lorsque le module est importé
if __name__ != "__main__":
    # Essayer de créer les répertoires nécessaires
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    # Charger/créer l'ID de l'appareil
    device_id = load_or_create_device_id()
    
    # Vérifier si une migration est nécessaire
    progression_path = get_progression_file_path()
    if not os.path.exists(progression_path):
        migrate_all_users_from_old_system()