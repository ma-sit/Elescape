from pygame import *
import sys
import os
import csv
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.menu_interf_jeu import menu_parametres
from interface.menu import bouton
from interface.page_laterale_jeu_combinaisons import Page
from interface.fin_niveau import affichage_victoire

elements = {}

with open('data/csv/encyclopedie.csv', newline='', encoding='utf-8') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=';')
    for row in spamreader:
        row = {k.strip(): v.strip() for k, v in row.items()}  # Nettoie les espaces

        elem_id = row.get("ID")  # Récupération de l'ID
        if elem_id is None or elem_id == "":  
            print("Erreur : ID manquant dans", row)
            continue  # Ignore la ligne si l'ID est absent
            
        elements[int(elem_id)] = {
            "Nom": row.get("Nom", "Inconnu"),
            "Creations": [int(x) for x in row.get("Creations", "").split(',') if x],
            "DR": int(row.get("DR", "0") or "0"),
            "Image": row.get("Image", "")
        }

def get_next_image(c, w):
    c = (c + 1) % len(w)
    return w[c]

def fusionner(element1, element2,nb_fusions):
    if elements[element1]["Nom"] != elements[element2]["Nom"]:
        for element in elements[element1]["Creations"]:
            if element in elements[element2]["Creations"]:
                nb_fusions += 1
                return int(element)  # Retourne l'ID du nouvel élément créé
    return None

def afficher_elements(ecr, elements, elementsbase):
    objets = []
    
    # Parcours des éléments dans elementsbase, qui peut contenir plusieurs instances du même élément
    for elem_id, instances in elementsbase.items():
        if elem_id == 0:  # Ne pas charger l'image du personnage
            continue
        
        if elem_id in elements:
            for instance in instances:
                img = elements[elem_id]["Image"]
                
                if isinstance(img, str):
                    # Parser la chaîne en liste d'images
                    img = [path.strip().strip('"') for path in img.split(',')]
                
                # Si "Image" est une liste, choisir une image aléatoirement
                if isinstance(img, list):
                    img = random.choice(img)
                
                img = image.load(img)  # Charge l'image
                x, y = instance["x"], instance["y"]  # Récupère les coordonnées pour cette instance
                objets.append({
                    "id": elem_id, 
                    "image": img,
                    "original_image": img.copy(),
                    "rect": img.get_rect(topleft=(x, y)), 
                    "x": x, 
                    "y": y, 
                    "selected": False
                })

    # Trie les objets par ordre croissant pour afficher les objets dans l'ordre
    objets.sort(key=lambda obj: obj["rect"].y)
    return objets

def flouter(surface):
    blurred_surface = surface.copy()
    blurred_surface.fill(GRIS, special_flags=BLEND_RGBA_MULT)
    return blurred_surface

def creer_objet(new_id, img, target_obj, objets):

    x_existing, y_existing = target_obj["rect"].center
    w_existing, h_existing = target_obj["rect"].size

    # Liste des emplacements à tester
    offsets = [(w_existing /2, h_existing /2),(0, h_existing /2),(-w_existing /2, h_existing /2),(-w_existing /2, 0),(-w_existing /2, -h_existing /2),(0, -h_existing /2),(w_existing /2, -h_existing /2),(w_existing /2, 0)]
    offset_index = 0

    # Vérifier qu'on place l'objet dans un emplacement libre
    while True:
        offset_x, offset_y = offsets[offset_index]
        new_x, new_y = x_existing + offset_x, y_existing + offset_y
        new_rect = Rect(new_x, new_y, img.get_width(), img.get_height())

        if not any(obj["rect"].colliderect(new_rect) for obj in objets):
            break

        offset_index += 1
        if offset_index >= len(offsets):  
            # Si toutes les directions sont bloquées, on garde l’emplacement d'origine
            new_x, new_y = x_existing + offset_x, y_existing + offset_y
            break
    return {
        "id": new_id,
        "image": img,
        "original_image": img.copy(),
        "rect": img.get_rect(center=(new_x, new_y))
    }

