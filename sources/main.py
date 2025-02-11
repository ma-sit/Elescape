from pygame import *
import sys
from shared.components.config import *
from interface.menu import dessiner_menu, plein_ecran
from interface.selection_niveau import selection_niveau
from interface.parametres import page_parametres, charger_touches

# Chargement des touches
touches = charger_touches()

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
            if evt.key == touches['Plein écran']:
                plein_ecran()
            elif evt.key == touches['Jouer']:
                act = selection_niveau()
            elif evt.key == touches['Paramètres']:
                act = page_parametres()
            elif evt.key == touches['Quitter']:
                act = False
