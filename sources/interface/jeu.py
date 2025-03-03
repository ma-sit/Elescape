from pygame import *
import sys
import os
import csv
import random
import json
import math as m  # Pour utiliser m.pi, m.cos, etc.

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.menu_interf_jeu import menu_parametres
from interface.menu import bouton
from interface.page_laterale_jeu_combinaisons import Page
from interface.parametres import TOUCHES_DEFAUT

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
    angle = m.degrees(m.atan2(dy, dx))
    if -45 <= angle < 45:
        return "right"
    elif 45 <= angle < 135:
        return "down"
    elif -135 <= angle < -45:
        return "up"
    else:
        return "left"

# Fonction pour charger les frames d'animation du personnage depuis un dossier.
def charger_frames_perso_from_folder(folder_path, directions=("down", "left", "right", "up"), nb_frames=4):
    frames = {}
    for direction in directions:
        frames[direction] = []
        for i in range(1, nb_frames+1):
            file_name = f"{direction}{i}.png"  # ex: down1.png, down2.png, etc.
            full_path = os.path.join(folder_path, file_name)
            try:
                frame = image.load(full_path).convert_alpha()
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
                "Type": row.get("Type", "classique")  # "animal" ou "classique"
            }
except Exception as e:
    print(f"Erreur lors du chargement de l'encyclopédie: {e}")
    elements = {0: {"Nom": "Inconnu", "Creations": [], "DR": 0, "Image": "", "Type": "classique"}}

def get_next_image(c, w):
    c = (c + 1) % len(w)
    return w[c], c

def fusionner(element1, element2):
    if element1 not in elements or element2 not in elements:
        return None
    if elements[element1]["Nom"] != elements[element2]["Nom"]:
        for element in elements[element1]["Creations"]:
            if element in elements[element2]["Creations"]:
                return int(element)
    return None

# Charger les frames d'un animal depuis un dossier
def charger_frames_animal_from_folder(folder_path, nb_frames=4, directions=("down", "left", "right", "up"), extras=("sleep", "eat")):
    frames = {}
    for direction in directions:
        frames[direction] = []
        for i in range(1, nb_frames+1):
            file_name = f"{direction}{i}.png"
            full_path = os.path.join(folder_path, file_name)
            try:
                frame = image.load(full_path).convert_alpha()
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
                frames[extra].append(frame)
            except Exception as e:
                print(f"Erreur lors du chargement de {full_path}: {e}")
    return frames

