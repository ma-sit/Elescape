from pygame import *
import sys
import json
from shared.components.config import *
from interface.menu import dessiner_menu
from interface.selection_niveau import selection_niveau
from interface.parametres import page_parametres

# Initialisation
init()

# Charger ou réinitialiser les touches utilisateur
def charger_touches():
    try:
        with open("data/touches.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'Déplacement': BUTTON_RIGHT,
            'Action': K_SPACE,
            'Retour': K_ESCAPE,
            'Plein écran': K_f,
            'Paramètres': K_s,
            'Jouer': K_p,
            'Quitter': K_q
        }

# Sauvegarder les touches dans le fichier
def sauvegarder_touches(touches):
    with open("data/touches.json", "w") as f:
        json.dump(touches, f)

touches = charger_touches()

# Boucle principale
def boucle_principale():
    act = True
    while act:
        dessiner_menu(ecr)
        
        for evt in event.get():
            if evt.type == QUIT:
                act = False
            elif evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if btn_jeu["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    act = selection_niveau()
                elif btn_cfg["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    act = page_parametres()
                elif btn_fin["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    act = False
            elif evt.type == KEYDOWN:
                if evt.key == touches['Jouer']:
                    act = selection_niveau()
                elif evt.key == touches['Paramètres']:
                    act = page_parametres()
                elif evt.key == touches['Quitter']:
                    act = False
        
        display.flip()
        time.delay(30)

    quit()
    sys.exit()

if __name__ == "__main__":
    boucle_principale()
