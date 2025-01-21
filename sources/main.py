from pygame import *
import sys
from sources.shared.components.config import *
from sources.interface.menu import dessiner_menu, plein_ecran
from sources.interface.selection_niveau import selection_niveau
from sources.interface.parametres import page_parametres

# Initialisation
init()

# Chargement fond menu
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
            
        if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
            if btn_jeu.collidepoint(evt.pos):
                act = selection_niveau()
            elif btn_cfg.collidepoint(evt.pos):
                act = page_parametres()
            elif btn_fin.collidepoint(evt.pos):
                act = False

        if evt.type == KEYDOWN:
            if evt.key == K_f:
                plein_ecran()
            elif evt.key == K_p:
                act = selection_niveau()
            elif evt.key == K_s:
                act = page_parametres()
            elif evt.key == K_q:
                act = False

quit()
sys.exit()
