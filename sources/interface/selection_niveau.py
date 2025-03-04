from pygame import *
import sys
import os
from math import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.jeu import page_jeu
from interface.menu import bouton

def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10, width=2):
    """Dessine une ligne pointillée entre deux points"""
    x1, y1 = start_pos
    x2, y2 = end_pos
    
    # Calculer la distance et l'angle
    dx = x2 - x1
    dy = y2 - y1
    distance = sqrt(dx*dx + dy*dy)
    dashes = int(distance / dash_length)
    
    # Normaliser le vecteur de direction
    if distance > 0:
        dx = dx / distance
        dy = dy / distance
    
    # Dessiner les segments
    dash_on = True
    for i in range(dashes):
        start = (x1 + dx * i * dash_length, y1 + dy * i * dash_length)
        if dash_on:
            end = (x1 + dx * (i + 0.5) * dash_length, y1 + dy * (i + 0.5) * dash_length)
            draw.line(surface, color, start, end, width)
        dash_on = not dash_on

def selection_niveau():
    running = True
    
    # Dimensions et style pour les rectangles des niveaux
    box_width = 180
    box_height = 80
    
    # Polices et titre améliorés
    title_font = font.Font(None, 120)
    subtitle_font = font.Font(None, 40)
    level_font = font.Font(None, 40)  # Police plus grande pour les niveaux
    
    title = title_font.render("Vitanox", True, (0, 0, 0))
    subtitle = subtitle_font.render("Sélection du niveau", True, (40, 40, 40))
    
    title_rect = title.get_rect(center=(lrg//2, htr//8))
    subtitle_rect = subtitle.get_rect(center=(lrg//2, htr//8 + 80))
    
    # Définition des niveaux avec des positions ajustées pour éviter les chevauchements
    levels = [
        {"id": 1, "pos": (lrg//6, htr//4), "text": "Niveau 1", "available": True},
        {"id": 2, "pos": (lrg//2 - 120, htr//2 - 50), "text": "Niveau 2", "available": False},
        {"id": 3, "pos": (lrg//2 + 50, htr//4), "text": "Niveau 3", "available": False},
        {"id": 4, "pos": (4*lrg//5, htr//4), "text": "Niveau 4", "available": False},
        {"id": 5, "pos": (2*lrg//3, htr//2), "text": "Niveau 5", "available": False},
        {"id": 6, "pos": (lrg//6, 3*htr//5), "text": "Niveau 6", "available": False},
        {"id": 7, "pos": (lrg//2, 3*htr//4), "text": "Niveau 7", "available": False},
        {"id": 8, "pos": (4*lrg//5, 3*htr//4), "text": "Niveau 8", "available": False}
    ]
    
    # Créer des rectangles pour chaque niveau avec des états de survol et de clic
    for level in levels:
        level["rect"] = Rect(level["pos"][0] - box_width//2, level["pos"][1] - box_height//2, box_width, box_height)
        level["a_joue_son"] = False
        level["image"] = None
        level["hover"] = False
        level["shadow_offset"] = 4  # Pour l'effet d'ombre
    
    # Connexions linéaires entre les niveaux
    connections = [
        (0, 1),  # Niveau 1 -> Niveau 2
        (1, 2),  # Niveau 2 -> Niveau 3
        (2, 3),  # Niveau 3 -> Niveau 4
        (3, 4),  # Niveau 4 -> Niveau 5
        (4, 5),  # Niveau 5 -> Niveau 6
        (5, 6),  # Niveau 6 -> Niveau 7
        (6, 7)   # Niveau 7 -> Niveau 8
    ]

    # Animation et horloge
    clock = time.Clock()
    hover_scale = 1.0
    
    while running:
        dt = clock.tick(60) / 1000.0  # Pour des animations fluides
        
        try:
            # Charger et adapter l'image de fond
            fnd = image.load("data/images/image_selection_niveau.png").convert()
            fnd = transform.scale(fnd, (rec.right, rec.bottom))
        except Exception as e:
            print(f"Erreur lors du chargement de l'image de fond: {e}")
            fnd = Surface((lrg, htr))
            fnd.fill((240, 240, 245))  # Fond légèrement bleuté
        
        ecr.blit(fnd, (0, 0))
        
        # Dessiner d'abord toutes les connexions avec des lignes pointillées NOIRES
        for conn in connections:
            try:
                start_level = levels[conn[0]]
                end_level = levels[conn[1]]
                start_pos = start_level["rect"].center
                end_pos = end_level["rect"].center
                
                # Dessiner une ligne pointillée noire avec une teinte plus claire pour plus d'esthétique
                draw_dashed_line(ecr, (25, 25, 25), start_pos, end_pos, dash_length=8, width=3)
            except Exception as e:
                print(f"Erreur lors du dessin des connexions: {e}")
        
        # Afficher le titre et sous-titre
        ecr.blit(title, title_rect)
        ecr.blit(subtitle, subtitle_rect)
        
        # Mettre à jour l'état de survol
        mouse_pos = mouse.get_pos()
        for level in levels:
            level["hover"] = level["rect"].collidepoint(mouse_pos)
        
        # Dessiner d'abord les ombres des boutons
        for level in levels:
            try:
                if level["hover"]:
                    # Ombre légèrement plus grande en survol
                    shadow_offset = level["shadow_offset"] + 2
                else:
                    shadow_offset = level["shadow_offset"]
                
                # Rectangle d'ombre avec coins arrondis
                shadow_rect = Rect(
                    level["rect"].x + shadow_offset,
                    level["rect"].y + shadow_offset,
                    level["rect"].width,
                    level["rect"].height
                )
                
                # Dessiner l'ombre avec une transparence
                shadow_surface = Surface((shadow_rect.width, shadow_rect.height), SRCALPHA)
                shadow_color = (10, 10, 10, 100)  # Noir semi-transparent
                draw.rect(shadow_surface, shadow_color, Rect(0, 0, shadow_rect.width, shadow_rect.height), border_radius=15)
                ecr.blit(shadow_surface, shadow_rect)
            except Exception as e:
                print(f"Erreur lors du dessin de l'ombre pour le niveau {level['id']}: {e}")
        
        # Dessiner ensuite les boutons de niveau
        for level in levels:
            try:
                # Couleur de base et de survol 
                if level["available"]:
                    base_color = (35, 35, 40)
                    hover_color = (50, 50, 60)
                    border_color = (70, 70, 80)  # Bordure légèrement plus claire
                    text_color = (255, 255, 255)
                else:
                    base_color = (25, 25, 25)
                    hover_color = (40, 40, 40)
                    border_color = (60, 60, 60)
                    text_color = (180, 180, 180)  # Texte grisé pour niveaux non disponibles
                
                # Couleur selon l'état
                color = hover_color if level["hover"] else base_color
                
                # Surface du bouton avec coins arrondis
                button_surface = Surface((level["rect"].width, level["rect"].height), SRCALPHA)
                draw.rect(button_surface, color, Rect(0, 0, level["rect"].width, level["rect"].height), border_radius=15)
                
                # Bordure fine
                draw.rect(button_surface, border_color, Rect(0, 0, level["rect"].width, level["rect"].height), 2, border_radius=15)
                
                # Texte du niveau
                text_surf = level_font.render(level["text"], True, text_color)
                text_rect = text_surf.get_rect(center=(level["rect"].width//2, level["rect"].height//2))
                button_surface.blit(text_surf, text_rect)
                
                # Appliquer un effet de pulsation subtil sur le bouton survolé
                if level["hover"] and level["available"]:
                    hover_scale = 1.0 + sin(time.get_ticks() / 200.0) * 0.03
                    scaled_surface = transform.scale(
                        button_surface, 
                        (int(button_surface.get_width() * hover_scale), 
                         int(button_surface.get_height() * hover_scale))
                    )
                    scaled_rect = scaled_surface.get_rect(center=level["rect"].center)
                    ecr.blit(scaled_surface, scaled_rect)
                    
                    # Jouer le son au survol une seule fois
                    if not level["a_joue_son"]:
                        son_survol.play()
                        level["a_joue_son"] = True
                else:
                    ecr.blit(button_surface, level["rect"])
                    level["a_joue_son"] = False
                
                # Indicateur visuel pour le niveau disponible (petit symbole de déverrouillage)
                if level["available"]:
                    # Petit cercle vert dans le coin
                    indicator_radius = 6
                    indicator_pos = (level["rect"].right - 15, level["rect"].top + 15)
                    draw.circle(ecr, (100, 200, 100), indicator_pos, indicator_radius)
                    
            except Exception as e:
                print(f"Erreur lors du dessin du niveau {level['id']}: {e}")
        
        display.flip()

        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                running = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                mouse_pos = mouse.get_pos()
                for level in levels:
                    if level["rect"].collidepoint(mouse_pos):
                        son_clicmenu.play()
                        if level["available"]:
                            # Lancer le niveau sélectionné
                            return page_jeu(level["id"])
                        else:
                            # Indiquer que le niveau n'est pas disponible
                            print(f"{level['text']} non disponible")

    return True