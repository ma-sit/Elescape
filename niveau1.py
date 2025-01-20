from pygame import *
from config import *

def niveau1():
    """Premier niveau du jeu avec fond blanc"""
    act = True
    
    while act:
        # Fond blanc
        ecr.fill(BLC)
        
        # Mise à jour affichage
        display.flip()
        
        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:  # Retour au menu
                    act = False
                
    return True
