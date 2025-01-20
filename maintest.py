from pygame import *
import sys
from config import *
from menu import dessiner_menu, plein_ecran
from jeu import page_jeu
from parametres import page_parametres

# Initialisation de Pygame
init()

# Chargement du fond d'écran
fnd = image.load("background/bg_menu.png").convert()
fnd = transform.scale(fnd, (rec.right, rec.bottom))

# Boucle principale
act = True
while act:
    dessiner_menu(ecr, fnd)
    display.flip()

    for evt in event.get():
        if evt.type == QUIT:
            act = False

        # Gestion des clics souris
        if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
            if btn_jeu.collidepoint(evt.pos):
                act = page_jeu()
            elif btn_cfg.collidepoint(evt.pos):
                act = page_parametres()
            elif btn_fin.collidepoint(evt.pos):
                act = False

        # Gestion clavier
        if evt.type == KEYDOWN:
            if evt.key == K_f:      # F: plein écran
                plein_ecran()
            elif evt.key == K_p:    # P: jouer
                act = page_jeu()
            elif evt.key == K_s:    # S: paramètres
                act = page_parametres()
            elif evt.key == K_q:    # Q: quitter
                act = False

quit()
sys.exit()
