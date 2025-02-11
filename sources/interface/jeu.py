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
        row = {k.strip(): v.strip() for k, v in row.items()}  # Nettoyer les espaces

        elem_id = row.get("ID")  # Récupération de l'ID
        if elem_id is None or elem_id == "":  
            print("Erreur : ID manquant dans", row)
            continue  # Ignore la ligne si l'ID est absent
            
            # Stocker les éléments avec ID comme clé
        elements[int(elem_id)] = {
            "Nom": row.get("Nom", "Inconnu"),
            "Creations": [int(x) for x in row.get("Creations", "").split(',') if x],  # Liste d'IDs
            "DR": int(row.get("DR", "0")),  # 1 ou 0
            "Image": row.get("Image", "")
        }
print("✅ Éléments chargés :", elements)
def get_next_image(c,w):
    c = (c + 1) % len(w)
    return w[c]

def fusionner(element1,element2):
    #Vérifie que les elements sont différents, puis si ils peuvent créer qq chose
    if elements[element1]["Nom"]!=elements[element2]["Nom"]:
        for element in elements[element1]["Creations"]:
            if element in elements[element2]["Creations"]:
                e=int(element)
                # retourne l'élément crée
                return e

def afficher_elements(ecr, elements):
    objets = []
    # Définir une position de base pour les éléments (ex: en ligne)
    positions_initiales = [(100 + i * 150, 500) for i in range(len(elements))]

    for (elem_id, element), (x, y) in zip(elements.items(), positions_initiales):
        if element["Image"]:  # Vérifie qu'une image existe
            objets.append({"id": elem_id, "image": image.load(element["Image"]), "rect":image.load(element["Image"]).get_rect(), "x": x, "y": y, "selected": False})

    return objets

def page_jeu():
    """Affichage du jeu avec déplacement du personnage et interactions avec les éléments."""
    init()
    ecr = display.set_mode((lrg, htr))  # Créer la fenêtre
    clock = time.Clock()
    act = True
    selected_obj = None
    elementsbase=[5,6]
    
    walk_images = [image.load(f"data/images/perso/i{i}.jpg") for i in range(1, 7)]
    x, y = lrg // 2, htr // 2  # Position initiale
    speed = 7  # Vitesse du déplacement
    current_image = 0
    target_x, target_y = x, y  # Position cible
    moving = False
    
    objets = afficher_elements(ecr, elements)
    
    while act:
        ecr.fill(BLC)  # Efface l'écran avec la couleur de fond
        
        for el in elementsbase:
            ecr.blit(image.load(elements[el]["Image"]), (objets[el]["x"], objets[el]["y"]))  # Afficher chaque objet
        
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
                                    "img": image.load(elements[new_id]["Image"]),
                                    "rect": image.load(elements[new_id]["Image"]).get_rect(center=evt.pos)
                                })
                                objets.remove(obj)
                                objets.remove(selected_obj)
                    selected_obj = None
            elif evt.type == MOUSEMOTION and selected_obj:
                selected_obj["rect"].move_ip(evt.rel)

        if moving:
            dx = target_x - x
            dy = target_y - y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > speed:
                x += (dx / distance) * speed
                y += (dy / distance) * speed
            else:
                x, y = target_x, target_y
                moving = False
            ecr.blit(get_next_image(current_image, walk_images), (x - walk_images[0].get_width() // 2, y - walk_images[0].get_height() // 2))
        else:
            ecr.blit(walk_images[0], (x - walk_images[0].get_width() // 2, y - walk_images[0].get_height() // 2))

        for obj in objets:
            ecr.blit(obj["image"], obj["rect"])
        
        display.flip()
        clock.tick(10)
    return True
