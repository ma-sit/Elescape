from pygame import *
import json
from shared.components.config import *

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
    
    act = True
    menu_width = 300
    menu_height = 200
    menu_x = (lrg - menu_width) // 2
    menu_y = (htr - menu_height) // 2
    button_width = 120
    button_height = 40
    button_x = menu_x + (menu_width - button_width) // 2
    button_y = menu_y + menu_height - button_height - 20
    quit_button = Rect(button_x, button_y, button_width, button_height)
    
    while act:
        surf_overlay = Surface((lrg, htr), SRCALPHA)
        surf_overlay.fill((0, 0, 0, 128))
        ecr.blit(surf_overlay, (0, 0))
        
        draw.rect(ecr, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height))
        draw.rect(ecr, BLC, (menu_x, menu_y, menu_width, menu_height), 2)
        
        titre = font.Font(None, 36).render("Parameters", True, BLC)
        titre_rect = titre.get_rect(center=(menu_x + menu_width//2, menu_y + 30))
        ecr.blit(titre, titre_rect)
        
        draw.rect(ecr, (150, 150, 150), quit_button)
        draw.rect(ecr, BLC, quit_button, 2)
        quit_text = font.Font(None, 32).render("Quit", True, BLC)
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        ecr.blit(quit_text, quit_text_rect)
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == touches['Retour']:
                menu_actif = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if quit_button.collidepoint(evt.pos):
                    act = False
    
    return True
