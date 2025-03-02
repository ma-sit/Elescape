from pygame import *
import json
from shared.components.config import *
from interface.menu import bouton
from interface.parametres import page_parametres, page_parametres_superpose

def menu_parametres(background_image=None):
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
    
    # Dimensions du menu
    menu_width = 400
    menu_height = 350
    menu_x = (lrg - menu_width) // 2
    menu_y = (htr - menu_height) // 2
    
    # Dimensions communes pour les boutons
    button_width = 200
    button_height = 50
    button_spacing = 30
    
    # Boutons centrés
    resume_button = {
        "rect": Rect(menu_x + (menu_width - button_width) // 2, menu_y + 100, button_width, button_height),
        "image": None,
        "a_joue_son": False,
        "text": "Reprendre"
    }
    
    settings_button = {
        "rect": Rect(menu_x + (menu_width - button_width) // 2, menu_y + 100 + button_height + button_spacing, button_width, button_height),
        "image": None,
        "a_joue_son": False,
        "text": "Paramètres"
    }
    
    quit_button = {
        "rect": Rect(menu_x + (menu_width - button_width) // 2, menu_y + 100 + 2 * (button_height + button_spacing), button_width, button_height),
        "image": None,
        "a_joue_son": False,
        "text": "Quitter"
    }
    
    # Couleurs améliorées
    panel_bg_color = (20, 40, 100)        # Bleu foncé pour le fond
    panel_border_color = (80, 140, 240)   # Bleu clair pour la bordure
    button_color = (40, 80, 160)          # Couleur de base des boutons
    button_highlight = (60, 120, 220)     # Couleur de survol des boutons
    text_color = (220, 220, 255)          # Couleur du texte
    
    # Stocker l'image d'arrière-plan du jeu (sans le menu pause)
    game_background = background_image
    
    while menu_actif:
        # Si une image d'arrière-plan est fournie, l'afficher
        if game_background is not None:
            ecr.blit(game_background, (0, 0))
        
        # Créer une surface semi-transparente pour assombrir légèrement l'arrière-plan
        surf_overlay = Surface((lrg, htr), SRCALPHA)
        surf_overlay.fill((0, 0, 0, 180))  # Fond sombre semi-transparent
        ecr.blit(surf_overlay, (0, 0))
        
        # Dessiner l'ombre du panneau principal
        shadow_offset = 6
        shadow = Rect(menu_x + shadow_offset, menu_y + shadow_offset, menu_width, menu_height)
        draw.rect(ecr, (0, 0, 0, 100), shadow, border_radius=20)
        
        # Dessiner le panneau principal
        panel = Rect(menu_x, menu_y, menu_width, menu_height)
        draw.rect(ecr, panel_bg_color, panel, border_radius=20)
        draw.rect(ecr, panel_border_color, panel, 2, border_radius=20)
        
        # Titre
        titre = font.Font(None, 50).render("Pause", True, text_color)
        titre_rect = titre.get_rect(center=(menu_x + menu_width//2, menu_y + 50))
        ecr.blit(titre, titre_rect)
        
        # Dessiner les boutons avec effets
        bouton(ecr, button_color, resume_button, resume_button["text"], son_survol, son_clicmenu, 15, surbrillance=button_highlight)
        bouton(ecr, button_color, settings_button, settings_button["text"], son_survol, son_clicmenu, 15, surbrillance=button_highlight)
        bouton(ecr, button_color, quit_button, quit_button["text"], son_survol, son_clicmenu, 15, surbrillance=button_highlight)
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
                
            if evt.type == KEYDOWN and evt.key == touches['Retour']:
                menu_actif = False
                
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if resume_button["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    menu_actif = False
                    
                elif settings_button["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    try:
                        # Utiliser l'image du jeu de départ (sans le menu pause)
                        # pour afficher les paramètres directement par-dessus le jeu
                        param_result = page_parametres_superpose(game_background)
                        # Si page_parametres_superpose() retourne False, on quitte également le jeu
                        if not param_result:
                            return False
                    except Exception as e:
                        print(f"Erreur lors de l'accès aux paramètres: {e}")
                    
                elif quit_button["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    return False
    
    return True

