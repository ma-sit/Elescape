from pygame import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def page_parametres():
    """Page des paramètres"""
    act = True
    volume = mixer.music.get_volume()
    clic_souris = False
    horloge = time.Clock()
    
    while act:
        ecr.fill(NOR)
        afficher_texte("Paramètres", lrg // 2, 100,police_titre,BLC)
        afficher_texte(f"Volume : {int(volume * 100)}%", lrg // 2, 250, police_options, BLEU)
        afficher_texte("Retour (Appuie sur Échap)", lrg // 2, 400,police_options,BLEU)
        
        # son
        draw.rect(ecr, BLC, (barre_x, barre_y, barre_largeur, barre_hauteur), border_radius=10)

        largeur_remplie = int(barre_largeur * volume)
        if largeur_remplie > 0:  # Si volume > 0
            if volume == 1.0:  # Volume maximal (arrondi à gauche et à droite)
                draw.rect(
                    ecr,
                    BLEU,
                    (barre_x, barre_y, largeur_remplie, barre_hauteur),
                    border_radius=10,
                )
            else:  # Volume partiel (arrondi uniquement à gauche)
                draw.rect(
                    ecr,
                    BLEU,
                    (barre_x, barre_y, largeur_remplie, barre_hauteur),
                    border_top_left_radius=10,
                    border_bottom_left_radius=10,
                )

        
        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    act = False
                if evt.key == K_LEFT:
                    volume = max(0.0, volume - 0.01)
                if evt.key == K_RIGHT:
                    volume = min(1.0, volume + 0.01)
            if evt.type == MOUSEBUTTONDOWN:
                x, y = evt.pos
                if barre_x <= x <= barre_x + barre_largeur and barre_y <= y <= barre_y + barre_hauteur:
                    clic_souris = True 

            if evt.type ==  MOUSEBUTTONUP:
                clic_souris = False

            if evt.type == MOUSEMOTION and clic_souris:
                x, y = evt.pos
                volume = max(0.0, min(1.0, (x - barre_x) / barre_largeur)) # Ajuste le volume selon la position de la souris
        
        touches = key.get_pressed()
        if touches[K_LEFT]:
            volume = max(0.0, volume - 0.01)  # Diminution progressive
        if touches[K_RIGHT]:
            volume = min(1.0, volume + 0.01)
        
        mixer.music.set_volume(volume)
        display.flip()
        horloge.tick(30)

    return True

def afficher_texte(texte, x, y,plc,couleur):
    """ Affiche un texte centré """
    police=plc
    surface_texte = police.render(texte, True,couleur)
    rect_texte = surface_texte.get_rect(center=(x, y))
    ecr.blit(surface_texte, rect_texte)
