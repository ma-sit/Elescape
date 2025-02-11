from pygame import *
from shared.components.config import *
import json
import os

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
    touche_active = None
    
    # Chargement des touches sauvegardées ou utilisation des touches par défaut
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

    while act:
        ecr.fill(NOR)
        
        # Titre
        afficher_texte("Paramètres", lrg // 2, 100, police_titre, BLC)

        # Boutons du menu
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

        if section_active == "Touches":
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

        elif section_active == "Audio":
            # [Code existant pour la section Audio]
            pass

        for evt in event.get():
            if evt.type == QUIT:
                # Sauvegarde des touches avant de quitter
                with open("data/touches.json", "w") as f:
                    json.dump(touches, f)
                return False

            if evt.type == KEYDOWN:
                if touche_active:
                    if touche_active != "Déplacement":
                        touches[touche_active] = evt.key
                        touche_active = None
                elif evt.key == K_ESCAPE:
                    # Sauvegarde des touches avant de quitter
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
                                touche_active = None
                        y_pos += espacement

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
