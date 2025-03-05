from pygame import *
import sys
import os
import csv
import random
import json
from math import *  # Utilisation de from math import * comme demandé

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.menu_interf_jeu import menu_parametres
from interface.menu import bouton
from interface.page_laterale_jeu_combinaisons import Page
from interface.parametres import TOUCHES_DEFAUT
from interface.fin_niveau_victoire import afficher_victoire_niveau

# Variables pour le paramètre de volume global
global_volume_general = 1.0
global_volume_musique = 1.0
global_volume_sfx = 1.0

elements = {}

# Séquences d'animation pour les états extra (pour les animaux)
EXTRA_ANIM_SEQUENCES = {
    "sleep": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    "eat":   [0, 1, 2, 3, 2, 3, 2, 3, 2, 1, 0]
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
            file_name = f"{direction}{i}.png"  # ex: down1.png, down2.png, etc.
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
                "Type": row.get("Type", "classique"),  # "animal", "objectif" ou "classique"
                "Mission": row.get("Mission", "")
            }
            if elements[int(elem_id)]["Type"].lower() == "objectif":
                elements[int(elem_id)]["mission_seen"] = False
except Exception as e:
    print(f"Erreur lors du chargement de l'encyclopédie: {e}")
    elements = {0: {"Nom": "Inconnu", "Creations": [], "DR": 0, "Image": "", "Type": "classique", "Mission": ""}}

# Fonction qui renvoie la liste des identifiants communs (sans doublon) entre les "Créations" des deux éléments.
def fusionner_ids(element1, element2):
    common = []
    if element1 not in elements or element2 not in elements:
        return common
    # Ne fusionner que si les noms diffèrent
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
                            "rect": frames["down"][0].get_rect(topleft=(x, y)),
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
                            "rect": img.get_rect(topleft=(x, y)),
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
                            "rect": img.get_rect(topleft=(x, y)),
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

