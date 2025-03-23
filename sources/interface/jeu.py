#Projet : Elescape
#Auteurs : Mathis MENNESSIER ; Julien MONGENET ; Simon BILLE

from pygame import *
import sys
import os
import csv
import random
import json
from math import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.menu_interf_jeu import menu_parametres
from interface.menu import bouton
from interface.page_laterale_jeu_combinaisons import Page
from interface.parametres import TOUCHES_DEFAUT
from interface.fin_niveau_victoire import afficher_victoire_niveau
from shared.utils.progression_utils import charger_progression, sauvegarder_progression

# Variables pour le paramètre de volume global
global_volume_general = 1.0
global_volume_musique = 1.0
global_volume_sfx = 1.0

elements = {}

# Séquences d'animation pour les états extra (pour les animaux)
EXTRA_ANIM_SEQUENCES = {
    "sleep": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    "eat": [0, 1, 2, 3, 2, 3, 2, 3, 2, 1, 0]
}

# Fonction pour déterminer la direction (cardinale) la plus proche d'un vecteur (dx, dy)
def get_direction(dx, dy):
    angle = degrees(atan2(dy, dx))
    if -45 <= angle < 45:
        return "right"
    elif 45 <= angle < 135:
        return "down"
    elif -135 <= angle < -45:
        return "up"
    else:
        return "left"

def wrap_text(text, max_chars=40):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

# Charger les frames du personnage depuis un dossier en appliquant un facteur d'échelle
def charger_frames_perso_from_folder(folder_path, directions=("down", "left", "right", "up"), nb_frames=4, scale=1.0):
    frames = {}
    for direction in directions:
        frames[direction] = []
        for i in range(1, nb_frames+1):
            file_name = f"{direction}{i}.png"
            full_path = os.path.join(folder_path, file_name)
            try:
                frame = image.load(full_path).convert_alpha()
                if scale != 1.0:
                    new_width = int(frame.get_width() * scale)
                    new_height = int(frame.get_height() * scale)
                    frame = transform.scale(frame, (new_width, new_height))
                frames[direction].append(frame)
            except Exception as e:
                print(f"Erreur lors du chargement de {full_path}: {e}")
    return frames

# Chargement des touches du jeu
def charger_touches():
    try:
        with open("data/touches.json", "r") as f:
            touches = json.load(f)
        for key in TOUCHES_DEFAUT:
            if key not in touches:
                touches[key] = TOUCHES_DEFAUT[key]
        return touches
    except Exception as e:
        print(f"Erreur lors du chargement des touches: {e}")
        return TOUCHES_DEFAUT.copy()

