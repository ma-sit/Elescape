from pygame import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def page_parametres():
    """Page des paramètres"""
    act = True
    volume_general = mixer.music.get_volume()
    volume_sfx = mixer.music.get_volume()  # Volume pour les effets sonores
    clic_souris = False
    barre_active = None  # Pour savoir quelle barre est en cours d'ajustement
    horloge = time.Clock()
    
    # Position des barres
    barre_y_general = 250  # Position Y de la première barre
    barre_y_sfx = 350      # Position Y de la deuxième barre
    
    while act:
        ecr.fill(NOR)
        afficher_texte("Paramètres", lrg // 2, 100, police_titre, BLC)
        
        # Textes des volumes
        afficher_texte(f"Volume général : {int(volume_general * 100)}%", 
                      barre_x - 10, barre_y_general - 20, 
                      police_options, BLEU, "right")
        afficher_texte(f"Volume interface : {int(volume_sfx * 100)}%", 
                      barre_x - 10, barre_y_sfx - 20, 
                      police_options, BLEU, "right")
        
        afficher_texte("Retour (Appuie sur Échap)", lrg // 2, 450, police_options, BLEU)
        
        # Barre volume général
        draw.rect(ecr, BLC, (barre_x, barre_y_general, barre_largeur, barre_hauteur), 
                 border_radius=10)
        largeur_remplie = int(barre_largeur * volume_general)
        if largeur_remplie > 0:
            if volume_general == 1.0:
                draw.rect(ecr, BLEU, 
                         (barre_x, barre_y_general, largeur_remplie, barre_hauteur),
                         border_radius=10)
            else:
                draw.rect(ecr, BLEU, 
                         (barre_x, barre_y_general, largeur_remplie, barre_hauteur),
                         border_top_left_radius=10, border_bottom_left_radius=10)

        # Barre volume SFX
        draw.rect(ecr, BLC, (barre_x, barre_y_sfx, barre_largeur, barre_hauteur), 
                 border_radius=10)
        largeur_remplie_sfx = int(barre_largeur * volume_sfx)
        if largeur_remplie_sfx > 0:
            if volume_sfx == 1.0:
                draw.rect(ecr, BLEU, 
                         (barre_x, barre_y_sfx, largeur_remplie_sfx, barre_hauteur),
                         border_radius=10)
            else:
                draw.rect(ecr, BLEU, 
                         (barre_x, barre_y_sfx, largeur_remplie_sfx, barre_hauteur),
                         border_top_left_radius=10, border_bottom_left_radius=10)
        
        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    act = False
            if evt.type == MOUSEBUTTONDOWN:
                x, y = evt.pos
                if barre_x <= x <= barre_x + barre_largeur:
                    if barre_y_general <= y <= barre_y_general + barre_hauteur:
                        barre_active = "general"
                        clic_souris = True
                    elif barre_y_sfx <= y <= barre_y_sfx + barre_hauteur:
                        barre_active = "sfx"
                        clic_souris = True

            if evt.type == MOUSEBUTTONUP:
                clic_souris = False
                barre_active = None

            if evt.type == MOUSEMOTION and clic_souris:
                x, y = evt.pos
                if barre_active == "general":
                    volume_general = max(0.0, min(1.0, (x - barre_x) / barre_largeur))
                elif barre_active == "sfx":
                    volume_sfx = max(0.0, min(1.0, (x - barre_x) / barre_largeur))
        
        mixer.music.set_volume(volume_general)
        # Ici vous devrez implémenter la gestion du volume des effets sonores
        # mixer.Channel(0).set_volume(volume_sfx)  # Exemple
        
        display.flip()
        horloge.tick(30)

    return True

def afficher_texte(texte, x, y, plc, couleur, align="center"):
    """ Affiche un texte avec alignement personnalisable """
    police = plc
    surface_texte = police.render(texte, True, couleur)
    rect_texte = surface_texte.get_rect()
    if align == "center":
        rect_texte.center = (x, y)
    elif align == "right":
        rect_texte.midright = (x, y)
    elif align == "left":
        rect_texte.midleft = (x, y)
    ecr.blit(surface_texte, rect_texte)
