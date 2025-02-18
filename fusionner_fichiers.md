filename:**main.py**
````py
from pygame import *
import sys
import json
from shared.components.config import *
from interface.menu import bouton,dessiner_menu, plein_ecran
from interface.selection_niveau import selection_niveau
from interface.parametres import page_parametres

# Initialisation
init()

# Chargement des touches
try:
    with open("data/touches.json", "r") as f:
        touches = json.load(f)
except:
    touches = {
        'Déplacement': BUTTON_RIGHT,
        'Action': K_SPACE,
        'Retour': K_ESCAPE,
        'Plein écran': K_f,
        'Paramètres': K_s,
        'Jouer': K_p,
        'Quitter': K_q
    }


# Boucle principale
act = True
while act:
    dessiner_menu(ecr)
    
    for evt in event.get():
        if evt.type == QUIT:
            act = False
        if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
            if btn_jeu["rect"].collidepoint(evt.pos):
                son_clicmenu.play()
                act = selection_niveau()
            elif btn_cfg["rect"].collidepoint(evt.pos):
                son_clicmenu.play()
                act = page_parametres()
            elif btn_fin["rect"].collidepoint(evt.pos):
                son_clicmenu.play()
                act = False
        if evt.type == KEYDOWN:
            if evt.key == touches['Jouer']:
                act = selection_niveau()
            elif evt.key == touches['Paramètres']:
                act = page_parametres()
            elif evt.key == touches['Quitter']:
                act = False
    display.flip()
    time.delay(30)

quit()
sys.exit()
````

filename:**data\touches.json**
````json
{"D\u00c3\u00a9placement": 3, "Action": 32, "Retour": 27, "Plein \u00c3\u00a9cran": 102, "Param\u00c3\u00a8tres": 115, "Jouer": 112, "Quitter": 113}
````

filename:**data\csv\encyclopedie.csv**
````csv
ID;Nom;Creations;DR;Image
0;Humain;6,5,9,16,18;1;
1;Seau d'eau;4;0;data/images/seau_d'eau.png
2;Graine;4;0;data/images/graine.png
3;Pierre;6;1;data/images/pierre.png
4;Plante;5;0;data/images/plante.png
5;Bois;7,11;1;data/images/bois.png
6;Etincelles;7;0;data/images/etincelles.png
7;Chaleur;8;0;data/images/chaleur.png
8;Metal;9,12;0;data/images/metal.png
9;Cle;8;1;data/images/cle.png
10;Seau;8;0;
11;Pioche;;1;
12;Lame;11;0;
13;Pierre lisse;12;0;
14;Fruits;16;;
15;Feu;8;0;
16;Cuisiner;15;0;
17;Gaz;15;0;
18;Energie;17;0;
19;Terre;13;0;
20;Air;18,13;1;
21;Eau;17;0;

````

filename:**interface\jeu.py**
````py
from pygame import *
import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.menu_interf_jeu import menu_parametres

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
                act = menu_parametres()
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

````

