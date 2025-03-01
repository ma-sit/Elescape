from pygame import *
import json
from shared.components.config import *
from interface.menu import bouton

def menu_parametres():
    """Menu des paramètres qui s'affiche par-dessus le niveau"""
    # Chargement des touches
    try:
        with open("data/touches.json", "r") as f:
            touches = json.load(f)
    except:
        touches = {
            'Retour': K_ESCAPE
        }
    
    menu_actif = True
    menu_width = 300
    menu_height = 200
    menu_x = (lrg - menu_width) // 2
    menu_y = (htr - menu_height) // 2
    button_width = 120
    button_height = 40
    button_x = menu_x + (menu_width - button_width) // 2
    button_y = menu_y + menu_height - button_height - 20
    
    # Bouton quitter avec le format compatible avec la fonction bouton()
    quit_button = {
        "rect": Rect(button_x, button_y, button_width, button_height),
        "image": None,
        "a_joue_son": False,
        "text": "Quit"
    }
    
    while menu_actif:
        surf_overlay = Surface((lrg, htr), SRCALPHA)
        surf_overlay.fill((0, 0, 0, 128))
        ecr.blit(surf_overlay, (0, 0))
        
        # Rectangle de fond du menu avec coins arrondis
        draw.rect(ecr, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height), border_radius=15)
        draw.rect(ecr, BLC, (menu_x, menu_y, menu_width, menu_height), 2, border_radius=15)
        
        titre = font.Font(None, 36).render("Parameters", True, BLC)
        titre_rect = titre.get_rect(center=(menu_x + menu_width//2, menu_y + 30))
        ecr.blit(titre, titre_rect)
        
        # Utilisation de la fonction bouton avec arrondis
        hover = bouton(ecr, (150, 150, 150), quit_button, quit_button["text"], son_survol, son_clicmenu, 10, surbrillance=BLC)
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == touches['Retour']:
                menu_actif = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if quit_button["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    return False
    
    return True
