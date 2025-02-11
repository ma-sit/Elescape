from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from data.level.niveau1 import niveau1

def create_button(x, y, width, height, text):
    button_rect = Rect(x, y, width, height)
    button_text = font.Font(None, 36).render(text, True, (255, 255, 255))
    text_rect = button_text.get_rect(center=button_rect.center)
    return (button_rect, button_text, text_rect)

def selection_niveau():
    running = True
    
    # Dimensions et style
    button_width = 120
    button_height = 50
    padding = 20
    
    # Titres
    title_font = font.Font(None, 100)
    subtitle_font = font.Font(None, 60)
    title = title_font.render("VITANOX", True, (255, 255, 255))
    subtitle = subtitle_font.render("Select your level", True, (255, 255, 255))
    
    # Position des titres
    title_rect = title.get_rect(center=(lrg//2, htr//4))
    subtitle_rect = subtitle.get_rect(center=(lrg//2, htr//4 + 80))
    
    # Calcul positions des boutons
    total_width = 5 * (button_width + padding) - padding
    start_x = (lrg - total_width) // 2
    first_row_y = htr//2 + 100
    second_row_y = first_row_y + button_height + padding
    
    # Création des boutons
    buttons = []
    for i in range(10):
        row = i // 5
        col = i % 5
        x = start_x + col * (button_width + padding)
        y = first_row_y if row == 0 else second_row_y
        buttons.append(create_button(x, y, button_width, button_height, f"Level {i+1}"))

    while running:
        ecr.fill((40, 40, 40))  # Fond gris foncé
        
        # Affichage titres
        ecr.blit(title, title_rect)
        ecr.blit(subtitle, subtitle_rect)
        
        # Affichage boutons avec effet de bordure
        for button_rect, button_text, text_rect in buttons:
            draw.rect(ecr, (80, 80, 80), button_rect)  # Bouton
            draw.rect(ecr, (120, 120, 120), button_rect, 2)  # Bordure
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
                        if i == 0:
                            return niveau1()
                        else:
                            print(f"Niveau {i+1} non disponible")

    return True
