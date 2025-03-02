from pygame import *
from shared.components.config import *
import sys
import os

def Page(ecr, all_elements=None, discovered_elements=None):
    """Affiche la page d'encyclopédie avec une liste scrollable d'éléments
    
    Arguments:
        ecr -- Surface d'affichage pygame
        all_elements -- Dictionnaire contenant tous les éléments du jeu
        discovered_elements -- Liste des ID des éléments découverts
    """
    # Si les éléments ne sont pas fournis, utiliser des valeurs par défaut
    if all_elements is None:
        all_elements = {}
    if discovered_elements is None:
        discovered_elements = []
    
    # Capturer l'écran du jeu actuel
    game_screen = ecr.copy()
    
    # Dimensions du menu latéral
    menu_largeur = 500
    menu_x = lrg
    vitesse = 20
    menu_actif = True
    ouvert = True
    
    # Paramètres pour la grille d'éléments
    element_width = 80
    element_height = 80
    grid_padding = 20
    grid_spacing = 15
    grid_cols = 4
    grid_x = menu_x + grid_padding
    grid_y = 100  # Position y de départ pour la grille
    
    # Chargement des icônes et ressources
    try:
        lock_icon = image.load("data/images/autres/lock.png")
        lock_icon = transform.scale(lock_icon, (40, 40))
    except Exception as e:
        print(f"Erreur lors du chargement de l'icône de cadenas: {e}")
        # Créer une icône par défaut si le chargement échoue
        lock_icon = Surface((40, 40), SRCALPHA)
        draw.rect(lock_icon, (150, 150, 150), Rect(5, 5, 30, 25))
        draw.rect(lock_icon, (150, 150, 150), Rect(15, 0, 10, 35))
    
    # Paramètres pour le scroll
    scroll_offset = 0
    scroll_speed = 30
    max_visible_rows = (htr - grid_y - grid_padding) // (element_height + grid_spacing)
    total_rows = (len(all_elements) + grid_cols - 1) // grid_cols
    
    # Paramètres pour la scrollbar
    scrollbar_width = 15
    scrollbar_padding = 5
    scrollbar_x = menu_x + menu_largeur - scrollbar_width - scrollbar_padding
    scrollbar_y = grid_y
    scrollbar_height = max_visible_rows * (element_height + grid_spacing)
    scrollbar_active = False
    
    # Paramètres pour l'élément sélectionné
    selected_element = None
    
    # Polices pour le texte
    title_font = font.Font(None, 36)
    element_font = font.Font(None, 20)
    description_font = font.Font(None, 24)
    
    # Variable pour stocker le temps de la dernière action
    last_action_time = 0
    
    # Couleurs pour l'interface
    text_color = (255, 255, 255)
    grid_bg_color = (40, 40, 40)
    scrollbar_bg_color = (60, 60, 60)
    scrollbar_fg_color = (100, 100, 100)
    hover_color = (70, 70, 70)
    selected_color = (80, 100, 200)
    
    while menu_actif:
        current_time = time.get_ticks()
        
        # Afficher d'abord l'écran de jeu
        ecr.blit(game_screen, (0, 0))
        
        # Animation d'ouverture
        if ouvert and menu_x > lrg - menu_largeur:
            menu_x -= vitesse
            # Ajustement des positions de la grille et de la scrollbar
            grid_x = menu_x + grid_padding
            scrollbar_x = menu_x + menu_largeur - scrollbar_width - scrollbar_padding
        elif not ouvert and menu_x < lrg:
            menu_x += vitesse
            # Si le menu est complètement fermé, quitter la boucle
            if menu_x >= lrg:
                menu_actif = False
        
        # Dessiner le panneau latéral avec un fond semi-transparent
        panel_surface = Surface((menu_largeur, htr), SRCALPHA)
        panel_surface.fill((30, 30, 50, 240))  # Fond sombre semi-transparent
        ecr.blit(panel_surface, (menu_x, 0))
        
        # Dessiner le titre
        titre = title_font.render("Encyclopédie", True, text_color)
        titre_rect = titre.get_rect(center=(menu_x + menu_largeur//2, 50))
        ecr.blit(titre, titre_rect)
        
        # Dessiner la zone de grille (arrière-plan)
        grid_area = Rect(menu_x + grid_padding - 5, grid_y - 5, 
                         menu_largeur - 2*grid_padding - scrollbar_width - 5, 
                         max_visible_rows * (element_height + grid_spacing) + 10)
        draw.rect(ecr, grid_bg_color, grid_area, border_radius=8)
        draw.rect(ecr, (70, 70, 90), grid_area, 2, border_radius=8)
        
        # Calculer le nombre total de lignes nécessaires
        total_rows = (len(all_elements) + grid_cols - 1) // grid_cols
        max_scroll = max(0, total_rows - max_visible_rows)
        
        # Dessiner les éléments visibles
        mouse_pos = mouse.get_pos()
        hover_element = None
        
        # Paramètres pour déterminer quels éléments sont visibles
        start_row = int(scroll_offset)
        end_row = min(total_rows, start_row + max_visible_rows + 1)
        
        # Créer une liste ordonnée des éléments
        element_items = sorted(all_elements.items(), key=lambda x: int(x[0]))
        
        # Définir la zone de clippage pour les éléments
        ecr.set_clip(grid_area)
        
        for i, (elem_id, elem_data) in enumerate(element_items):
            row = i // grid_cols
            col = i % grid_cols
            
            # Ne dessiner que les éléments dans les lignes visibles
            if start_row <= row < end_row:
                # Position de l'élément avec scroll
                elem_x = grid_x + col * (element_width + grid_spacing)
                elem_y = grid_y + (row - scroll_offset) * (element_height + grid_spacing)
                
                # Créer un rect pour l'élément
                elem_rect = Rect(elem_x, elem_y, element_width, element_height)
                
                # Vérifier si la souris survole cet élément
                is_hover = elem_rect.collidepoint(mouse_pos)
                if is_hover:
                    hover_element = elem_id
                
                # Vérifier si c'est l'élément sélectionné
                is_selected = selected_element == elem_id
                
                # Couleur de fond en fonction de l'état
                if is_selected:
                    bg_color = selected_color
                    border_color = (150, 180, 255)
                elif is_hover:
                    bg_color = hover_color
                    border_color = (120, 120, 140)
                else:
                    bg_color = grid_bg_color
                    border_color = (80, 80, 100)
                
                # Dessiner le fond de l'élément
                draw.rect(ecr, bg_color, elem_rect, border_radius=8)
                draw.rect(ecr, border_color, elem_rect, 2, border_radius=8)
                
                # Vérifier si l'élément est découvert
                is_discovered = int(elem_id) in discovered_elements
                
                # Si l'élément est découvert, afficher son image et son nom
                if is_discovered:
                    try:
                        # Si l'image est une liste, prendre la première
                        img_path = elem_data["Image"]
                        if ',' in img_path:
                            img_path = img_path.split(',')[0].strip().strip('"')
                            
                        # Charger et redimensionner l'image
                        elem_img = image.load(img_path)
                        elem_img = transform.scale(elem_img, (element_width - 20, element_height - 20))
                        
                        # Centrer l'image dans son rectangle
                        img_rect = elem_img.get_rect(center=elem_rect.center)
                        ecr.blit(elem_img, img_rect)
                        
                        # Afficher le nom en bas de l'élément (optionnel si pas assez de place)
                        if element_height >= 60:  # Seulement si assez d'espace
                            name_text = element_font.render(elem_data["Nom"][:10], True, text_color)
                            name_rect = name_text.get_rect(midbottom=(elem_rect.centerx, elem_rect.bottom - 5))
                            ecr.blit(name_text, name_rect)
                    except Exception as e:
                        print(f"Erreur lors de l'affichage de l'élément {elem_id}: {e}")
                        # Afficher un placeholder en cas d'erreur
                        draw.rect(ecr, (100, 50, 50), Rect(elem_x + 10, elem_y + 10, element_width - 20, element_height - 20))
                
                # Sinon, afficher un cadenas
                else:
                    # Dessiner un fond grisé
                    draw.rect(ecr, (50, 50, 60), Rect(elem_x + 10, elem_y + 10, element_width - 20, element_height - 20))
                    
                    # Afficher le cadenas
                    lock_rect = lock_icon.get_rect(center=elem_rect.center)
                    ecr.blit(lock_icon, lock_rect)
        
        # Réinitialiser la zone de clippage
        ecr.set_clip(None)
        
        # Dessiner la scrollbar si nécessaire
        if total_rows > max_visible_rows:
            # Fond de la scrollbar
            scrollbar_bg = Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
            draw.rect(ecr, scrollbar_bg_color, scrollbar_bg, border_radius=4)
            
            # Poignée (thumb) de la scrollbar
            thumb_height = max(30, scrollbar_height * (max_visible_rows / total_rows))
            thumb_position = scrollbar_y + (scroll_offset / max_scroll) * (scrollbar_height - thumb_height)
            
            thumb_rect = Rect(scrollbar_x, thumb_position, scrollbar_width, thumb_height)
            draw.rect(ecr, scrollbar_fg_color, thumb_rect, border_radius=4)
            
            # Surbrillance si la souris est sur la scrollbar
            if thumb_rect.collidepoint(mouse_pos) or scrollbar_active:
                draw.rect(ecr, (130, 130, 150), thumb_rect, 2, border_radius=4)
        
        # Afficher les informations de l'élément sélectionné
        if selected_element is not None and int(selected_element) in discovered_elements:
            # Zone d'information en bas
            info_area = Rect(menu_x + grid_padding, grid_y + scrollbar_height + 20,
                           menu_largeur - 2*grid_padding, 150)
            draw.rect(ecr, (40, 45, 70), info_area, border_radius=8)
            draw.rect(ecr, (70, 80, 120), info_area, 2, border_radius=8)
            
            # Afficher les détails de l'élément sélectionné
            elem_data = all_elements[selected_element]
            
            # Titre (nom de l'élément)
            detail_title = title_font.render(elem_data["Nom"], True, text_color)
            ecr.blit(detail_title, (info_area.x + 15, info_area.y + 15))
            
            # Créations possibles
            if elem_data["Creations"]:
                creations_text = description_font.render("Peut créer:", True, (200, 200, 255))
                ecr.blit(creations_text, (info_area.x + 15, info_area.y + 55))
                
                # Afficher les noms des créations possibles
                creation_y = info_area.y + 85
                for i, creation_id in enumerate(elem_data["Creations"][:3]):  # Limiter à 3 pour l'espace
                    if str(creation_id) in all_elements:
                        creation_name = all_elements[str(creation_id)]["Nom"]
                        if int(creation_id) in discovered_elements:
                            creation_color = (180, 255, 180)  # Vert pour les éléments découverts
                        else:
                            creation_name = "???"
                            creation_color = (255, 180, 180)  # Rouge pour les éléments non découverts
                        
                        creation_text = description_font.render(f"- {creation_name}", True, creation_color)
                        ecr.blit(creation_text, (info_area.x + 35, creation_y + i*25))
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
                
            # Gestion du bouton Échap pour fermer
            elif evt.type == KEYDOWN and evt.key == K_ESCAPE:
                if ouvert:
                    ouvert = False
                else:
                    menu_actif = False
            
            # Gestion de la molette pour le scroll
            elif evt.type == MOUSEBUTTONDOWN:
                if evt.button == 4:  # Molette vers le haut
                    scroll_offset = max(0, scroll_offset - 0.5)
                elif evt.button == 5:  # Molette vers le bas
                    scroll_offset = min(max_scroll, scroll_offset + 0.5)
                
                # Gestion du clic sur un élément
                elif evt.button == 1:
                    # Vérifier si le clic est sur un élément
                    if hover_element is not None:
                        selected_element = hover_element
                    
                    # Gestion du clic sur la scrollbar
                    if total_rows > max_visible_rows:
                        scrollbar_area = Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
                        if scrollbar_area.collidepoint(evt.pos):
                            scrollbar_active = True
                            # Déplacer directement la scrollbar à la position du clic
                            y_rel = evt.pos[1] - scrollbar_y
                            scroll_ratio = y_rel / scrollbar_height
                            scroll_offset = min(max_scroll, max(0, scroll_ratio * total_rows))
                
            # Gestion du relâchement du bouton de la souris
            elif evt.type == MOUSEBUTTONUP:
                if evt.button == 1:
                    scrollbar_active = False
            
            # Gestion du déplacement de la scrollbar
            elif evt.type == MOUSEMOTION and scrollbar_active:
                # Calculer la nouvelle position du scroll
                y_rel = evt.pos[1] - scrollbar_y
                scroll_ratio = y_rel / scrollbar_height
                scroll_offset = min(max_scroll, max(0, scroll_ratio * total_rows))
    
    return True