def afficher_elements(ecr, elements, elementsbase):
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
                    img_paths = [path.strip().strip('"') for path in img_path.split(',')]
                else:
                    img_paths = [img_path]
                if not img_paths:
                    print(f"Erreur: Aucun chemin d'image valide pour l'élément {elem_id}")
                    continue
                x, y = instance["x"], instance["y"]
                if elements[elem_id].get("Type", "").lower() == "animal":
                    try:
                        frames = charger_frames_animal_from_folder(img_paths[0])
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
                else:
                    try:
                        img_choice = random.choice(img_paths)
                        img = image.load(img_choice)
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

    try:
        with open(f'data/csv/niveau{niveau}.csv', newline='', encoding='utf-8') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=';')
            bg_loaded = False
            for row in spamreader:
                row = {k.strip(): v.strip() for k, v in row.items()}
                bg = row.get("bg")
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
                        x, y = map(int, emplacement.split(','))
                        if elem_id not in elementsbase:
                            elementsbase[elem_id] = []
                        elementsbase[elem_id].append({"x": x, "y": y})
                    except ValueError as e:
                        print(f"Erreur de format dans le CSV pour l'élément {elem_id}: {emplacement} - {e}")
            if not bg_loaded:
                print("Aucun fond trouvé, utilisation d'un fond par défaut")
                fnd = Surface((lrg, htr))
                fnd.fill((50, 50, 70))
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

    # Charger les frames du personnage (perso) – 4 frames par direction
    try:
        perso_frames = charger_frames_perso_from_folder("data/images/perso")
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

    # Initialisation de la position du perso (centre)
    x, y = lrg // 2, htr // 2
    speed = 7
    current_image = 0  # Anciennement utilisé pour walk_images, non utilisé ici
    target_x, target_y = x, y
    moving = False

    try:
        objets = afficher_elements(ecr, elements, elementsbase)
    except Exception as e:
        print(f"Erreur lors de l'affichage des éléments: {e}")
        objets = []
        
    perso_rect = perso_frames["down"][0].get_rect(center=(x, y))
    fnd = transform.scale(fnd, (rec.right, rec.bottom))
    target_obj = None
    offset_x, offset_y = 0, 0

    while act:
        try:
            ecr.blit(fnd, (0, 0))
            current_time = time.get_ticks()
            
            # Affichage des éléments classiques
            for obj in objets:
                if not obj.get("is_animal", False):
                    ecr.blit(obj["image"], (obj["rect"].x, obj["rect"].y))
                    if "enlarge_start" in obj:
                        if current_time - obj["enlarge_start"] > 100:
                            obj["image"] = obj["original_image"]
                            obj["rect"] = obj["original_image"].get_rect(center=obj["rect"].center)
                            del obj["enlarge_start"]
            
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
                        if btn_ency["rect"].collidepoint(evt.pos):
                            son_clicmenu.play()
                            Page(ecr, elements, element_decouvert)
                        else:
                            for obj in objets:
                                if obj["rect"].collidepoint(evt.pos):
                                    selected_obj = obj
                                    # Pour l'animal, agrandir uniquement une fois
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
                        for obj in objets:
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
                                    if fusionner(obj["id"], selected_obj["id"]) is not None:
                                        closest_obj = obj
                                        break
                            if closest_obj:
                                new_id = fusionner(closest_obj["id"], selected_obj["id"])
                                if new_id and new_id not in element_decouvert:
                                    element_discovered = new_id
                                    element_decouvert.append(new_id)
                                if new_id:
                                    try:
                                        img_paths = elements[new_id]["Image"].split(',')
                                        if img_paths:
                                            img_path = random.choice([path.strip().strip('"') for path in img_paths])
                                            img = image.load(img_path)
                                            if elements[closest_obj["id"]]["DR"] == 0 or elements[selected_obj["id"]]["DR"] == 0:
                                                nouvel_objet = {
                                                    "id": new_id,
                                                    "image": img,
                                                    "original_image": img.copy(),
                                                    "rect": img.get_rect(center=closest_obj["rect"].center)
                                                }
                                                objets.append(nouvel_objet)
                                            else:
                                                objets.append(creer_objet(new_id, img, selected_obj, objets))
                                            if elements[closest_obj["id"]]["DR"] == 0:
                                                objets.remove(closest_obj)
                                            if elements[selected_obj["id"]]["DR"] == 0:
                                                if selected_obj in objets:
                                                    objets.remove(selected_obj)
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
                # Déterminer la direction du déplacement
                if dx != 0 or dy != 0:
                    perso_current_direction = get_direction(dx, dy)
                if current_time - perso_last_anim_time > perso_anim_delay:
                    perso_anim_index = (perso_anim_index + 1) % len(perso_frames[perso_current_direction])
                    perso_last_anim_time = current_time
                ecr.blit(perso_frames[perso_current_direction][perso_anim_index], perso_rect.topleft)
            else:
                perso_rect.center = (x, y)
                ecr.blit(perso_frames[perso_current_direction][0], perso_rect.topleft)

            # Fusion automatique entre le perso et un élément cible
            if target_obj and perso_rect.colliderect(target_obj["rect"]) and not moving:
                new_id = fusionner(0, target_obj["id"])
                if new_id and new_id not in element_decouvert:
                    element_discovered = new_id
                    element_decouvert.append(new_id)
                if new_id:
                    try:
                        img_paths = elements[new_id]["Image"].split(',')
                        if img_paths:
                            img_path = random.choice([path.strip().strip('"') for path in img_paths])
                            img = image.load(img_path)
                            if elements[target_obj["id"]]["DR"] == 0:
                                nouvel_objet = {
                                    "id": new_id,
                                    "image": img,
                                    "original_image": img.copy(),
                                    "rect": img.get_rect(center=target_obj["rect"].center)
                                }
                                objets.append(nouvel_objet)
                                objets.remove(target_obj)
                            else:
                                objets.append(creer_objet(new_id, img, target_obj, objets))
                    except Exception as e:
                        print(f"Erreur lors de la fusion avec le personnage: {e}")
                target_obj = None

            # Mise à jour du mouvement et de l'animation des animaux (identique aux versions précédentes)
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
                                    angle = random.uniform(0, 2 * m.pi)
                                    offset = random.randint(120, 200)
                                    tg_x = cx + offset * m.cos(angle)
                                    tg_y = cy + offset * m.sin(angle)
                                    tg_x = max(0, min(tg_x, lrg))
                                    tg_y = max(0, min(tg_y, htr))
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
                                    new_cx = max(0, min(new_cx, lrg))
                                    new_cy = max(0, min(new_cy, htr))
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
            
            for obj in objets:
                ecr.blit(obj["image"], obj["rect"])
            
            if element_discovered:
                blurred_bg = flouter(ecr)
                ecr.blit(blurred_bg, (0, 0))
                try:
                    img_paths = elements[element_discovered]["Image"].split(',')
                    if img_paths:
                        img_path = random.choice([path.strip().strip('"') for path in img_paths])
                        img = image.load(img_path)
                        img = transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5)))
                        element_rect = img.get_rect(center=(lrg // 2, htr // 2 - 50))
                        ecr.blit(img, element_rect)
                        text = fnt.render(elements[element_discovered]["Nom"], True, (255, 255, 255))
                        text_rect = text.get_rect(center=(lrg // 2, element_rect.bottom + 20))
                        ecr.blit(text, text_rect)
                except Exception as e:
                    print(f"Erreur lors de l'affichage de l'élément découvert: {e}")
                    element_discovered = False
            
            hover_ency = bouton(ecr, (150, 150, 150), btn_ency, "Encyclopédie", son_survol, son_clicmenu, r_jeu, surbrillance=BLC)
            display.flip()
            clock.tick(60)
        except Exception as e:
            print(f"Erreur dans la boucle principale du jeu: {e}")
            return False
    
    return True
