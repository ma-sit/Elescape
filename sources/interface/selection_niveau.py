from pygame import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from data.level.niveau1 import niveau1

def selection_niveau():
    """Menu de sélection des niveaux"""
    act = True
    
    # Chargement image niveau 1
    img_niv1 = image.load("data/images/bg_level1.jpg").convert()
    img_niv1 = transform.scale(img_niv1, (lrg//3, htr//2))
    
    # Zone cliquable niveau 1
    rect_niv1 = Rect(lrg//3, htr//4, lrg//3, htr//2)
    
    while act:
        ecr.fill((50, 50, 50))
        ecr.blit(img_niv1, (lrg//3, htr//4))
        
        txt = fnt.render("Niveau 1", True, BLC)
        txt_rect = txt.get_rect(center=(lrg//2, htr//4 - 30))
        ecr.blit(txt, txt_rect)
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                act = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if rect_niv1.collidepoint(evt.pos):
                    return niveau1()
    return True
