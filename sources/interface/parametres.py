from pygame import *
from shared.components.config import *
import json

def page_parametres():
    """Page des paramètres"""
    act = True
    volume_general = mixer.music.get_volume()
    
    while act:
        ecr.fill(NOR)

        afficher_texte("Paramètres", lrg // 2, 100, police_titre, BLC)

        # Section Audio - Exemple simplifié d'ajustement du volume général
        afficher_texte(f"Volume général : {int(volume_general * 100)}%", lrg // 2 - 200,
                       htr // 2 - 50, police_options, BLEU)
        
        draw.rect(ecr, BLC,
                  Rect(lrg // 2 - 200 + int(volume_general * barre_largeur), htr // 2 - 30,
                       barre_largeur * volume_general,
                       barre_hauteur))

        for evt in event.get():
            if evt.type == QUIT or (evt.type == KEYDOWN and evt.key == K_ESCAPE):
                return False

            if evt.type == MOUSEBUTTONDOWN:
                x_pos = evt.pos[0]
                if lrg // 2 - barre_largeur <= x_pos <= lrg // 2 + barre_largeur:
                    volume_general = max(0.0,
                                         min(1.0,
                                             (x_pos - (lrg // barge_x))))
