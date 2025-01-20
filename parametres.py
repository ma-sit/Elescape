import pygame
from config import *

def page_parametres(ecr, fnt):
    """Gère la page des paramètres"""
    act = True
    while act:
        ecr.fill((150, 150, 150))
        txt = fnt.render("Page des Paramètres - Appuyez sur Echap pour revenir", True, BLC)
        ecr.blit(txt, (50, HTR // 2 - 25))
        pygame.display.flip()

        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return False
            if evt.type == pygame.KEYDOWN and evt.key == pygame.K_ESCAPE:
                act = False
    return True

