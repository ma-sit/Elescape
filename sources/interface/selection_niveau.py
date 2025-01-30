from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def create_button(x, y, width, height, text, font_size=32):
    button_rect = Rect(x, y, width, height)
    button_text = font.Font(None, font_size).render(text, True, BLC)
    text_rect = button_text.get_rect(center=button_rect.center)
    return (button_rect, button_text, text_rect)

def selection_niveau():
    """Menu de sélection des niveaux"""
    running = True
    
    # Dimensions des boutons
    button_width = 100
    button_height = 50
    padding = 20
    
    # Calcul des positions pour centrer les boutons
    start_x = (lrg - (5 * (button_width + padding))) // 2
    first_row_y = htr // 3
    second_row_y = first_row_y + button_height + padding
    
    # Création des boutons
    buttons = []
    for i in range(10):
        row = i // 5  # 0 pour première ligne, 1 pour deuxième ligne
        col = i % 5   # Position dans la ligne
        x = start_x + col * (button_width + padding)
        y = first_row_y if row == 0 else second_row_y
        buttons.append(create_button(x, y, button_width, button_height, f"Level {i+1}"))

    while running:
        ecr.fill((50, 50, 50))
        
        # Affichage des boutons
        for i, (button_rect, button_text, text_rect) in enumerate(buttons):
            draw.rect(ecr, (150, 150, 150), button_rect)
            draw.rect(ecr, (200, 200, 200), button_rect, 2)
            ecr.blit(button_text, text_rect)

        display.flip()

        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                running = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                mouse_pos = mouse.get_pos()
                for i, (button_rect, _, _) in enumerate(buttons):
                    if button_rect.collidepoint(mouse_pos):
                        print(f"Niveau {i+1} sélectionné")
                        # Ici, vous pouvez ajouter la logique pour charger le niveau
                        return True

    return True
