from pygame import *
import sys
import json
from shared.components.config import *

def selection_niveau():
    """Menu de sélection des niveaux"""
    # Chargement des touches
    try:
        with open("data/touches.json", "r") as f:
            touches = json.load(f)
    except:
        touches = {
            'Retour': K_ESCAPE
        }
    
    running = True
    while running:
        ecr.fill(NOR)
        
        # Titre
        afficher_texte("Sélection du niveau", lrg // 2, 100, police_titre, BLC)
        
        # Niveaux
        for i in range(10):
            x = lrg // 2 - 200 + (i % 5) * 100
            y = 250 + (i // 5) * 100
            rect_niveau = Rect(x, y, 80, 80)
            draw.rect(ecr, BLEU, rect_niveau)
            afficher_texte(str(i + 1), x + 40, y + 40, police_options, BLC)
        
        afficher_texte("Retour (Échap)", lrg // 2, 550, police_options, BLEU)
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == touches['Retour']:
                running = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                for i in range(10):
                    x = lrg // 2 - 200 + (i % 5) * 100
                    y = 250 + (i // 5) * 100
                    rect_niveau = Rect(x, y, 80, 80)
                    if rect_niveau.collidepoint(evt.pos):
                        if i == 0:
                            return page_jeu()
                        else:
                            print(f"Niveau {i+1} non disponible")
        
        display.flip()
    
    return True

def afficher_texte(texte, x, y, plc, couleur):
    txt = plc.render(texte, True, couleur)
    rect = txt.get_rect(center=(x, y))
    ecr.blit(txt, rect)