filename:**interface\menu.py**
````py
from pygame import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def bouton(ecr, couleur, btn, texte, son_survol, son_click, surbrillance=None):
    """Dessine un bouton interactif avec sons et coins arrondis"""
    rect = btn["rect"]  # Récupérer le pygame.Rect
    survole = rect.collidepoint(mouse.get_pos())

    if survole:
        couleur = surbrillance if surbrillance else couleur
        if not btn["a_joue_son"]:  # Vérifie si le son n'a pas encore été joué
            son_survol.play()
            btn["a_joue_son"] = True
    else:
        btn["a_joue_son"] = False  # Réinitialise quand la souris quitte le bouton

    draw.rect(ecr, couleur, rect, border_radius=15)  # Dessiner le bouton arrondi
    txt_rendu = fnt.render(texte, True, (255, 255, 255))
    ecr.blit(txt_rendu, (rect.x + (rect.width - txt_rendu.get_width()) // 2, rect.y + 10))

    return survole



def dessiner_menu(ecr):
    """Affiche le menu principal"""
    
    ecr.fill(BLC)
    
    hover_jeu = bouton(ecr, NOR, btn_jeu, "Jouer", son_survol, son_clicmenu, surbrillance=(150, 150, 150))
    hover_cfg = bouton(ecr, NOR, btn_cfg, "Paramètres", son_survol, son_clicmenu, surbrillance=(150, 150, 150))
    hover_fin = bouton(ecr, NOR, btn_fin, "Quitter", son_survol, son_clicmenu, surbrillance=(150, 150, 150))
    
    """Titre du jeu"""
    rect_titre = Rect(0, 0, 550, 100)  # Zone du titre (ajuste si besoin)
    rect_titre.center = (ecr.get_width() // 2, 290)  # Centrer

    survol_titre = rect_titre.collidepoint(mouse.get_pos())
    
    titre_agrandi = False
    taille_titre = 200  # Taille normale du titre
    taille_titre_max = 250  # Taille agrandie

    # 🔹 Ajustement de la taille
    if survol_titre and not titre_agrandi:
        taille_titre = min(taille_titre + 8, taille_titre_max)  # Grandit progressivement
        titre_agrandi = True
    elif not survol_titre and titre_agrandi:
        taille_titre = max(taille_titre - 8, 60)  # Revient à la taille normale
        titre_agrandi = False

    # 🔹 Affichage du titre
    police_titre = font.Font(None, taille_titre)  # Appliquer la taille dynamique
    txt_titre = police_titre.render("Vitanox", True, (0, 0, 0))  # Blanc
    rect_titre = txt_titre.get_rect(center=(ecr.get_width() // 2, 300))  # Centrer
    ecr.blit(txt_titre, rect_titre)
    
    

def plein_ecran():
    """Bascule plein écran"""
    global ecr
    if display.get_surface().get_flags() & FULLSCREEN:
        ecr = display.set_mode((lrg, htr), RESIZABLE)
    else:
        ecr = display.set_mode((0, 0), FULLSCREEN)

````

filename:**interface\menu_interf_jeu.py**
````py
from pygame import *
import json
from shared.components.config import *

def menu_parametres():
    """Menu des paramètres qui s'affiche par-dessus le niveau"""
    # Chargement des touches
    try:
        with open("data/touches.json", "r") as f:
            touches = json.load(f)
    except:
        touches = {
            'Retour': K_ESCAPE
        }
    
    menu_actif = True
    menu_width = 300
    menu_height = 200
    menu_x = (lrg - menu_width) // 2
    menu_y = (htr - menu_height) // 2
    button_width = 120
    button_height = 40
    button_x = menu_x + (menu_width - button_width) // 2
    button_y = menu_y + menu_height - button_height - 20
    quit_button = Rect(button_x, button_y, button_width, button_height)
    
    while menu_actif:
        surf_overlay = Surface((lrg, htr), SRCALPHA)
        surf_overlay.fill((0, 0, 0, 128))
        ecr.blit(surf_overlay, (0, 0))
        
        draw.rect(ecr, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height))
        draw.rect(ecr, BLC, (menu_x, menu_y, menu_width, menu_height), 2)
        
        titre = font.Font(None, 36).render("Parameters", True, BLC)
        titre_rect = titre.get_rect(center=(menu_x + menu_width//2, menu_y + 30))
        ecr.blit(titre, titre_rect)
        
        draw.rect(ecr, (150, 150, 150), quit_button)
        draw.rect(ecr, BLC, quit_button, 2)
        quit_text = font.Font(None, 32).render("Quit", True, BLC)
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        ecr.blit(quit_text, quit_text_rect)
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == touches['Retour']:
                menu_actif = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if quit_button.collidepoint(evt.pos):
                    return False
    
    return True

````

filename:**interface\parametres.py**
````py
from pygame import *
from shared.components.config import *
import json

def page_parametres():
    """Page des paramètres"""
    act = True
    volume_general = mixer.music.get_volume()
    volume_musique = mixer.music.get_volume()
    volume_sfx = mixer.music.get_volume()
    clic_souris = False
    barre_active = None
    horloge = time.Clock()
    section_active = "Audio"
    
    # Chargement des touches
    try:
        with open("data/touches.json", "r") as f:
            touches = json.load(f)
    except:
        touches = {
            'Déplacement': BUTTON_RIGHT,
            'Action': K_SPACE,
            'Retour': K_ESCAPE,
            'Plein écran': K_f,
            'Paramètres': K_s,
            'Jouer': K_p,
            'Quitter': K_q
        }
    touche_active = None

    while act:
        ecr.fill(NOR)
        
        # Titre
        afficher_texte("Paramètres", lrg // 2, 100, police_titre, BLC)

        # Position des boutons du menu
        positions_boutons = [
            ("Audio", lrg // 2 - 170),
            ("Interface", lrg // 2),
            ("Touches", lrg // 2 + 170)
        ]

        # Dessiner les boutons du menu
        for texte, x in positions_boutons:
            couleur = BLEU if texte == section_active else BLC
            rect_bouton = Rect(x - 75, 150, 150, 40)
            draw.rect(ecr, couleur, rect_bouton)
            afficher_texte(texte, x, 170, police_options, NOR)

        # Section Audio
        if section_active == "Audio":
            # Afficher les textes des volumes
            afficher_texte(f"Volume général : {int(volume_general * 100)}%", 
                         barre_x, barre_y_general - 30, police_options, BLEU, "left")
            afficher_texte(f"Volume musique : {int(volume_musique * 100)}%", 
                         barre_x, barre_y_musique - 30, police_options, BLEU, "left")
            afficher_texte(f"Volume interface : {int(volume_sfx * 100)}%", 
                         barre_x, barre_y_sfx - 30, police_options, BLEU, "left")

            # Barres de volume
            for volume, y_pos in [(volume_general, barre_y_general),
                                (volume_musique, barre_y_musique),
                                (volume_sfx, barre_y_sfx)]:
                rect_barre = Rect(barre_x, y_pos, barre_largeur, barre_hauteur)
                draw.rect(ecr, BLC, rect_barre)
                if volume > 0:
                    rect_rempli = Rect(barre_x, y_pos, int(barre_largeur * volume), barre_hauteur)
                    draw.rect(ecr, BLEU, rect_rempli)

        # Section Touches
        elif section_active == "Touches":
            y_pos = 250
            espacement = 80
            
            for nom, code in touches.items():
                rect_touche = Rect(lrg//2 - 200, y_pos, 400, 60)
                couleur = BLEU if touche_active == nom else BLC
                draw.rect(ecr, NOR, rect_touche)
                draw.rect(ecr, couleur, rect_touche, 2)
                
                if nom == "Déplacement":
                    nom_touche = "Clic droit" if code == BUTTON_RIGHT else "Clic gauche"
                else:
                    nom_touche = key.name(code).upper()
                    
                afficher_texte(f"{nom} : {nom_touche}", 
                             lrg//2, y_pos + 30, police_options, couleur)
                y_pos += espacement

            if touche_active:
                afficher_texte("Appuyez sur une touche...", 
                             lrg // 2, 550, police_options, BLEU)
            else:
                afficher_texte("Cliquez sur une touche à modifier", 
                             lrg // 2, 550, police_options, BLEU)

        afficher_texte("Retour (Échap)", lrg // 2, 550, police_options, BLEU)

        for evt in event.get():
            if evt.type == QUIT:
                with open("data/touches.json", "w") as f:
                    json.dump(touches, f)
                return False

            if evt.type == KEYDOWN:
                if touche_active:
                    if touche_active != "Déplacement":
                        touches[touche_active] = evt.key
                        with open("data/touches.json", "w") as f:
                            json.dump(touches, f)
                        touche_active = None
                elif evt.key == K_ESCAPE:
                    with open("data/touches.json", "w") as f:
                        json.dump(touches, f)
                    act = False

            if evt.type == MOUSEBUTTONDOWN:
                x, y = evt.pos
                
                # Gestion des clics sur les boutons du menu
                if 150 <= y <= 190:
                    for texte, pos_x in positions_boutons:
                        if pos_x - 75 <= x <= pos_x + 75:
                            section_active = texte
                
                # Gestion des touches
                if section_active == "Touches":
                    y_pos = 250
                    for nom in touches:
                        rect_touche = Rect(lrg//2 - 200, y_pos, 400, 60)
                        if rect_touche.collidepoint(x, y):
                            touche_active = nom
                            if nom == "Déplacement":
                                touches[nom] = evt.button
                                with open("data/touches.json", "w") as f:
                                    json.dump(touches, f)
                                touche_active = None
                        y_pos += espacement

                # Gestion des barres de volume
                if section_active == "Audio":
                    if barre_x <= x <= barre_x + barre_largeur:
                        if barre_y_general <= y <= barre_y_general + barre_hauteur:
                            barre_active = "general"
                            clic_souris = True
                        elif barre_y_musique <= y <= barre_y_musique + barre_hauteur:
                            barre_active = "musique"
                            clic_souris = True
                        elif barre_y_sfx <= y <= barre_y_sfx + barre_hauteur:
                            barre_active = "sfx"
                            clic_souris = True

            if evt.type == MOUSEBUTTONUP:
                clic_souris = False
                barre_active = None

            if evt.type == MOUSEMOTION and clic_souris and section_active == "Audio":
                x = evt.pos[0]
                nouveau_volume = max(0.0, min(1.0, (x - barre_x) / barre_largeur))
                if barre_active == "general":
                    volume_general = nouveau_volume
                elif barre_active == "musique":
                    volume_musique = nouveau_volume
                elif barre_active == "sfx":
                    volume_sfx = nouveau_volume

                volume_musique_final = volume_musique * volume_general
                volume_sfx_final = volume_sfx * volume_general
                mixer.music.set_volume(volume_musique_final)
                son_clic.set_volume(volume_sfx_final)

        display.flip()
        horloge.tick(30)
        
    return True

def afficher_texte(texte, x, y, plc, couleur, align="center"):
    surface_texte = plc.render(texte, True, couleur)
    rect_texte = surface_texte.get_rect()
    if align == "center":
        rect_texte.center = (x, y)
    elif align == "right":
        rect_texte.midright = (x, y)
    elif align == "left":
        rect_texte.midleft = (x, y)
    ecr.blit(surface_texte, rect_texte)

````

filename:**interface\selection_niveau.py**
````py
from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.jeu import page_jeu

def create_button(x, y, width, height, text):
    button_rect = Rect(x, y, width, height)
    button_text = font.Font(None, 36).render(text, True, (255, 255, 255))
    text_rect = button_text.get_rect(center=button_rect.center)
    return (button_rect, button_text, text_rect)

def selection_niveau():
    running = True
    
    # Dimensions et style
    button_width = 120
    button_height = 50
    padding = 20
    
    # Titres
    title_font = font.Font(None, 100)
    subtitle_font = font.Font(None, 60)
    title = title_font.render("VITANOX", True, (255, 255, 255))
    subtitle = subtitle_font.render("Select your level", True, (255, 255, 255))
    
    # Position des titres
    title_rect = title.get_rect(center=(lrg//2, htr//4))
    subtitle_rect = subtitle.get_rect(center=(lrg//2, htr//4 + 80))
    
    # Calcul positions des boutons
    total_width = 5 * (button_width + padding) - padding
    start_x = (lrg - total_width) // 2
    first_row_y = htr//2 + 100
    second_row_y = first_row_y + button_height + padding
    
    # Création des boutons
    buttons = []
    for i in range(10):
        row = i // 5
        col = i % 5
        x = start_x + col * (button_width + padding)
        y = first_row_y if row == 0 else second_row_y
        buttons.append(create_button(x, y, button_width, button_height, f"Level {i+1}"))

    while running:
        
        fnd = image.load("data/images/image_menu.png").convert()
        fnd = transform.scale(fnd, (rec.right, rec.bottom))
        ecr.blit(fnd, (0, 0))  # Fond gris foncé
        
        # Affichage titres
        ecr.blit(title, title_rect)
        ecr.blit(subtitle, subtitle_rect)
        
        # Affichage boutons avec effet de bordure
        for button_rect, button_text, text_rect in buttons:
            draw.rect(ecr, (80, 80, 80), button_rect)  # Bouton
            draw.rect(ecr, (120, 120, 120), button_rect, 2)  # Bordure
            ecr.blit(button_text, text_rect)
        
        display.flip()

        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                running = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                mouse_pos = mouse.get_pos()
                for i, (button_rect, _, _) in enumerate(buttons):
                    if button_rect.collidepoint(mouse_pos):
                        if i == 0:
                            return page_jeu(i+1)
                        else:
                            print(f"Niveau {i+1} non disponible")

    return True

````

filename:**shared\components\config.py**
````py
from pygame import *

# Initialisation
init()
mixer.init()

# Configuration écran
ecr = display.set_mode((0, 0), FULLSCREEN)
rec = ecr.get_rect()
lrg, htr = ecr.get_size()

# Sons
try:
    son_clic = mixer.Sound("data/sons/click_002.wav")
    mixer.music.load("data/sons/musique_test.mp3")
    son_survol = mixer.Sound("data/sons/clic1.wav")
    son_clicmenu = mixer.Sound("data/sons/clic2.wav")
    mixer.music.set_volume(0.5)
    mixer.music.play(-1)
except:
    print("Error : fichiers sons non trouvés")

# Boutons menu
btn_jeu = {"rect": Rect(lrg/2-125, htr/2-100, 250, 60), "a_joue_son": False}
btn_cfg = {"rect": Rect(lrg/2-125, htr/2, 250, 60), "a_joue_son": False}
btn_fin = {"rect": Rect(lrg/2-125, htr/2+100, 250, 60), "a_joue_son": False}

# Couleurs
BLC = (255, 255, 255)
NOR = (0, 0, 0)
BLEU = (0, 100, 200)

# Police
fnt = font.Font(None, 50)
police_titre = font.Font(None, 150)
police_options = font.Font(None, 40)

# Position de la barre de volume
barre_x = 200
barre_y_general = 250
barre_y_musique = 350
barre_y_sfx = 450
barre_largeur = 400
barre_hauteur = 20

````

filename:**shared\components\déplacement du perso V2.py**
````py
import pygame
import sys
import math

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Déplacement fluide avec images")

# Chargement des images pour les différentes directions
walk_down = [pygame.image.load(f'walk_down_{i}.png') for i in range(1, 5)]  # vers le bas
walk_up = [pygame.image.load(f'walk_up_{i}.png') for i in range(1, 5)]      # vers le haut
walk_left = [pygame.image.load(f'walk_left_{i}.png') for i in range(1, 5)]  # vers la gauche
walk_right = [pygame.image.load(f'walk_right_{i}.png') for i in range(1, 5)]  # vers la droite

# Paramètres du personnage
x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # Position initiale
speed = 3  # Vitesse du déplacement
current_image = 0  # Index de l'image en cours pour l'animation

# Variables pour le mouvement
target_x, target_y = x, y  # Position cible
moving = False

# Fonction pour changer l'index de l'image (en fonction de la direction)
def get_next_image(direction):
    global current_image
    current_image = (current_image + 1) % 4  # Passer d'une image à l'autre (quatre images)
    
    if direction == 'down':
        return walk_down[current_image]
    elif direction == 'up':
        return walk_up[current_image]
    elif direction == 'left':
        return walk_left[current_image]
    elif direction == 'right':
        return walk_right[current_image]

# Boucle principale du jeu
clock = pygame.time.Clock()

while True:
    screen.fill((255, 255, 255))  # Fond blanc
    
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Récupérer la position de la souris
            target_x, target_y = pygame.mouse.get_pos()
            moving = True

    # Calculer le mouvement fluide vers la cible
    if moving:
        # Calculer la direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Déterminer la direction principale en fonction de l'angle
        direction = ''
        if abs(dx) > abs(dy):  # Mouvement horizontal
            if dx > 0:
                direction = 'right'
            else:
                direction = 'left'
        else:  # Mouvement vertical
            if dy > 0:
                direction = 'down'
            else:
                direction = 'up'

        # Si la distance est assez grande, on avance un peu
        if distance > speed:
            x += (dx / distance) * speed
            y += (dy / distance) * speed
        else:
            # Arrêter lorsque l'on arrive assez près de la cible
            x, y = target_x, target_y
            moving = False

        # Afficher l'image correspondante pour le mouvement
        screen.blit(get_next_image(direction), (x - walk_down[0].get_width() // 2, y - walk_down[0].get_height() // 2))
    else:
        # Si on n'est pas en mouvement, afficher une image statique ou autre
        screen.blit(walk_down[0], (x - walk_down[0].get_width() // 2, y - walk_down[0].get_height() // 2))

    # Actualiser l'écran
    pygame.display.flip()

    # Limiter les FPS pour un mouvement fluide
    clock.tick(30)

````

filename:**shared\components\déplacement du perso.py**
````py
import pygame
import sys

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Déplacement fluide avec images")

# Chargement des images pour le mouvement
walk_images = [
    pygame.image.load('i1.jpg'),  # Remplacer par le chemin vers vos images
    pygame.image.load('i2.jpg'),
    pygame.image.load('i3.jpg'),
    pygame.image.load('i4.jpg'),
    pygame.image.load('i5.jpg'),
    pygame.image.load('i6.jpg'),
    pygame.image.load('i7.jpg')
]

# Paramètres du personnage
x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # Position initiale
speed = 7  # Vitesse du déplacement
current_image = 0  # Index de l'image en cours pour l'animation

# Variables pour le mouvement
target_x, target_y = x, y  # Position cible
moving = False

# Fonction pour changer l'index de l'image
def get_next_image():
    global current_image
    current_image = (current_image + 1) % len(walk_images)
    return walk_images[current_image]

# Boucle principale du jeu
clock = pygame.time.Clock()

while True:
    screen.fill((255, 255, 255))  # Fond blanc
    
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Récupérer la position de la souris
            target_x, target_y = pygame.mouse.get_pos()
            moving = True

    # Calculer le mouvement fluide vers la cible
    if moving:
        # Calculer la direction
        dx = target_x - x
        dy = target_y - y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # Si la distance est assez grande, on avance un peu
        if distance > speed:
            x += (dx / distance) * speed
            y += (dy / distance) * speed
        else:
            # Arrêter lorsque l'on arrive assez près de la cible
            x, y = target_x, target_y
            moving = False

        # Afficher l'image correspondante pour le mouvement
        screen.blit(get_next_image(), (x - walk_images[0].get_width() // 2, y - walk_images[0].get_height() // 2))
    else:
        # Si on n'est pas en mouvement, afficher une image statique ou autre
        screen.blit(walk_images[0], (x - walk_images[0].get_width() // 2, y - walk_images[0].get_height() // 2))

    # Actualiser l'écran
    pygame.display.flip()

    # Limiter les FPS pour un mouvement fluide
    clock.tick(10)
````

filename:**shared\components\encyclopédie.py**
````py
import csv
from random import *
encyclopédie = []
with open('encyclopédie.csv', newline='') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=';')
    for row in spamreader:
        encyclopédie.append(dict(row))

elements_connus=[1,2,3,4]

def combinaison(element1,element2):
    n=0
    #Vérifie que les elements sont différents, puis si ils peuvent créer qq chose
    if encyclopédie[element1]["Nom"]!=encyclopédie[element2]["Nom"]:
        for element in encyclopédie[element1]["Créations"]:
            if element in encyclopédie[element2]["Créations"]:
                n=1
                e=int(element)
                # retourne l'élément crée
                return e,element1,element2
    # return false si objets non fusionnable
    else:
        return False
    if n==0:
        return False


def nouvel_element(element):
    if element in elements_connus:
        None
    else:
        # retourne l'element si pas encore découvert pour l'afficher en grand
        elements_connus.append(element)
        return element
    





````

filename:**shared\utils\utils.py**
````py

````


=== Fichiers ignorés ===
fusionner_fichiers.md
fusionner_fichiers.py
data\images\air.png
data\images\bg_level1.jpg
data\images\bg_menu.png
data\images\bois.png
data\images\chaleur.png
data\images\cle.png
data\images\cuisiner.png
data\images\eau.png
data\images\energie.png
data\images\etincelles.png
data\images\feu.png
data\images\fruits.png
data\images\gaz.png
data\images\graine.png
data\images\image_menu.png
data\images\lame.png
data\images\metal.png
data\images\pierre.png
data\images\pierre_lisse.png
data\images\pioche.png
data\images\plante.png
data\images\seau.PNG
data\images\seau_d'eau.PNG
data\images\terre.png
data\images\Thumbs.db
data\images\perso\i1.jpg
data\images\perso\i2.jpg
data\images\perso\i3.jpg
data\images\perso\i4.jpg
data\images\perso\i5.jpg
data\images\perso\i6.jpg
data\images\perso\i7.jpg
data\sons\clic1.wav
data\sons\clic2.wav
data\sons\click_002.wav
data\sons\musique_test.mp3
data\sons\musique_test1.mp3

=== Fichiers inclus ===
**main.py**
**data\touches.json**
**data\csv\encyclopedie.csv**
**interface\jeu.py**
**interface\menu.py**
**interface\menu_interf_jeu.py**
**interface\parametres.py**
**interface\selection_niveau.py**
**shared\components\config.py**
**shared\components\déplacement du perso V2.py**
**shared\components\déplacement du perso.py**
**shared\components\encyclopédie.py**
**shared\utils\utils.py**

=== Arborescence du dossier ===
└─ sources
   ├─ data
   │  ├─ csv
   │  │  └─ **encyclopedie.csv**
   │  ├─ images
   │  │  ├─ Thumbs.db
   │  │  ├─ air.png
   │  │  ├─ bg_level1.jpg
   │  │  ├─ bg_menu.png
   │  │  ├─ bois.png
   │  │  ├─ chaleur.png
   │  │  ├─ cle.png
   │  │  ├─ cuisiner.png
   │  │  ├─ eau.png
   │  │  ├─ energie.png
   │  │  ├─ etincelles.png
   │  │  ├─ feu.png
   │  │  ├─ fruits.png
   │  │  ├─ gaz.png
   │  │  ├─ graine.png
   │  │  ├─ image_menu.png
   │  │  ├─ lame.png
   │  │  ├─ metal.png
   │  │  ├─ perso
   │  │  │  ├─ i1.jpg
   │  │  │  ├─ i2.jpg
   │  │  │  ├─ i3.jpg
   │  │  │  ├─ i4.jpg
   │  │  │  ├─ i5.jpg
   │  │  │  ├─ i6.jpg
   │  │  │  └─ i7.jpg
   │  │  ├─ pierre.png
   │  │  ├─ pierre_lisse.png
   │  │  ├─ pioche.png
   │  │  ├─ plante.png
   │  │  ├─ seau.PNG
   │  │  ├─ seau_d'eau.PNG
   │  │  └─ terre.png
   │  ├─ sons
   │  │  ├─ clic1.wav
   │  │  ├─ clic2.wav
   │  │  ├─ click_002.wav
   │  │  ├─ musique_test.mp3
   │  │  └─ musique_test1.mp3
   │  └─ **touches.json**
   ├─ fusionner_fichiers.md
   ├─ fusionner_fichiers.py
   ├─ interface
   │  ├─ **jeu.py**
   │  ├─ **menu.py**
   │  ├─ **menu_interf_jeu.py**
   │  ├─ **parametres.py**
   │  └─ **selection_niveau.py**
   ├─ **main.py**
   └─ shared
      ├─ components
      │  ├─ **config.py**
      │  ├─ **déplacement du perso V2.py**
      │  ├─ **déplacement du perso.py**
      │  └─ **encyclopédie.py**
      └─ utils
         └─ **utils.py**
