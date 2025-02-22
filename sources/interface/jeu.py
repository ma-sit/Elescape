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

def fusionner(element1, element2):
    if elements[element1]["Nom"] != elements[element2]["Nom"]:
        for element in elements[element1]["Creations"]:
            if element in elements[element2]["Creations"]:
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

    # Trie les objets par ordre croissant de la coordonnée y (du plus bas au plus haut)
    objets.sort(key=lambda obj: obj["rect"].y)
    
    return objets

def flouter(surface):
    """Applique un flou simple à l'image (en la rendant plus opaque et en lui ajoutant un filtre)."""
    blurred_surface = surface.copy()
    blurred_surface.fill(GREY, special_flags=pygame.BLEND_RGBA_MULT)  # Applique un flou simple
    return blurred_surface

def page_jeu(niveau):
    """Affichage du jeu avec déplacement du personnage et interactions avec les éléments."""
    
    elementsbase = {}

    # Chargement des éléments de base
    with open(f'data/csv/niveau{niveau}.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            row = {k.strip(): v.strip() for k, v in row.items()}
            bg = row.get("bg")
            if bg:
                fnd = image.load(bg).convert()
            elem_id = row.get("elements_base")
            emplacement = row.get("emplacement")
            if elem_id and emplacement:
                try:
                    elem_id = int(elem_id)
                    x, y = map(int, emplacement.split(','))
                    
                    if elem_id not in elementsbase:
                        elementsbase[elem_id] = []  # Crée une liste si l'élément n'existe pas encore

                    elementsbase[elem_id].append({"x": x, "y": y})  # Ajoute une nouvelle instance
                except ValueError:
                    print(f"Erreur de format dans le CSV pour l'élément {elem_id}: {emplacement}")
        
    init()
    ecr = display.set_mode((lrg, htr))
    clock = time.Clock()
    act = True
    selected_obj = None
    element_discovered = False
    
    walk_images = [image.load(f"data/images/perso/i{i}.jpg") for i in range(1, 7)]
    x, y = lrg // 2, htr // 2  # Position initiale
    speed = 7  
    current_image = 0
    target_x, target_y = x, y
    moving = False
    
    objets = afficher_elements(ecr, elements, elementsbase)
    perso_rect = walk_images[0].get_rect(center=(x, y))  # Rect du personnage
    
    fnd = transform.scale(fnd, (rec.right, rec.bottom))
    
    offset_x, offset_y = 0, 0
    
    while act:
        ecr.blit(fnd, (0, 0))
        
        for obj in objets:
            ecr.blit(obj["image"], (obj["rect"].x, obj["rect"].y))

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
                elif evt.button == 3:  # Clic droit pour déplacer le personnage
                    target_x, target_y = mouse.get_pos()
                    moving = True
            elif evt.type == MOUSEBUTTONUP and evt.button == 1:
                if selected_obj:
                    for obj in objets:
                        if "original_image" in obj:
                            selected_obj["image"] = selected_obj["original_image"]
                            selected_obj["rect"] = selected_obj["image"].get_rect(center=selected_obj["rect"].center)
                        if obj != selected_obj and obj["rect"].colliderect(selected_obj["rect"]):
                            new_id = fusionner(obj["id"], selected_obj["id"])
                            print(evt)
                            if new_id:
                                img = image.load(elements[new_id]["Image"])
                                nouvel_objet = {
                                    "id": new_id,
                                    "image": img,
                                    "original_image": img.copy(),
                                    "rect": img.get_rect(center=evt.pos)
                                }
                                objets.append(nouvel_objet)
                                if elements[obj["id"]]["DR"] == 0:
                                    objets.remove(obj)
                                if elements[selected_obj["id"]]["DR"] == 0:
                                    objets.remove(selected_obj)
                    # Déplacer l'objet et mettre à jour sa position
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

        perso_rect.center = (x, y)  # Mise à jour de la position du rect du personnage
        ecr.blit(get_next_image(current_image, walk_images), perso_rect.topleft)

        # Vérifier la collision entre le personnage et les objets
        for obj in objets[:]:  # Copie de la liste pour éviter modification en boucle
            if perso_rect.colliderect(obj["rect"]):
                new_id = fusionner(0, obj["id"])  # Fusionner l'humain avec l'objet
                if new_id:
                    objets.append({
                        "id": new_id,
                        "image": image.load(elements[new_id]["Image"]),
                        "rect": image.load(elements[new_id]["Image"]).get_rect(center=(x, y))
                    })
                    if elements[obj["id"]]["DR"] == 0:
                        objets.remove(obj)

        for obj in objets:
            ecr.blit(obj["image"], obj["rect"])
        
        if element_discovered:
            # Applique le flou sur l'arrière-plan
            blurred_bg = flouter(ecr)
            ecr.blit(blurred_bg, (0, 0))

            # Affiche l'élément découvert au centre
            element_rect = discovered_element.get_rect(center=(lrg // 2, htr // 2))
            ecr.blit(discovered_element, element_rect)
        
        hover_ency = bouton(ecr, (150, 150, 150) , btn_ency, "Encyclopédie", son_survol, son_clicmenu, r_jeu, surbrillance=BLC)
            

        display.flip()
        clock.tick(60)
    
    return True
