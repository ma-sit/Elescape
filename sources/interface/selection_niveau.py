from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.jeu import page_jeu
from interface.menu import bouton

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
        
        btn = {
            "rect": Rect(x, y, button_width, button_height),
            "image": None,
            "a_joue_son": False,
            "text": f"Level {i+1}"
        }
        buttons.append(btn)

    while running:
        fnd = image.load("data/images/image_selection_niveau.png").convert()
        fnd = transform.scale(fnd, (rec.right, rec.bottom))
        ecr.blit(fnd, (0, 0))
        
        # Affichage titres
        ecr.blit(title, title_rect)
        ecr.blit(subtitle, subtitle_rect)
        
        # Affichage boutons avec effet de bordure
        for i, btn in enumerate(buttons):
            hover = bouton(ecr, (80, 80, 80), btn, btn["text"], son_survol, son_clicmenu, 10, surbrillance=(120, 120, 120))
        
        display.flip()

        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                running = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                mouse_pos = mouse.get_pos()
                for i, btn in enumerate(buttons):
                    if btn["rect"].collidepoint(mouse_pos):
                        son_clicmenu.play()
                        if i == 0:
                            return page_jeu(i+1)
                        else:
                            print(f"Niveau {i+1} non disponible")

    return True
