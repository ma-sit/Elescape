from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from data.level.niveau1 import niveau1

def create_button(x, y, width, height, text, font_size=32):
    button_rect = Rect(x, y, width, height)
    button_text = font.Font(None, font_size).render(text, True, BLC)
    text_rect = button_text.get_rect(center=button_rect.center)
    return (button_rect, button_text, text_rect)

def selection_niveau():
    running = True
    
    # Police pour les titres
    title_font = font.Font(None, 80)
    subtitle_font = font.Font(None, 50)
    
    # Création des textes
    title_text = title_font.render("VITANOX", True, BLC)
    subtitle_text = subtitle_font.render("Select your level", True, BLC)
    
    # Position des titres
    title_rect = title_text.get_rect(center=(lrg//2, htr//6))
    subtitle_rect = subtitle_text.get_rect(center=(lrg//2, htr//4))
    
    # Dimensions des boutons
    button_width = 100
    button_height = 50
    padding = 20
    
    # Calcul des positions pour centrer les boutons
    start_x = (lrg - (5 * (button_width + padding))) // 2
    first_row_y = htr//2
    second_row_y = first_row_y + button_height + padding
    quit_y = second_row_y + button_height + padding * 2
    
    # Création des boutons de niveau
    buttons = []
    for i in range(10):
        row = i // 5
        col = i % 5
        x = start_x + col * (button_width + padding)
        y = first_row_y if row == 0 else second_row_y
        buttons.append(create_button(x, y, button_width, button_height, f"Level {i+1}"))
    
    # Création du bouton Quit
    quit_button = create_button(lrg//2 - button_width//2, quit_y, button_width, button_height, "Quit")

    while running:
        ecr.fill((50, 50, 50))
        
        # Affichage des titres
        ecr.blit(title_text, title_rect)
        ecr.blit(subtitle_text, subtitle_rect)
        
        # Affichage des boutons de niveau
        for i, (button_rect, button_text, text_rect) in enumerate(buttons):
            draw.rect(ecr, (150, 150, 150), button_rect)
            draw.rect(ecr, (200, 200, 200), button_rect, 2)
            ecr.blit(button_text, text_rect)
        
        # Affichage du bouton Quit
        quit_rect, quit_text, quit_text_rect = quit_button
        draw.rect(ecr, (150, 150, 150), quit_rect)
        draw.rect(ecr, (200, 200, 200), quit_rect, 2)
        ecr.blit(quit_text, quit_text_rect)

        display.flip()

        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                running = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                mouse_pos = mouse.get_pos()
                # Vérification du clic sur le bouton Quit
                if quit_button[0].collidepoint(mouse_pos):
                    running = False
                # Vérification des clics sur les niveaux
                for i, (button_rect, _, _) in enumerate(buttons):
                    if button_rect.collidepoint(mouse_pos):
                        if i == 0:
                            return niveau1()
                        else:
                            print(f"Niveau {i+1} non disponible")

    return True
