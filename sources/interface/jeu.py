from pygame import *
import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

elements = {}

with open('data/csv/encyclopedie.csv', newline='', encoding='utf-8') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=';')
    for row in spamreader:
        row = {k.strip(): v.strip() for k, v in row.items()}  # Nettoie les espaces

        elem_id = row.get("ID")  # Récupération de l'ID
        if elem_id is None or elem_id == "":  
            print("Erreur : ID manquant dans", row)
            continue  # Ignore la ligne si l'ID est absent
            
        # Stocker les éléments avec ID comme clé
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

def afficher_elements(ecr, elements,elementsbase):
    objets = []
    positions_initiales = [(100 + i * 150, 500) for i in range(len(elements))]

    for (elem_id, element), (x, y) in zip(elements.items(), positions_initiales):
        if elem_id == 0:  # Ne pas charger d'image pour le personnage
            continue

        if element["Image"]:
            if elem_id in elementsbase:
                img = image.load(element["Image"])  # Chargement de l'image
                objets.append({
                    "id": elem_id, 
                    "image": img, 
                    "rect": img.get_rect(topleft=(x, y)), 
                    "x": x, 
                    "y": y, 
                    "selected": False
                })

    return objets

def page_jeu(niveau):
    """Affichage du jeu avec déplacement du personnage et interactions avec les éléments."""
    init()
    ecr = display.set_mode((lrg, htr))
    clock = time.Clock()
    act = True
    selected_obj = None
    elementsbase = [5, 6]  # Éléments de départ
    
    walk_images = [image.load(f"data/images/perso/i{i}.jpg") for i in range(1, 7)]
    x, y = lrg // 2, htr // 2  # Position initiale
    speed = 7  
    current_image = 0
    target_x, target_y = x, y
    moving = False
    
    objets = afficher_elements(ecr, elements,elementsbase)
    perso_rect = walk_images[0].get_rect(center=(x, y))  # Rect du personnage
    
    while act:
        ecr.fill(BLC)

        for obj in objets:
            ecr.blit(obj["image"], (obj["rect"].x, obj["rect"].y))

        for evt in event.get():
            if evt.type == QUIT:
                return False
            elif evt.type == KEYDOWN and evt.key == K_ESCAPE:
                act = False
            elif evt.type == MOUSEBUTTONDOWN:
                if evt.button == 1:  # Clic gauche pour déplacer un élément
                    for obj in objets:
                        if obj["rect"].collidepoint(evt.pos):
                            selected_obj = obj
                            break
                elif evt.button == 3:  # Clic droit pour déplacer le personnage
                    target_x, target_y = mouse.get_pos()
                    moving = True
            elif evt.type == MOUSEBUTTONUP and evt.button == 1:
                if selected_obj:
                    for obj in objets:
                        if obj != selected_obj and obj["rect"].colliderect(selected_obj["rect"]):
                            new_id = fusionner(obj["id"], selected_obj["id"])
                            if new_id:
                                objets.append({
                                    "id": new_id,
                                    "image": image.load(elements[new_id]["Image"]),
                                    "rect": image.load(elements[new_id]["Image"]).get_rect(center=evt.pos)
                                })
                                if elements[obj["id"]]["DR"] == 0:
                                    objets.remove(obj)
                                if elements[selected_obj["id"]]["DR"] == 0:
                                    objets.remove(selected_obj)
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

        display.flip()
        clock.tick(30)
    
    return True
