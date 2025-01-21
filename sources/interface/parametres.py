from pygame import *
from sources.shared.components.config import *

def page_parametres():
    """Page des paramètres"""
    act = True
    while act:
        ecr.fill((150, 150, 150))
        txt = fnt.render("Paramètres - ECHAP pour revenir", True, BLC)
        ecr.blit(txt, (50, htr//2 - 25))
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                act = False
    return True
