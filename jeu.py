from pygame import *
from config import *

def page_jeu():
    """Page du jeu"""
    act = True
    while act:
        ecr.fill((100, 100, 100))
        txt = fnt.render("Page de Jeu - Appuyez sur Echap pour revenir", True, BLC)
        ecr.blit(txt, (50, htr // 2 - 25))
        display.flip()

        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                act = False
    return True