def page_jeu(niveau):
    
    elementsbase = {}
    with open(f'data/csv/niveau{niveau}.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            row = {k.strip(): v.strip() for k, v in row.items()}
            bg = row.get("bg")
            elfinal = row.get("elfinal")
            elfinal = elfinal.strip()
            if bg:
                fnd = image.load(bg).convert()
            elem_id = row.get("elements_base")
            emplacement = row.get("emplacement")
            if elem_id and emplacement:
                try:
                    elem_id = int(elem_id)
                    x, y = map(int, emplacement.split(','))
                    
                    if elem_id not in elementsbase:
                        elementsbase[elem_id] = []

                    elementsbase[elem_id].append({"x": x, "y": y})
                except ValueError:
                    print(f"Erreur de format dans le CSV pour l'élément {elem_id}: {emplacement}")
        
    init()
    ecr = display.set_mode((lrg, htr))
    clock = time.Clock()
    act = True
    selected_obj = None
    selected_obj_h = None
    element_decouvert = [1,3]
    element_discovered = False
    nb_fusions = 0
    start_time = time.get_ticks()
    elfinal = 11
    
    walk_images = [image.load(f"data/images/perso/i{i}.jpg") for i in range(1, 7)]
    x, y = lrg // 2, htr // 2  # Position initiale
    speed = 7  
    current_image = 0
    target_x, target_y = x, y
    moving = False
    objets = afficher_elements(ecr, elements, elementsbase)
    perso_rect = walk_images[0].get_rect(center=(x, y))  # Rect du personnage
    fnd = transform.scale(fnd, (rec.right, rec.bottom))
    target_obj = None
    offset_x, offset_y = 0, 0
    
    while act:
        ecr.blit(fnd, (0, 0))
        
        current_time = time.get_ticks()
        
        for obj in objets:
            ecr.blit(obj["image"], (obj["rect"].x, obj["rect"].y))
            if "enlarge_start" in obj:
                if current_time - obj["enlarge_start"] > 100:
                    obj["image"] = obj["original_image"]
                    obj["rect"] = obj["original_image"].get_rect(center=obj["rect"].center)
                    del obj["enlarge_start"]

        for evt in event.get():
            if evt.type == QUIT:
                return False
            elif evt.type == KEYDOWN and evt.key == K_ESCAPE:
                act = menu_parametres()
            elif evt.type == MOUSEBUTTONDOWN:
                if element_discovered:
                    element_discovered = False
                elif evt.button == 1:
                    if btn_ency["rect"].collidepoint(evt.pos):
                        son_clicmenu.play()
                        Page(ecr)
                    else:
                        for obj in objets:
                            if obj["rect"].collidepoint(evt.pos):
                                selected_obj = obj
                                if "original_image" in obj:
                                    obj["image"] = transform.scale(obj["original_image"], (int(obj["rect"].width * 1.1), int(obj["rect"].height * 1.1)))
                                    obj["rect"] = obj["image"].get_rect(center=obj["rect"].center)
                                offset_x, offset_y = evt.pos[0] - obj["rect"].centerx, evt.pos[1] - obj["rect"].centery
                                break
                elif evt.button == 3:
                    target_x, target_y = mouse.get_pos()
                    moving = True
                    for obj in objets:
                        if obj["rect"].collidepoint(evt.pos):
                            if obj["rect"].collidepoint(evt.pos):
                                obj["enlarge_start"] = time.get_ticks()
                                target_obj = obj
                                orig_w, orig_h = obj["original_image"].get_size()
                                new_size = (int(orig_w * 1.1), int(orig_h * 1.1))
                                obj["image"] = transform.scale(obj["original_image"], new_size)
                                obj["rect"] = obj["image"].get_rect(center=obj["rect"].center)
                                break
            elif evt.type == MOUSEBUTTONUP:
                if evt.button == 1:
                    if selected_obj:
                        if "original_image" in selected_obj:
                            selected_obj["image"] = selected_obj["original_image"]
                            selected_obj["rect"] = selected_obj["image"].get_rect(center=selected_obj["rect"].center)
                            
                        closest_obj = None
                        for obj in objets:
                            if obj != selected_obj and obj["rect"].colliderect(selected_obj["rect"]):
                                if fusionner(obj["id"], selected_obj["id"],nb_fusions) is not None:
                                    closest_obj = obj
                                    break
                        if closest_obj:
                            new_id = fusionner(closest_obj["id"], selected_obj["id"],nb_fusions)
                            if new_id and new_id not in element_decouvert:
                                element_discovered = new_id
                                element_decouvert.append(new_id)
                            if new_id:
                                img = image.load(elements[new_id]["Image"])
                                
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
                                        
                        selected_obj["rect"].center = (evt.pos[0] - offset_x, evt.pos[1] - offset_y)
                        selected_obj["x"], selected_obj["y"] = selected_obj["rect"].center  # Mise à jour de la position de l'objet

                        # Re-trier les objets après le déplacement
                        objets.sort(key=lambda obj: obj["rect"].y)
                    selected_obj = None
            elif evt.type == MOUSEMOTION and selected_obj:
                selected_obj["rect"].move_ip(evt.rel)
                
                            
        if moving:
            dx, dy = target_x - x, target_y - y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > speed:
                x += (dx / distance) * speed
                y += (dy / distance) * speed
            else:
                x, y = target_x, target_y
                moving = False
                
                if target_obj and perso_rect.colliderect(target_obj["rect"]):
                    new_id = fusionner(0, target_obj["id"],nb_fusions)
                    if new_id and new_id not in element_decouvert:
                        element_discovered = new_id
                        element_decouvert.append(new_id)
                    if new_id:
                        img = image.load(elements[new_id]["Image"])
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
                
                    target_obj = None

        perso_rect.center = (x, y)  # Mise à jour de la position du rect du perso
        ecr.blit(get_next_image(current_image, walk_images), perso_rect.topleft)
                                
        for obj in objets:
            ecr.blit(obj["image"], obj["rect"])
        
        if element_discovered:
            if element_discovered == int(elfinal):
                # il faudra ajouter une animation qui affiche l'element final avant d'afficher la page de fin 
                temps_ecoule = time.get_ticks() - start_time
                act = affichage_victoire(niveau, temps_ecoule, nb_fusions, None)
            else:
                # Applique le flou sur l'arrière-plan
                blurred_bg = flouter(ecr)
                ecr.blit(blurred_bg, (0, 0))

                # Chargement et agrandissement de l'image
                img = image.load(elements[element_discovered]["Image"])
                img = transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5)))

                # Centrage de l'image
                element_rect = img.get_rect(center=(lrg // 2, htr // 2 - 50))  # Légèrement remonté pour laisser de la place au texte
                ecr.blit(img, element_rect)

                # Affichage du nom sous l'image
                text = fnt.render(elements[element_discovered]["Nom"], True, (255, 255, 255))  # Texte blanc
                text_rect = text.get_rect(center=(lrg // 2, element_rect.bottom + 20))  # Position sous l'image
                ecr.blit(text, text_rect)

        bouton(ecr, (150, 150, 150) , btn_ency, "Encyclopédie", son_survol, son_clicmenu, r_jeu, surbrillance=BLC)
        

        display.flip()
        clock.tick(60)
    
    return True