# Chargement de l'encyclopédie
try:
    with open('data/csv/encyclopedie.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            row = {k.strip(): v.strip() for k, v in row.items()}
            elem_id = row.get("ID")
            if elem_id is None or elem_id == "":
                print("Erreur : ID manquant dans", row)
                continue
            elements[int(elem_id)] = {
                "Nom": row.get("Nom", "Inconnu"),
                "Creations": [int(x) for x in row.get("Creations", "").split(',') if x],
                "DR": int(row.get("DR", "0") or "0"),
                "Image": row.get("Image", ""),
                "Type": row.get("Type", "classique"), # "animal", "objectif" ou "classique"
                "Mission": row.get("Mission", "")
            }
            if elements[int(elem_id)]["Type"].lower() == "objectif":
                elements[int(elem_id)]["mission_seen"] = False
except Exception as e:
    print(f"Erreur lors du chargement de l'encyclopédie: {e}")
    elements = {0: {"Nom": "Inconnu", "Creations": [], "DR": 0, "Image": "", "Type": "classique", "Mission": ""}}

# Fonction qui renvoie la liste des identifiants communs entre les "Créations" des deux éléments.
def fusionner_ids(element1, element2):
    common = []
    if element1 not in elements or element2 not in elements:
        return common
    if elements[element1]["Nom"] != elements[element2]["Nom"]:
        for cid in elements[element1]["Creations"]:
            if cid in elements[element2]["Creations"] and cid not in common:
                common.append(cid)
    return common

# Pour compatibilité, fusionner() retourne le premier id commun s'il existe
def fusionner(element1, element2):
    common = fusionner_ids(element1, element2)
    if common:
        return common[0]
    return None

def get_next_image(c, w):
    c = (c + 1) % len(w)
    return w[c], c

# Charger les frames d'un animal depuis un dossier en appliquant un facteur d'échelle
def charger_frames_animal_from_folder(folder_path, nb_frames=4, directions=("down", "left", "right", "up"), extras=("sleep", "eat"), scale=1.0):
    frames = {}
    for direction in directions:
        frames[direction] = []
        for i in range(1, nb_frames+1):
            file_name = f"{direction}{i}.png"
            full_path = os.path.join(folder_path, file_name)
            try:
                frame = image.load(full_path).convert_alpha()
                if scale != 1.0:
                    new_width = int(frame.get_width() * scale)
                    new_height = int(frame.get_height() * scale)
                    frame = transform.scale(frame, (new_width, new_height))
                frames[direction].append(frame)
            except Exception as e:
                print(f"Erreur lors du chargement de {full_path}: {e}")
    for extra in extras:
        frames[extra] = []
        for i in range(1, nb_frames+1):
            file_name = f"{extra}{i}.png"
            full_path = os.path.join(folder_path, file_name)
            try:
                frame = image.load(full_path).convert_alpha()
                if scale != 1.0:
                    new_width = int(frame.get_width() * scale)
                    new_height = int(frame.get_height() * scale)
                    frame = transform.scale(frame, (new_width, new_height))
                frames[extra].append(frame)
            except Exception as e:
                print(f"Erreur lors du chargement de {full_path}: {e}")
    return frames

# Afficher les éléments en appliquant une échelle aux images
def afficher_elements(ecr, elements, elementsbase, scale=1.0):
    objets = []
    for elem_id, instances in elementsbase.items():
        if elem_id == 0:
            continue
        if elem_id in elements:
            for instance in instances:
                img_path = elements[elem_id]["Image"]
                if not img_path:
                    print(f"Erreur: Chemin d'image vide pour l'élément {elem_id}")
                    continue
                if isinstance(img_path, str):
                    img_paths = [p.strip().strip('"') for p in img_path.split(',')]
                else:
                    img_paths = [img_path]
                if not img_paths:
                    print(f"Erreur: Aucun chemin d'image valide pour l'élément {elem_id}")
                    continue
                x, y = instance["x"], instance["y"]
                t = elements[elem_id].get("Type", "").lower()
                if t == "animal":
                    try:
                        frames = charger_frames_animal_from_folder(img_paths[0], scale=scale)
                        obj = {
                            "id": elem_id,
                            "is_animal": True,
                            "frames": frames,
                            "current_direction": "down",
                            "anim_index": 0,
                            "last_anim_time": 0,
                            "last_move_time": 0,
                            "state": "idle",
                            "state_start_time": 0,
                            "rect": frames["down"][0].get_rect(center=(x, y)),
                            "selected": False,
                            "x": x,
                            "y": y,
                            "image": frames["down"][0]
                        }
                        objets.append(obj)
                    except Exception as e:
                        print(f"Erreur lors du chargement de l'animal {elem_id}: {e}")
                elif t == "objectif":
                    try:
                        img_choice = random.choice(img_paths)
                        img = image.load(img_choice).convert_alpha()
                        # Redimensionnement de l'image selon le facteur scale
                        orig_w, orig_h = img.get_size()
                        img = transform.scale(img, (int(orig_w * scale), int(orig_h * scale)))
                        obj = {
                            "id": elem_id,
                            "is_objectif": True,
                            "image": img,
                            "original_image": img.copy(),
                            "rect": img.get_rect(center=(x, y)),
                            "x": x,
                            "y": y,
                            "selected": False,
                            "mission_seen": False
                        }
                        objets.append(obj)
                    except Exception as e:
                        print(f"Erreur lors du chargement de l'objectif {elem_id}: {e}")
                else:
                    try:
                        img_choice = random.choice(img_paths)
                        img = image.load(img_choice).convert_alpha()
                        orig_w, orig_h = img.get_size()
                        img = transform.scale(img, (int(orig_w * scale), int(orig_h * scale)))
                        obj = {
                            "id": elem_id,
                            "image": img,
                            "original_image": img.copy(),
                            "rect": img.get_rect(center=(x, y)),
                            "x": x,
                            "y": y,
                            "selected": False
                        }
                        objets.append(obj)
                    except Exception as e:
                        print(f"Erreur lors du chargement de l'image {img_path} pour l'élément {elem_id}: {e}")
    # On trie par rect.bottom pour l'ordre d'affichage
    objets.sort(key=lambda obj: obj["rect"].bottom)
    return objets

def flouter(surface):
    blurred_surface = surface.copy()
    blurred_surface.fill((180, 180, 180), special_flags=BLEND_RGBA_MULT)
    return blurred_surface

def creer_objet(new_id, img, target_obj, objets):
    x_existing, y_existing = target_obj["rect"].center
    w_existing, h_existing = target_obj["rect"].size
    offsets = [(w_existing/2, h_existing/2), (0, h_existing/2), (-w_existing/2, h_existing/2),
               (-w_existing/2, 0), (-w_existing/2, -h_existing/2), (0, -h_existing/2),
               (w_existing/2, -h_existing/2), (w_existing/2, 0)]
    offset_index = 0
    while True:
        offset_x, offset_y = offsets[offset_index]
        new_x, new_y = x_existing + offset_x, y_existing + offset_y
        new_rect = Rect(new_x, new_y, img.get_width(), img.get_height())
        if not any(obj["rect"].colliderect(new_rect) for obj in objets):
            break
        offset_index += 1
        if offset_index >= len(offsets):
            new_x, new_y = x_existing + offset_x, y_existing + offset_y
            break
    return {
        "id": new_id,
        "image": img,
        "original_image": img.copy(),
        "rect": img.get_rect(center=(new_x, new_y))
    }

# Classe du tutoriel amélioré
class TutorielAmeliore:
    """
    Classe pour gérer le tutoriel amélioré du jeu Elescape avec des effets visuels
    et une progression plus interactive.
    """
    def __init__(self, screen_width, screen_height, scale_factor=1.0):
        # Dimensions de l'écran
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale = scale_factor
        
        # Étapes du tutoriel
        self.etapes = [
            {
                "texte": "Bienvenue sur Elescape !",
                "auto_avance": True,
                "delai": 2000,
                "action_requise": False,
                "indicateur": None,
                "accompli": False
            },
            {
                "texte": "Clique droit n'importe où pour déplacer ton personnage",
                "auto_avance": False,
                "action_requise": True,
                "indicateur": "deplacement",
                "accompli": False
            },
            {
                "texte": "Clique gauche sur un objet pour le sélectionner",
                "auto_avance": False,
                "action_requise": True,
                "indicateur": "selection",
                "accompli": False
            },
            {
                "texte": "Déplace-le vers un autre objet compatible pour les fusionner",
                "auto_avance": False,
                "action_requise": True,
                "indicateur": "fusion",
                "accompli": False
            },
            {
                "texte": "Consulte l'encyclopédie pour voir les éléments découverts",
                "auto_avance": False,
                "action_requise": True,
                "indicateur": "encyclopedie",
                "accompli": False
            },
            {
                "texte": "Appuie sur Echap pour ouvrir le menu",
                "auto_avance": False,
                "action_requise": True,
                "indicateur": "menu",
                "accompli": False
            },
            {
                "texte": "Essaie de découvrir l'élément qui termine le niveau !",
                "auto_avance": True,
                "delai": 3000,
                "action_requise": False,
                "indicateur": None,
                "accompli": False
            },
            {
                "texte": "Maintenant, à toi de jouer !",
                "auto_avance": True,
                "delai": 3000,
                "action_requise": False,
                "indicateur": None,
                "accompli": False
            }
        ]
        
        # Variables d'état
        self.etape_courante = 0
        self.actif = True
        self.temps_affichage = 0
        self.temps_derniere_interaction = 0
        self.alpha_fond = 0
        self.fondu_entrant = True
        self.temps_pulsation = 0
        self.police = font.Font(None, int(30 * self.scale))
        
        # Variables pour les indicateurs visuels
        self.indicateur_alpha = 0
        self.indicateur_taille = 1.0
        self.temps_indicateur = 0
        
        # Création des images pour les indicateurs
        self.img_curseur_main = self.creer_curseur_main_defaut()
        self.img_curseur_clic = self.creer_curseur_clic_defaut()
        self.img_fleche = self.creer_fleche_defaut()
        self.img_cercle = self.creer_cercle_defaut()
    
    def creer_curseur_main_defaut(self):
        """Crée une image de curseur main par défaut"""
        surf = Surface((32, 32), SRCALPHA)
        draw
        
def page_jeu(niveau):
    global global_volume_general, global_volume_musique, global_volume_sfx
    touches = charger_touches()
    elementsbase = {}
    niveau_complete = False
    elfinal = None
    
    # Charger la progression actuelle pour obtenir les éléments déjà découverts
    progression = charger_progression()
    element_decouvert = progression.get("elements_decouverts", [])[:]  # Copie pour éviter de modifier l'original

    # Définir la résolution de référence et calculer les facteurs d'échelle
    reference_width, reference_height = 1920, 1080
    # rec est supposé définir la taille de l'écran (par exemple via rec.right et rec.bottom)
    current_width, current_height = rec.right, rec.bottom
    scale_x = current_width / reference_width
    scale_y = current_height / reference_height
    # Pour les images, on utilise un facteur commun pour préserver les proportions
    scale_common = min(scale_x, scale_y)

    # Variables pour le tutoriel
    tutorial_active = niveau == 1
    tutorial_step = 0
    tutorial_steps = [
        "Bienvenue sur Elescape",
        "Clique droit n'importe où pour déplacer ton personnage",
        "Clique gauche sur un objet pour le sélectionner",
        "Déplace-le vers un autre objet compatible pour les fusionner",
        "Consulte l'encyclopédie pour voir les éléments découverts",
        "Appuie sur Echap pour ouvrir le menu",
        "Essaie de découvrir l'élément qui termine le niveau",
        "Maintenant, à toi de jouer !"
    ]
    # True signifie que l'étape avance automatiquement après un délai
    tutorial_auto_advance = [True, False, False, False, False, False, True, True]
    # Délais en millisecondes pour les étapes avec avance automatique
    tutorial_delays = [2000, 0, 0, 0, 0, 0, 3000, 8000]
    tutorial_actions_done = [False, False, False, False, False, False, False, False]
    tutorial_display_time = 0
    tutorial_font = font.Font(None, 30)
    tutorial_bg_alpha = 0
    tutorial_fade_in = True
    tutorial_last_interaction = 0
    
    try:
        with open(f'data/csv/niveau{niveau}.csv', newline='', encoding='utf-8') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=';')
            bg_loaded = False
            for row in spamreader:
                row = {k.strip(): v.strip() for k, v in row.items()}
                bg = row.get("bg")
                ef = row.get("elfinal")
                if ef:
                    elfinal = int(ef)
                if bg and not bg_loaded:
                    try:
                        fnd = image.load(bg).convert()
                        bg_loaded = True
                    except Exception as e:
                        print(f"Erreur lors du chargement du fond: {e}")
                        fnd = Surface((lrg, htr))
                        fnd.fill((50, 50, 70))
                elem_id = row.get("elements_base")
                emplacement = row.get("emplacement")
                if elem_id and emplacement:
                    try:
                        elem_id = int(elem_id)
                        # On attend ici des coordonnées normalisées entre 0 et 1
                        x_norm, y_norm = map(float, emplacement.split(','))
                        x = int(x_norm * current_width)
                        y = int(y_norm * current_height)
                        if elem_id not in elementsbase:
                            elementsbase[elem_id] = []
                        elementsbase[elem_id].append({"x": x, "y": y})
                    except ValueError as e:
                        print(f"Erreur de format dans le CSV pour l'élément {elem_id}: {emplacement} - {e}")
            if not bg_loaded:
                print("Aucun fond trouvé, utilisation d'un fond par défaut")
                fnd = Surface((lrg, htr))
                fnd.fill((50, 50, 70))
    except FileNotFoundError:
        print(f"Fichier du niveau {niveau} introuvable. Génération d'un niveau par défaut.")
        fnd = Surface((lrg, htr))
        fnd.fill((70, 30, 30))
        base_elements = []
        for elem_id in base_elements:
            if elem_id not in elementsbase:
                elementsbase[elem_id] = []
            num_instances = niveau * 3 + 5
            for i in range(num_instances):
                # Ici on utilise des positions normalisées aléatoires
                x = int(random.random() * current_width)
                y = int(random.random() * current_height)
                elementsbase[elem_id].append({"x": x, "y": y})
    except Exception as e:
        print(f"Erreur lors du chargement du niveau {niveau}: {e}")
        fnd = Surface((lrg, htr))
        fnd.fill((50, 50, 70))
    
    init()
    clock = time.Clock()
    act = True
    selected_obj = None
    element_discovered = False
    final_trigger_time = None
    final_element_found = False
    final_object_reached = False
    final_object_time = None
    final_element_time = None  # Nouvel ajout pour le timer de l'élément final


    # Charger les frames du perso
    try:
        perso_frames = charger_frames_perso_from_folder("data/images/perso", scale=scale_common)
        perso_current_direction = "down"
        perso_anim_index = 0
        perso_last_anim_time = 0
        perso_anim_delay = 150  # Délai en ms entre chaque frame
    except Exception as e:
        print(f"Erreur lors du chargement des frames du personnage: {e}")
        dummy = Surface((50,50))
        dummy.fill((255,0,0))
        perso_frames = {"down": [dummy]}
        perso_current_direction = "down"
        perso_anim_index = 0
        perso_last_anim_time = 0
        perso_anim_delay = 150

    x, y = current_width // 2, current_height // 2
    speed = 5
    target_x, target_y = x, y
    moving = False

    try:
        objets = afficher_elements(ecr, elements, elementsbase, scale=scale_common)
    except Exception as e:
        print(f"Erreur lors de l'affichage des éléments: {e}")
        objets = []
        
    perso_rect = perso_frames["down"][0].get_rect(center=(x, y))
    fnd = transform.scale(fnd, (current_width, current_height))
    target_obj = None
    offset_x, offset_y = 0, 0

    # Charger l'image de base de la bulle
    try:
        bubble_img = image.load("data/images/autres/bulle.png").convert_alpha()
    except Exception as e:
        print(f"Erreur lors du chargement de la bulle : {e}")
        bubble_img = Surface((100, 50))
        bubble_img.fill((255,255,255))
    
    # Fonction pour afficher les messages du tutoriel
    def show_tutorial_message():
        if not tutorial_active or tutorial_step >= len(tutorial_steps):
            return
            
        current_msg = tutorial_steps[tutorial_step]
        
        # Calcul des dimensions du panneau de tutoriel
        padding_horizontal = 40
        padding_vertical = 20
        msg_surf = tutorial_font.render(current_msg, True, (255, 255, 255))
        panel_width = msg_surf.get_width() + padding_horizontal * 2
        panel_height = 60
        
        # Position du panneau (centré horizontalement, plus haut sur l'écran)
        panel_x = (current_width - panel_width) // 2
        panel_y = current_height - 120 # Position plus haute que l'original
        
        # Créer une surface semi-transparente pour le fond du message avec coins arrondis
        tutorial_bg = Surface((panel_width, panel_height), SRCALPHA)
        
        # Calculer l'alpha du fond (animation de fondu)
        nonlocal tutorial_bg_alpha
        if tutorial_fade_in:
            tutorial_bg_alpha = min(tutorial_bg_alpha + 10, 180)
        else:
            tutorial_bg_alpha = max(tutorial_bg_alpha - 10, 0)
        
        # Dessiner le rectangle arrondi
        draw.rect(tutorial_bg, (0, 0, 0, tutorial_bg_alpha), Rect(0, 0, panel_width, panel_height), border_radius=15)
        
        # Ajouter une bordure subtile
        if tutorial_bg_alpha > 50:
            border_alpha = min(255, int(tutorial_bg_alpha * 1.2))
            draw.rect(tutorial_bg, (80, 80, 100, border_alpha), Rect(0, 0, panel_width, panel_height), width=2, border_radius=15)
        
        # Positionner et afficher le fond
        ecr.blit(tutorial_bg, (panel_x, panel_y))
        
        # Afficher le texte du tutoriel
        msg_rect = msg_surf.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height // 2))
        
        # L'opacité du texte suit celle du fond
        msg_surf.set_alpha(int(255 * tutorial_bg_alpha / 180))
        ecr.blit(msg_surf, msg_rect)

    while act:
        try:
            ecr.blit(fnd, (0, 0))
            current_time = time.get_ticks()
            
            # Affichage des éléments classiques (non-animés, non-objectifs)
            for obj in objets:
                if not obj.get("is_animal", False) and not obj.get("is_objectif", False):
                    ecr.blit(obj["image"], (obj["rect"].x, obj["rect"].y))
                    if "enlarge_start" in obj:
                        if current_time - obj["enlarge_start"] > 100:
                            obj["image"] = obj["original_image"]
                            obj["rect"] = obj["original_image"].get_rect(center=obj["rect"].center)
                            del obj["enlarge_start"]
            
            # Gestion des événements
            for evt in event.get():
                if evt.type == QUIT:
                    return False
                elif evt.type == KEYDOWN:
                    for action, key_code in touches.items():
                        if evt.key == key_code:
                            if action == 'Retour':
                                # Pour le tutoriel : Appuyer sur Echap
                                if tutorial_active and not tutorial_actions_done[5]:
                                    tutorial_actions_done[5] = True
                                    if tutorial_step == 5:
                                        tutorial_step += 1
                                        tutorial_fade_in = True
                                        tutorial_bg_alpha = 0
                                        tutorial_display_time = current_time
                                        tutorial_last_interaction = current_time
                                
                                game_screen = ecr.copy()
                                act = menu_parametres(niveau,game_screen)
                elif evt.type == MOUSEBUTTONDOWN:
                    if element_discovered:
                        element_discovered = False
                    elif evt.button == 1:
                        # Utilisation de reversed(objets) pour sélectionner l'objet affiché par-dessus
                        if btn_ency["rect"].collidepoint(evt.pos):
                            son_survol.play()
                            
                            # Tutoriel: Consulter l'encyclopédie
                            if tutorial_active and not tutorial_actions_done[4]:
                                tutorial_actions_done[4] = True
                                if tutorial_step == 4:
                                    tutorial_step += 1
                                    tutorial_fade_in = True
                                    tutorial_bg_alpha = 0
                                    tutorial_display_time = current_time
                                    tutorial_last_interaction = current_time
                            
                            # Utiliser les éléments découverts de la progression actuelle
                            progression_actuelle = charger_progression()        
                            Page(ecr, elements, progression_actuelle.get("elements_decouverts", []))
                        else:
                            for obj in reversed(objets):
                                if obj["rect"].collidepoint(evt.pos):
                                    selected_obj = obj
                                    
                                    # Tutoriel: Sélectionner un objet
                                    if tutorial_active and not tutorial_actions_done[2]:
                                        tutorial_actions_done[2] = True
                                        if tutorial_step == 2:
                                            tutorial_step += 1
                                            tutorial_fade_in = True
                                            tutorial_bg_alpha = 0
                                            tutorial_display_time = current_time
                                            tutorial_last_interaction = current_time
                                    
                                    if obj.get("is_animal", False):
                                        if not obj.get("selected", False):
                                            obj["selected"] = True
                                            base_frame = obj["frames"][obj["current_direction"]][0]
                                            w, h = base_frame.get_size()
                                            scaled_img = transform.scale(base_frame, (int(w * 1.2), int(h * 1.2)))
                                            obj["image"] = scaled_img
                                            obj["rect"] = scaled_img.get_rect(center=obj["rect"].center)
                                    else:
                                        if "original_image" in obj:
                                            obj["image"] = transform.scale(obj["original_image"],
                                                                            (int(obj["original_image"].get_width() * 1.1),
                                                                             int(obj["original_image"].get_height() * 1.1)))
                                            obj["rect"] = obj["image"].get_rect(center=obj["rect"].center)
                                    offset_x, offset_y = evt.pos[0] - obj["rect"].centerx, evt.pos[1] - obj["rect"].centery
                                    break
                    elif evt.button == touches.get('Déplacement', BUTTON_RIGHT):
                        target_x, target_y = mouse.get_pos()
                        moving = True
                        
                        # Tutoriel: Déplacer le personnage
                        if tutorial_active and not tutorial_actions_done[1]:
                            tutorial_actions_done[1] = True
                            if tutorial_step == 1:
                                tutorial_step += 1
                                tutorial_fade_in = True
                                tutorial_bg_alpha = 0
                                tutorial_display_time = current_time
                                tutorial_last_interaction = current_time
                                
                        for obj in reversed(objets):
                            if obj["rect"].collidepoint(evt.pos):
                                obj["enlarge_start"] = time.get_ticks()
                                target_obj = obj
                                if obj.get("is_animal", False):
                                    if not obj.get("selected", False):
                                        obj["selected"] = True
                                        base_frame = obj["frames"][obj["current_direction"]][0]
                                        w, h = base_frame.get_size()
                                        new_size = (int(w * 1.1), int(h * 1.1))
                                        scaled_img = transform.scale(base_frame, new_size)
                                        obj["image"] = scaled_img
                                        obj["rect"] = scaled_img.get_rect(center=obj["rect"].center)
                                else:
                                    orig_w, orig_h = obj["original_image"].get_size()
                                    new_size = (int(orig_w * 1.1), int(orig_h * 1.1))
                                    obj["image"] = transform.scale(obj["original_image"], new_size)
                                    obj["rect"] = obj["image"].get_rect(center=obj["rect"].center)
                                break
                elif evt.type == MOUSEBUTTONUP:
                    if evt.button == 1:
                        if selected_obj:
                            if not selected_obj.get("is_animal", False) and "original_image" in selected_obj:
                                selected_obj["image"] = selected_obj["original_image"]
                                selected_obj["rect"] = selected_obj["image"].get_rect(center=selected_obj["rect"].center)
                            if selected_obj.get("is_animal", False):
                                selected_obj["selected"] = False
                                base_frame = selected_obj["frames"][selected_obj["current_direction"]][0]
                                selected_obj["image"] = base_frame
                                selected_obj["rect"] = base_frame.get_rect(center=selected_obj["rect"].center)
                                if "animal_target_pos" in selected_obj:
                                    del selected_obj["animal_target_pos"]
                                selected_obj["last_move_time"] = time.get_ticks()
                                selected_obj["state"] = "idle"
                            closest_obj = None
                            for obj in objets:
                                if obj != selected_obj and obj["rect"].colliderect(selected_obj["rect"]):
                                    common_ids = fusionner_ids(obj["id"], selected_obj["id"])
                                    if common_ids:
                                        closest_obj = obj
                                        break
                            if closest_obj:
                                common_ids = fusionner_ids(closest_obj["id"], selected_obj["id"])
                                if common_ids:
                                    center = closest_obj["rect"].center
                                    for cid in common_ids:
                                        if cid not in element_decouvert:
                                            element_discovered = cid
                                            element_decouvert.append(cid)
                                            
                                            # Si ce n'est pas l'élément final, sauvegarder immédiatement
                                            if cid != elfinal:
                                                progression = charger_progression()
                                                if cid not in progression.get("elements_decouverts", []):
                                                    elements_decouverts = progression.get("elements_decouverts", [])
                                                    elements_decouverts.append(cid)
                                                    progression["elements_decouverts"] = elements_decouverts
                                                    sauvegarder_progression(progression)
                                            else:
                                                # Pour l'élément final, ne pas le sauvegarder maintenant
                                                final_element_found = True

                                            # Tutoriel: Fusion réussie
                                            if tutorial_active and not tutorial_actions_done[3]:
                                                tutorial_actions_done[3] = True
                                                if tutorial_step == 3:
                                                    tutorial_step += 1
                                                    tutorial_fade_in = True
                                                    tutorial_bg_alpha = 0
                                                    tutorial_display_time = current_time
                                                    tutorial_last_interaction = current_time
                                                    
                                        try:
                                            img_paths = elements[cid]["Image"].split(',')
                                            if img_paths:
                                                img_path = random.choice([p.strip().strip('"') for p in img_paths])
                                                # Charger et mettre à l'échelle l'image du nouvel objet
                                                img = image.load(img_path).convert_alpha()
                                                orig_w, orig_h = img.get_size()
                                                img = transform.scale(img, (int(orig_w * scale_common), int(orig_h * scale_common)))
                                                new_obj = {
                                                    "id": cid,
                                                    "image": img,
                                                    "original_image": img.copy(),
                                                    "rect": img.get_rect(center=center)
                                                }
                                                # Si l'objet restant existe et n'est pas le perso, appliquer un décalage.
                                                if elements[closest_obj["id"]]["DR"] != 0 or elements[selected_obj["id"]]["DR"] != 0:
                                                    offset = -10
                                                    new_center = (closest_obj["rect"].right + new_obj["rect"].width // 2 + offset,
                                                                  closest_obj["rect"].centery)
                                                    new_obj["rect"].center = new_center
                                                offset = new_obj["rect"].width // 2 + 10
                                                center = (closest_obj["rect"].centerx + offset, closest_obj["rect"].centery)
                                                objets.append(new_obj)
                                                # Retirer les éléments fusionnés selon DR
                                                if elements[selected_obj["id"]]["DR"] == 0 and selected_obj in objets:
                                                    objets.remove(selected_obj)
                                                if elements[closest_obj["id"]]["DR"] == 0 and closest_obj in objets:
                                                    objets.remove(closest_obj)
                                                
                                                # MODIFICATION: Vérification améliorée de l'élément final
                                                if elfinal is not None:
                                                    if elfinal in element_decouvert:
                                                        final_element_found = True
                                                        print(f"Élément final {elfinal} trouvé! Fin du niveau activée.")
                                                    else:
                                                        print(f"Élément final: {elfinal}, Éléments découverts: {element_decouvert}")
                                                
                                                # Tutoriel: Niveau terminé
                                                if tutorial_active and not tutorial_actions_done[6]:
                                                    tutorial_actions_done[6] = True
                                                    if tutorial_step == 6:
                                                        tutorial_step += 1
                                                        tutorial_fade_in = True
                                                        tutorial_bg_alpha = 0
                                                        tutorial_display_time = current_time
                                                        tutorial_last_interaction = current_time
                                                            
                                        except Exception as e:
                                            print(f"Erreur lors de la fusion d'éléments: {e}")
                            selected_obj["rect"].center = (evt.pos[0] - offset_x, evt.pos[1] - offset_y)
                            selected_obj["x"], selected_obj["y"] = selected_obj["rect"].center
                            objets.sort(key=lambda obj: obj["rect"].bottom)
                        selected_obj = None
                    elif evt.button == BUTTON_RIGHT:
                        if target_obj:
                            if target_obj.get("is_animal", False):
                                target_obj["selected"] = False
                                base_frame = target_obj["frames"][target_obj["current_direction"]][0]
                                target_obj["image"] = base_frame
                                target_obj["rect"] = base_frame.get_rect(center=target_obj["rect"].center)
                                target_obj["last_move_time"] = time.get_ticks()
                                target_obj["state"] = "idle"
                            else:
                                # Pour les éléments classiques et objectifs, on réinitialise l'image
                                target_obj["image"] = target_obj["original_image"]
                                target_obj["rect"] = target_obj["image"].get_rect(center=target_obj["rect"].center)
                elif evt.type == MOUSEMOTION and selected_obj:
                    selected_obj["rect"].move_ip(evt.rel)
            
            # Mise à jour du déplacement et de l'animation du personnage (perso)
            if moving:
                dx = target_x - x
                dy = target_y - y
                dist = (dx**2 + dy**2) ** 0.5
                if dist < speed:
                    x, y = target_x, target_y
                    moving = False
                else:
                    x += speed * dx / dist
                    y += speed * dy / dist
                perso_rect.center = (x, y)
                if dx != 0 or dy != 0:
                    perso_current_direction = get_direction(dx, dy)
                if current_time - perso_last_anim_time > perso_anim_delay:
                    perso_anim_index = (perso_anim_index + 1) % len(perso_frames[perso_current_direction])
                    perso_last_anim_time = current_time
                perso_obj = {"id": 0, "image": perso_frames[perso_current_direction][perso_anim_index], "rect": perso_rect.copy()}
            else:
                perso_rect.center = (x, y)
                perso_obj = {"id": 0, "image": perso_frames[perso_current_direction][0], "rect": perso_rect.copy()}
            
            # Fusion automatique entre le perso et un élément cible
            if target_obj and perso_rect.colliderect(target_obj["rect"]) and not moving:
                common_ids = fusionner_ids(0, target_obj["id"])
                if common_ids:
                    center = target_obj["rect"].center
                    for cid in common_ids:
                        if cid not in element_decouvert:
                            element_discovered = cid
                            element_decouvert.append(cid)
                            
                            # Sauvegarder l'élément découvert dans la progression
                            progression = charger_progression()
                            if cid not in progression.get("elements_decouverts", []):
                                elements_decouverts = progression.get("elements_decouverts", [])
                                elements_decouverts.append(cid)
                                progression["elements_decouverts"] = elements_decouverts
                                sauvegarder_progression(progression)
                            
                            # Tutoriel: Fusion automatique avec le personnage
                            if tutorial_active and not tutorial_actions_done[3]:
                                tutorial_actions_done[3] = True
                                if tutorial_step == 3:
                                    tutorial_step += 1
                                    tutorial_fade_in = True
                                    tutorial_bg_alpha = 0
                                    tutorial_display_time = current_time
                                    tutorial_last_interaction = current_time
                                    
                        try:
                            img_paths = elements[cid]["Image"].split(',')
                            if img_paths:
                                img_path = random.choice([p.strip().strip('"') for p in img_paths])
                                # Charger et mettre à l'échelle l'image
                                img = image.load(img_path).convert_alpha()
                                orig_w, orig_h = img.get_size()
                                img = transform.scale(img, (int(orig_w * scale_common), int(orig_h * scale_common)))
                                new_obj = {
                                    "id": cid,
                                    "image": img,
                                    "original_image": img.copy(),
                                    "rect": img.get_rect(center=center)
                                }
                                if elements[target_obj["id"]]["DR"] != 0:
                                    offset = -10
                                    new_center = (target_obj["rect"].right + new_obj["rect"].width // 2 + offset,
                                                  target_obj["rect"].centery)
                                    new_obj["rect"].center = new_center
                                offset = new_obj["rect"].width // 2 + 10
                                center = (target_obj["rect"].centerx + offset, target_obj["rect"].centery)
                                objets.append(new_obj)
                                if elements[target_obj["id"]]["DR"] == 0:
                                    if target_obj in objets:
                                        objets.remove(target_obj)
                        except Exception as e:
                            print(f"Erreur lors de la fusion avec le personnage: {e}")
                target_obj = None
                
                # MODIFICATION: Vérification améliorée de l'élément final
                if elfinal is not None:
                    if elfinal in element_decouvert:
                        final_element_found = True
                        print(f"Élément final {elfinal} trouvé! Fin du niveau activée.")
                    else:
                        print(f"Élément final: {elfinal}, Éléments découverts: {element_decouvert}")

            # Mise à jour du mouvement et de l'animation des animaux
            for obj in objets:
                if obj.get("is_animal", False):
                    if not obj.get("selected", False):
                        state = obj.get("state", "idle")
                        if state == "idle":
                            if current_time - obj.get("last_move_time", 0) > 2000:
                                choice = random.random()
                                if choice < 0.7:
                                    obj["state"] = "moving"
                                    obj["state_start_time"] = current_time
                                    cx, cy = obj["rect"].center
                                    angle = random.uniform(0, 2 * pi)
                                    offset = random.randint(120, 200)
                                    tg_x = cx + offset * cos(angle)
                                    tg_y = cy + offset * sin(angle)
                                    tg_x = max(0, min(tg_x, current_width))
                                    tg_y = max(0, min(tg_y, current_height))
                                    obj["animal_target_pos"] = (tg_x, tg_y)
                                    dx = tg_x - cx
                                    dy = tg_y - cy
                                    obj["current_direction"] = get_direction(dx, dy)
                                elif choice < 0.85:
                                    obj["state"] = "sleeping"
                                    obj["state_start_time"] = current_time
                                    obj["anim_sequence"] = EXTRA_ANIM_SEQUENCES["sleep"]
                                    obj["anim_index"] = 0
                                else:
                                    obj["state"] = "eating"
                                    obj["state_start_time"] = current_time
                                    obj["anim_sequence"] = EXTRA_ANIM_SEQUENCES["eat"]
                                    obj["anim_index"] = 0
                        elif obj["state"] == "moving":
                            if "animal_target_pos" in obj:
                                tx, ty = obj["animal_target_pos"]
                                cx, cy = obj["rect"].center
                                dx = tx - cx
                                dy = ty - cy
                                dist = (dx**2 + dy**2) ** 0.5
                                speed_animal = 2
                                if dist < speed_animal:
                                    obj["rect"].center = (tx, ty)
                                    del obj["animal_target_pos"]
                                    obj["state"] = "idle"
                                    obj["last_move_time"] = current_time
                                else:
                                    new_cx = cx + speed_animal * dx / dist
                                    new_cy = cy + speed_animal * dy / dist
                                    new_cx = max(0, min(new_cx, current_width))
                                    new_cy = max(0, min(new_cy, current_height))
                                    obj["rect"].center = (new_cx, new_cy)
                                anim_delay = 200
                                if current_time - obj.get("last_anim_time", 0) > anim_delay:
                                    frames_list = obj["frames"][obj["current_direction"]]
                                    obj["anim_index"] = (obj.get("anim_index", 0) + 1) % len(frames_list)
                                    obj["last_anim_time"] = current_time
                                obj["image"] = obj["frames"][obj["current_direction"]][obj["anim_index"]]
                            else:
                                obj["state"] = "idle"
                                obj["last_move_time"] = current_time
                                obj["anim_index"] = 0
                                obj["image"] = obj["frames"][obj["current_direction"]][0]
                        elif obj["state"] in ["sleeping", "eating"]:
                            anim_delay = 300
                            seq = obj.get("anim_sequence", [])
                            if seq:
                                if current_time - obj.get("last_anim_time", 0) > anim_delay:
                                    obj["last_anim_time"] = current_time
                                    obj["anim_index"] += 1
                                    if obj["anim_index"] >= len(seq):
                                        obj["state"] = "idle"
                                        obj["anim_index"] = 0
                                        obj["last_move_time"] = current_time
                                        obj["image"] = obj["frames"][obj["current_direction"]][0]
                                    else:
                                        frame_idx = seq[obj["anim_index"]]
                                        if obj["state"] == "sleeping":
                                            if "sleep" in obj["frames"]:
                                                obj["image"] = obj["frames"]["sleep"][frame_idx]
                                            else:
                                                obj["image"] = obj["frames"][obj["current_direction"]][0]
                                        elif obj["state"] == "eating":
                                            if "eat" in obj["frames"]:
                                                obj["image"] = obj["frames"]["eat"][frame_idx]
                                            else:
                                                obj["image"] = obj["frames"][obj["current_direction"]][0]
                            else:
                                obj["image"] = obj["frames"][obj["current_direction"]][0]
                    # Si l'animal est sélectionné, son animation reste gelée.
            
            # Pour le rendu final, combiner le perso avec les autres objets et trier par rect.bottom
            perso_obj = {"id": 0, "image": perso_frames[perso_current_direction][perso_anim_index] if moving else perso_frames[perso_current_direction][0], "rect": perso_rect.copy()}
            all_objs = objets + [perso_obj]
            all_objs.sort(key=lambda o: o["rect"].bottom)
            if selected_obj is not None and selected_obj in all_objs:
                all_objs.remove(selected_obj)
                all_objs.append(selected_obj)
            for o in all_objs:
                ecr.blit(o["image"], o["rect"])
            
            # Affichage de l'objectif : pour chaque objet objectif, afficher une bulle en haut à droite
            for obj in objets:
                if obj.get("is_objectif", False):
                    if final_element_found and perso_rect.colliderect(obj["rect"]):
                        if not final_object_reached:
                            final_object_reached = True
                            final_object_time = current_time
                        large_bubble = transform.scale(bubble_img, (150, 100))
                        bubble_x_final = obj["rect"].right - large_bubble.get_width() + 120
                        bubble_y_final = obj["rect"].top - 70
                        ecr.blit(large_bubble, (bubble_x_final, bubble_y_final))
                        thank_text = "Merci !"
                        thank_surface = fnt.render(thank_text, True, (0, 0, 0))
                        ecr.blit(thank_surface, (bubble_x_final + (large_bubble.get_width() - thank_surface.get_width()) // 2,
                                                 bubble_y_final + (large_bubble.get_height() - thank_surface.get_height()) // 2 - 8))
                    # Si c'est l'élément final et qu'il a été découvert, on affiche toujours la bulle
                    elif final_element_found:
                        bubble_x = obj["rect"].right + 35
                        bubble_y = obj["rect"].top - 20
                        small_bubble = transform.scale(bubble_img, (50, 50))
                        ecr.blit(small_bubble, (bubble_x - small_bubble.get_width(), bubble_y))
                        exclam_text = fnt.render("!", True, (255, 0, 0))
                        exclam_x = bubble_x - small_bubble.get_width() + (small_bubble.get_width() - exclam_text.get_width()) // 2
                        exclam_y = bubble_y + (small_bubble.get_height() - exclam_text.get_height()) // 2
                        ecr.blit(exclam_text, (exclam_x, exclam_y))
                        
                    else:
                        # Traitement normal pour les autres objectifs
                        if not elements[obj["id"]].get("mission_seen", False):
                            bubble_x = obj["rect"].right + 35
                            bubble_y = obj["rect"].top - 20
                            small_bubble = transform.scale(bubble_img, (50, 50))
                            ecr.blit(small_bubble, (bubble_x - small_bubble.get_width(), bubble_y))
                            exclam_text = fnt.render("!", True, (255, 0, 0))
                            exclam_x = bubble_x - small_bubble.get_width() + (small_bubble.get_width() - exclam_text.get_width()) // 2
                            exclam_y = bubble_y + (small_bubble.get_height() - exclam_text.get_height()) // 2
                            ecr.blit(exclam_text, (exclam_x, exclam_y))
                        if perso_rect.colliderect(obj["rect"]):
                            # Bulle plus grande pour le vieux monsieur (ID 31)
                            if obj["id"] == 31:
                                large_bubble = transform.scale(bubble_img, (300, 250))  # Bulle plus grande
                                bubble_x_final = obj["rect"].right - large_bubble.get_width() + 250
                                bubble_y_final = obj["rect"].top - 190
                                max_chars = 20  # Plus de caractères par ligne pour le vieux monsieur
                            else:
                                large_bubble = transform.scale(bubble_img, (200, 200))
                                bubble_x_final = obj["rect"].right - large_bubble.get_width() + 200
                                bubble_y_final = obj["rect"].top - 150
                                max_chars = 10
                                
                            ecr.blit(large_bubble, (bubble_x_final, bubble_y_final))
                            mission_text = elements[obj["id"]].get("Mission", "Objectif non défini")
                            mission_text = wrap_text(mission_text, max_chars=max_chars)
                            lines = mission_text.split("\n")
                            y_offset = 0
                            for line in lines:
                                text_surface = fnt.render(line, True, (0, 0, 0))
                                ecr.blit(text_surface, (bubble_x_final + (large_bubble.get_width() - text_surface.get_width()) // 2,
                                                        bubble_y_final + y_offset + 35))
                                y_offset += text_surface.get_height() + 2
                            elements[obj["id"]]["mission_seen"] = True
            # Affichage du tutoriel
            if tutorial_active and tutorial_step < len(tutorial_steps):
                # Gérer l'avancement automatique pour les étapes avec délai
                if tutorial_auto_advance[tutorial_step]:
                    if tutorial_display_time == 0:
                        tutorial_display_time = current_time
                    
                    elapsed_time = current_time - tutorial_display_time
                    if elapsed_time >= tutorial_delays[tutorial_step]:
                        tutorial_actions_done[tutorial_step] = True
                        tutorial_step += 1
                        if tutorial_step < len(tutorial_steps):
                            tutorial_fade_in = True
                            tutorial_bg_alpha = 0
                            tutorial_display_time = current_time
                            tutorial_last_interaction = current_time
                
                # Gérer le fondu des messages
                time_since_last_interaction = current_time - tutorial_last_interaction
                
                # Gérer le fondu des messages
                if tutorial_step > 0 and time_since_last_interaction < 800:
                    tutorial_fade_in = True
                elif time_since_last_interaction > 10000 and not tutorial_auto_advance[tutorial_step] and not tutorial_actions_done[tutorial_step]:
                    # Réafficher avec effet de pulsation si aucune interaction depuis longtemps
                    if int(time_since_last_interaction / 1000) % 2 == 0:
                        tutorial_fade_in = True
                    else:
                        tutorial_fade_in = False
                
                # Afficher le message du tutoriel
                show_tutorial_message()

            hover_ency = bouton(ecr, (150, 150, 150), btn_ency, "Encyclopédie", son_survol, son_clicmenu, r_jeu, surbrillance=BLC)
                                
            if final_object_reached and current_time - final_object_time >= 1000:
                # Sauvegarder l'élément final dans la progression, s'il n'est pas déjà enregistré
                progression = charger_progression()
                if elfinal not in progression.get("elements_decouverts", []):
                    progression["elements_decouverts"].append(elfinal)
                    sauvegarder_progression(progression)
                afficher_victoire_niveau(ecr, niveau, element_final=None)
                act = False
                niveau_complete = True
                
            display.flip()
            clock.tick(60)
        except Exception as e:
            print(f"Erreur dans la boucle principale du jeu: {e}")
            return False
    
    # Sauvegarder les éléments découverts avant de quitter
    if element_decouvert:
        progression = charger_progression()
        # Fusionner les éléments découverts avec ceux déjà enregistrés
        elements_uniques = list(set(progression.get("elements_decouverts", []) + element_decouvert))
        progression["elements_decouverts"] = elements_uniques
        sauvegarder_progression(progression)
    
    return niveau_complete