import pygame
import sys
from config import *
from menutest import *
from jeu import page_jeu
from parametres import page_parametres

def main():
    """Fonction principale du jeu"""
    ecr = init_fenetre()
    fnt = pygame.font.Font(None, 50)
    fnd = pygame.image.load("background/bg_menu.png").convert()
    fnd = pygame.transform.scale(fnd, (LRG, HTR))
    
    act = True
    while act:
        dessiner_menu(ecr, fnt, fnd)
        pygame.display.flip()

        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                act = False

            if evt.type == pygame.MOUSEBUTTONDOWN and evt.button == 1:
                if btn_jeu.collidepoint(evt.pos):
                    act = page_jeu(ecr, fnt)
                elif btn_cfg.collidepoint(evt.pos):
                    act = page_parametres(ecr, fnt)
                elif btn_fin.collidepoint(evt.pos):
                    act = False

            if evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_f:
                    ecr = plein_ecran(ecr)
                elif evt.key == pygame.K_p:
                    act = page_jeu(ecr, fnt)
                elif evt.key == pygame.K_s:
                    act = page_parametres(ecr, fnt)
                elif evt.key == pygame.K_q:
                    act = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