def page_jeu(niveau):
    global global_volume_general, global_volume_musique, global_volume_sfx
    touches = charger_touches()
    elementsbase = {}
    niveau_complete = False
    elfinal = None

    # Définir la résolution de référence et calculer les facteurs d'échelle
    reference_width, reference_height = 1920, 1080
    # rec est supposé définir la taille de l'écran (par exemple via rec.right et rec.bottom)
    current_width, current_height = rec.right, rec.bottom
    scale_x = current_width / reference_width
    scale_y = current_height / reference_height
    # Pour les images, on utilise un facteur commun pour préserver les proportions
    scale_common = min(scale_x, scale_y)

    try:
        with open(f'data/csv/niveau{niveau}.csv', newline='', encoding='utf-8') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=';')
            bg_loaded = False
            for row in spamreader:
                row = {k.strip(): v.strip() for k, v in row.items()}
                bg = row.get("bg")
                ef = row.get("elfinal")  # Élément final pour gagner
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
        elfinal = 11
        base_elements = [1, 3, 7]
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
    element_decouvert = [1, 3]
    element_discovered = False

    # Charger les frames du personnage (perso) – 4 frames par direction avec échelle
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

    # Position initiale du perso (centre)
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

    # Charger l'image de base de la bulle pour l'objectif
    try:
        bubble_img = image.load("data/images/autres/bulle.png").convert_alpha()
    except Exception as e:
        print(f"Erreur lors du chargement de la bulle : {e}")
        bubble_img = Surface((100, 50))
        bubble_img.fill((255,255,255))

    # Titre du niveau
    niveau_titre_font = font.Font(None, 40)
    niveau_titre = niveau_titre_font.render(f"Niveau {niveau}", True, (255,255,255))
    niveau_titre_rect = niveau_titre.get_rect(midtop=(current_width//2, 10))

    while act:
        try:
            ecr.blit(fnd, (0, 0))
            ecr.blit(niveau_titre, niveau_titre_rect)
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
                                game_screen = ecr.copy()
                                act = menu_parametres(game_screen)
                elif evt.type == MOUSEBUTTONDOWN:
                    if element_discovered:
                        element_discovered = False
                    elif evt.button == 1:
                        # Utilisation de reversed(objets) pour sélectionner l'objet affiché par-dessus
                        if btn_ency["rect"].collidepoint(evt.pos):
                            son_survol.play()
                            Page(ecr, elements, element_decouvert)
                        else:
                            for obj in reversed(objets):
                                if obj["rect"].collidepoint(evt.pos):
                                    selected_obj = obj
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
                                                # Appliquer un décalage pour le deuxième objet
                                                offset = new_obj["rect"].width // 2 + 10
                                                center = (closest_obj["rect"].centerx + offset, closest_obj["rect"].centery)
                                                objets.append(new_obj)
                                                # Retirer les éléments fusionnés selon DR
                                                if elements[selected_obj["id"]]["DR"] == 0 and selected_obj in objets:
                                                    objets.remove(selected_obj)
                                                if elements[closest_obj["id"]]["DR"] == 0 and closest_obj in objets:
                                                    objets.remove(closest_obj)
                                        except Exception as e:
                                            print(f"Erreur lors de la fusion d'éléments: {e}")
                            selected_obj["rect"].center = (evt.pos[0] - offset_x, evt.pos[1] - offset_y)
                            selected_obj["x"], selected_obj["y"] = selected_obj["rect"].center
                            objets.sort(key=lambda obj: obj["rect"].bottom)
                        selected_obj = None
                    elif evt.button == BUTTON_RIGHT:
                        if target_obj and target_obj.get("is_animal", False):
                            target_obj["selected"] = False
                            base_frame = target_obj["frames"][target_obj["current_direction"]][0]
                            target_obj["image"] = base_frame
                            target_obj["rect"] = base_frame.get_rect(center=target_obj["rect"].center)
                            target_obj["last_move_time"] = time.get_ticks()
                            target_obj["state"] = "idle"
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
                                offset = new_obj["rect"].width // 2 + 10
                                center = (target_obj["rect"].centerx + offset, target_obj["rect"].centery)
                                objets.append(new_obj)
                                if elements[target_obj["id"]]["DR"] == 0:
                                    if target_obj in objets:
                                        objets.remove(target_obj)
                        except Exception as e:
                            print(f"Erreur lors de la fusion avec le personnage: {e}")
                target_obj = None

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
            for o in all_objs:
                ecr.blit(o["image"], o["rect"])
            
            # Affichage de l'objectif : pour chaque objet objectif, afficher une bulle en haut à droite
            for obj in objets:
                if obj.get("is_objectif", False):
                    bubble_x = obj["rect"].right + 35
                    bubble_y = obj["rect"].top - 20
                    if not elements[obj["id"]].get("mission_seen", False):
                        small_bubble = transform.scale(bubble_img, (50, 50))
                        ecr.blit(small_bubble, (bubble_x - small_bubble.get_width(), bubble_y))
                        exclam_text = fnt.render("!", True, (255, 0, 0))
                        exclam_x = bubble_x - small_bubble.get_width() + (small_bubble.get_width() - exclam_text.get_width()) // 2
                        exclam_y = bubble_y + (small_bubble.get_height() - exclam_text.get_height()) // 2
                        ecr.blit(exclam_text, (exclam_x, exclam_y))
                    if perso_rect.colliderect(obj["rect"]):
                        large_bubble = transform.scale(bubble_img, (200, 200))
                        bubble_x_final = obj["rect"].right - large_bubble.get_width() + 200
                        bubble_y_final = obj["rect"].top - 150
                        ecr.blit(large_bubble, (bubble_x_final, bubble_y_final))
                        mission_text = elements[obj["id"]].get("Mission", "Objectif non défini")
                        mission_text = wrap_text(mission_text, max_chars=10)
                        lines = mission_text.split("\n")
                        y_offset = 0
                        for line in lines:
                            text_surface = fnt.render(line, True, (0, 0, 0))
                            ecr.blit(text_surface, (bubble_x_final + (large_bubble.get_width() - text_surface.get_width()) // 2,
                                                     bubble_y_final + y_offset + 35))
                            y_offset += text_surface.get_height() + 2
                        elements[obj["id"]]["mission_seen"] = True

            hover_ency = bouton(ecr, (150, 150, 150), btn_ency, "Encyclopédie", son_survol, son_clicmenu, r_jeu, surbrillance=BLC)
            display.flip()
            clock.tick(60)
        except Exception as e:
            print(f"Erreur dans la boucle principale du jeu: {e}")
            return False
    
    return niveau_complete
