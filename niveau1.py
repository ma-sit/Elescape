from pygame import *
from config import *

def niveau1():
    """Premier niveau du jeu"""
    act = True
    
    # Chargement des éléments spécifiques au niveau 1
    fnd_niv1 = image.load("background/niveau1_bg.png").convert()
    fnd_niv1 = transform.scale(fnd_niv1, (lrg, htr))
    
    while act:
        # Affichage niveau 1
        ecr.blit(fnd_niv1, (0, 0))
        
        # Logique du niveau 1 ici
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                act = False
                
    return True
