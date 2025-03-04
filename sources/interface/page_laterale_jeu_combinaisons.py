from pygame import *
from shared.components.config import *
import sys
import os
import math

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
    menu_largeur = 550
    menu_x = lrg
    vitesse = 20
    menu_actif = True
    ouvert = True
    
    # Paramètres pour la grille d'éléments
    element_width = 85
    element_height = 85
    grid_padding = 20
    grid_spacing = 12
    grid_cols = 4
    grid_x = menu_x + grid_padding
    grid_y = 120  # Position y de départ pour la grille
    
    # Chargement des icônes et ressources - création manuelle pour éviter les erreurs de fichiers
    icons = {}
    
    # Icône de cadenas pour éléments verrouillés (créée manuellement)
    lock_icon = Surface((40, 40), SRCALPHA)
    draw.rect(lock_icon, (150, 150, 150), Rect(5, 5, 30, 25))
    draw.rect(lock_icon, (150, 150, 150), Rect(15, 0, 10, 35))
    icons["lock"] = lock_icon
    
    # Icône de fermeture (X)
    close_icon = Surface((25, 25), SRCALPHA)
    draw.line(close_icon, (220, 220, 220), (5, 5), (20, 20), 2)
    draw.line(close_icon, (220, 220, 220), (5, 20), (20, 5), 2)
    icons["close"] = close_icon
    
    # Cache pour les images des éléments (évite de recharger à chaque fois)
    image_cache = {}
    
    # Paramètres pour le scroll
    scroll_offset = 0
    scroll_target = 0  # Pour l'animation fluide
    scroll_animation_speed = 0.2  # Vitesse d'animation
    max_visible_rows = (htr - grid_y - grid_padding - 170) // (element_height + grid_spacing)
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
    
    # Effet de flottement
    float_offset = 0
    float_direction = 0.05
    
    # Polices pour le texte
    title_font = font.Font(None, 42)
    subtitle_font = font.Font(None, 32)
    element_font = font.Font(None, 20)
    description_font = font.Font(None, 24)
    small_font = font.Font(None, 18)
    stats_font = font.Font(None, 22)
    
    # Horloge pour le framerate
    clock = time.Clock()
    
    # Couleurs pour l'interface
    color_scheme = {
        "text": (255, 255, 255),
        "text_dim": (200, 200, 220),
        "panel_bg": (25, 25, 45, 240),
        "panel_dark": (15, 15, 35),
        "panel_light": (40, 45, 70),
        "grid_bg": (30, 30, 50),
        "border_dark": (60, 65, 90),
        "border_light": (80, 90, 130),
        "hover": (60, 70, 120),
        "selected": (70, 90, 150),
        "highlight": (100, 150, 255),
        "positive": (120, 255, 120),
        "warning": (255, 220, 100),
        "negative": (255, 120, 120),
        "scrollbar_bg": (50, 50, 70),
        "scrollbar_fg": (80, 90, 130),
        "button_bg": (50, 60, 100),
        "button_hover": (70, 80, 140),
        "info_bg": (40, 50, 90),
        "category_1": (70, 130, 180),  # Bleu - Éléments de base
        "category_2": (70, 160, 70),   # Vert - Plantes
        "category_3": (160, 120, 70),  # Marron - Animaux
        "category_4": (150, 70, 70)    # Rouge - Outils
    }
    
    # Assignation des catégories aux éléments
    element_categories = {}
    
    # Affecter des catégories aux éléments selon leur ID et type
    for elem_id, elem_data in all_elements.items():
        try:
            elem_id = int(elem_id)
            if elem_id == 0:  # Humain
                category = 1  # Base
            elif elem_id in [1, 5, 6, 11]:  # Arbre, Champignon, Foin, Pommier
                category = 2  # Plantes
            elif elem_id == 12:  # Cochon et autres animaux
                category = 3  # Animaux
            elif elem_id in [7, 8, 9]:  # Puit, Seau, Baril
                category = 4  # Outils
            else:
                category = 1  # Par défaut: Base
            
            # Attribuer une catégorie basée sur le type dans les données si disponible
            if elem_data.get("Type", "").lower() == "animal":
                category = 3  # Animaux
                
            element_categories[elem_id] = category
        except Exception as e:
            print(f"Erreur lors de l'assignation de catégorie pour {elem_id}: {e}")
            element_categories[elem_id] = 1  # Catégorie par défaut
    
    # Bouton de fermeture
    close_button = {
        "rect": Rect(menu_x + menu_largeur - 40, menu_x + 20, 30, 30),
        "hover": False
    }
    
    # Variables pour les effets visuels et animations
    pulse_time = 0
    
    # Variable pour les statistiques d'avancement
    try:
        completion_percentage = len(discovered_elements) / len(all_elements) * 100 if all_elements else 0
    except:
        completion_percentage = 0
    
    # Fonction pour déterminer la catégorie d'un élément
    def get_element_category(elem_id):
        try:
            return element_categories.get(int(elem_id), 1)  # Par défaut: catégorie Base
        except:
            return 1
    
    # Variables pour le compteur d'éléments
    count_discovered = len(discovered_elements)
    count_total = len(all_elements)
    
    # Boucle principale du menu
    while menu_actif:
        dt = clock.tick(60) / 1000.0  # Delta time en secondes
        current_time = time.get_ticks()
        mouse_pos = mouse.get_pos()
        
        # Mise à jour de l'animation du scroll
        if abs(scroll_target - scroll_offset) > 0.01:
            scroll_offset += (scroll_target - scroll_offset) * scroll_animation_speed
        
        # Mise à jour de l'effet de flottement
        float_offset += float_direction
        if float_offset > 3 or float_offset < -3:
            float_direction *= -1
        
        # Afficher d'abord l'écran de jeu
        ecr.blit(game_screen, (0, 0))
        
        # Animation d'ouverture/fermeture du menu
        target_x = lrg - menu_largeur if ouvert else lrg
        
        if abs(menu_x - target_x) > 1:
            menu_x += (target_x - menu_x) * 0.2
            menu_animation = abs((menu_x - lrg) / (lrg - (lrg - menu_largeur)))
        else:
            menu_x = target_x
            if not ouvert and menu_x >= lrg - 1:
                menu_actif = False
                break
        
        # Ajustement des positions de la grille et de la scrollbar
        grid_x = menu_x + grid_padding
        scrollbar_x = menu_x + menu_largeur - scrollbar_width - scrollbar_padding
        
        # Effet de flou semi-transparent sur le jeu
        try:
            overlay = Surface((lrg, htr), SRCALPHA)
            overlay_alpha = int(180 * min(1.0, max(0.0, menu_animation)))
            overlay.fill((0, 0, 20, overlay_alpha))
            ecr.blit(overlay, (0, 0))
        except:
            # En cas d'erreur, utiliser une approche plus simple
            dark_overlay = Surface((lrg, htr))
            dark_overlay.fill((0, 0, 20))
            dark_overlay.set_alpha(120)
            ecr.blit(dark_overlay, (0, 0))
        
        # Dessin de l'ombre du panneau pour effet de flottement
        shadow_panel = Surface((menu_largeur, htr), SRCALPHA)
        shadow_panel.fill((0, 0, 0, 100))
        ecr.blit(shadow_panel, (menu_x + 8, 8 + float_offset))
        
        # Dessin du panneau latéral avec coin très arrondis
        panel_surface = Surface((menu_largeur, htr), SRCALPHA)
        panel_surface.fill(color_scheme["panel_bg"])
        
        # Ajouter un léger dégradé sur les bords pour le style
        try:
            side_fade = Surface((20, htr), SRCALPHA)
            for i in range(20):
                alpha = 100 - i * 5
                draw.line(side_fade, (0, 0, 0, alpha), (i, 0), (i, htr), 1)
            panel_surface.blit(side_fade, (0, 0))
            panel_surface.blit(transform.flip(side_fade, True, False), (menu_largeur - 20, 0))
        except:
            # Ignorer les dégradés en cas d'erreur
            pass
        
        # Appliquer un masque avec des coins très arrondis au panneau
        try:
            mask = Surface((menu_largeur, htr), SRCALPHA)
            mask.fill((0, 0, 0, 0))
            radius = 30  # Rayon des coins arrondis
            
            # Dessiner un rectangle avec des coins très arrondis
            draw.rect(mask, (255, 255, 255, 255), Rect(0, 0, menu_largeur, htr), border_radius=radius)
            
            # Appliquer le masque
            panel_surface.blit(mask, (0, 0), special_flags=BLEND_RGBA_MULT)
        except:
            # Si l'application du masque échoue, garder le panneau rectangulaire
            pass
        
        # Dessiner le panneau avec l'effet de flottement
        ecr.blit(panel_surface, (menu_x, 0 + float_offset))
        
        # Dessiner une bordure brillante avec des coins arrondis
        try:
            draw.rect(ecr, color_scheme["border_light"], 
                    Rect(menu_x, 0 + float_offset, menu_largeur, htr), 
                    2, border_radius=30)
            
            # Ajouter une légère lueur sur le bord supérieur pour l'effet de flottement
            glow_rect = Rect(menu_x + 10, 10 + float_offset, menu_largeur - 20, 5)
            draw.rect(ecr, (100, 120, 180, 100), glow_rect, border_radius=5)
        except:
            # En cas d'erreur, utiliser une bordure simple
            pass
        
        # Dessin du titre avec effet d'ombre
        try:
            titre_shadow = title_font.render("Encyclopédie", True, (0, 0, 0))
            titre = title_font.render("Encyclopédie", True, color_scheme["text"])
            ecr.blit(titre_shadow, (menu_x + menu_largeur//2 - titre.get_width()//2 + 2, 32 + float_offset))
            ecr.blit(titre, (menu_x + menu_largeur//2 - titre.get_width()//2, 30 + float_offset))
        except:
            # En cas d'erreur, utiliser un rendu plus simple
            titre = title_font.render("Encyclopédie", True, color_scheme["text"])
            ecr.blit(titre, (menu_x + menu_largeur//2 - titre.get_width()//2, 30 + float_offset))
        
        # Afficher le compteur d'éléments découverts
        try:
            counter_text = f"{count_discovered}/{count_total} éléments découverts ({int(completion_percentage)}%)"
            counter_surface = stats_font.render(counter_text, True, color_scheme["text_dim"])
            counter_rect = counter_surface.get_rect(midtop=(menu_x + menu_largeur//2, 65 + float_offset))
            ecr.blit(counter_surface, counter_rect)
        except:
            # Ignorer en cas d'erreur
            pass
        
        # Dessiner l'ombre de la zone de grille pour effet de flottement
        grid_shadow = Rect(menu_x + grid_padding - 5 + 6, grid_y - 5 + 6 + float_offset, 
                         menu_largeur - 2*grid_padding - scrollbar_width - 5, 
                         max_visible_rows * (element_height + grid_spacing) + 10)
        draw.rect(ecr, (0, 0, 0, 80), grid_shadow, border_radius=20)
        
        # Dessiner la zone de grille (arrière-plan) avec coins plus arrondis
        grid_area = Rect(menu_x + grid_padding - 5, grid_y - 5 + float_offset, 
                        menu_largeur - 2*grid_padding - scrollbar_width - 5, 
                        max_visible_rows * (element_height + grid_spacing) + 10)
        
        # Créer un effet de profondeur avec un rectangle d'ombre
        shadow_area = Rect(grid_area.x + 3, grid_area.y + 3, grid_area.width, grid_area.height)
        draw.rect(ecr, (15, 15, 30), shadow_area, border_radius=20)
        
        # Rectangle principal avec coins plus arrondis
        draw.rect(ecr, color_scheme["grid_bg"], grid_area, border_radius=20)
        
        # Bordure plus fine et élégante
        draw.rect(ecr, color_scheme["border_dark"], grid_area, 1, border_radius=20)
        
        # Ajouter un léger effet de brillance en haut
        highlight = Rect(grid_area.x + 3, grid_area.y + 3, grid_area.width - 6, 15)
        highlight_color = (40, 45, 70)
        draw.rect(ecr, highlight_color, highlight, border_radius=10)
        
        # Calculer le nombre total de lignes nécessaires
        total_rows = (len(all_elements) + grid_cols - 1) // grid_cols
        max_scroll = max(0, total_rows - max_visible_rows)
        
        # Limiter la position de défilement
        scroll_target = max(0, min(scroll_target, max_scroll))
        
        # Animations pulsatoires pour les éléments
        try:
            pulse_factor = 0.03 * math.sin(current_time / 300)
        except:
            pulse_factor = 0
        
        # Dessiner les éléments visibles
        hover_element = None
        
        # Paramètres pour déterminer quels éléments sont visibles
        start_row = int(scroll_offset)
        end_row = min(total_rows, start_row + max_visible_rows + 1)
        
        # Définir la zone de clippage pour les éléments
        ecr.set_clip(grid_area)
        
        # Dessiner les éléments
        element_items = sorted(all_elements.items(), key=lambda x: int(x[0]))
        
        for i, (elem_id, elem_data) in enumerate(element_items):
            row = i // grid_cols
            col = i % grid_cols
            
            # Ne dessiner que les éléments dans les lignes visibles
            if start_row <= row < end_row:
                # Position de l'élément avec scroll
                elem_x = grid_x + col * (element_width + grid_spacing)
                elem_y = grid_y + (row - scroll_offset) * (element_height + grid_spacing) + float_offset
                
                # Effet de pulsation pour les éléments nouvellement découverts (simulation)
                elem_scale = 1.0
                
                # Créer un rect pour l'élément
                elem_rect = Rect(elem_x, elem_y, element_width, element_height)
                
                # Vérifier si la souris survole cet élément
                is_hover = elem_rect.collidepoint(mouse_pos)
                if is_hover and grid_area.collidepoint(mouse_pos):
                    hover_element = elem_id
                    # Effet de survol: légère augmentation de taille
                    elem_scale = 1.05
                
                # Vérifier si c'est l'élément sélectionné
                is_selected = selected_element == elem_id
                
                # Couleur de fond en fonction de l'état
                if is_selected:
                    # Pulsation plus prononcée pour l'élément sélectionné
                    try:
                        elem_scale = 1.07 + pulse_factor
                    except:
                        elem_scale = 1.07
                    bg_color = color_scheme["selected"]
                    border_color = color_scheme["highlight"]
                elif is_hover:
                    bg_color = color_scheme["hover"]
                    border_color = color_scheme["border_light"]
                else:
                    bg_color = color_scheme["grid_bg"]
                    border_color = color_scheme["border_dark"]
                
                # Appliquer une couleur subtile selon la catégorie
                try:
                    category = get_element_category(elem_id)
                    if category > 0 and category < 5:  # Limiter à 4 catégories
                        # Mélanger la couleur de catégorie avec la couleur de fond
                        cat_color_key = f"category_{category}"
                        if cat_color_key in color_scheme:
                            cat_color = color_scheme[cat_color_key]
                            bg_color = (
                                int(bg_color[0] * 0.7 + cat_color[0] * 0.3),
                                int(bg_color[1] * 0.7 + cat_color[1] * 0.3),
                                int(bg_color[2] * 0.7 + cat_color[2] * 0.3)
                            )
                except:
                    # Ignorer les couleurs de catégorie en cas d'erreur
                    pass
                
                # Appliquer l'effet d'échelle
                try:
                    if elem_scale != 1.0:
                        center_x, center_y = elem_rect.center
                        elem_width_scaled = int(element_width * elem_scale)
                        elem_height_scaled = int(element_height * elem_scale)
                        elem_rect = Rect(0, 0, elem_width_scaled, elem_height_scaled)
                        elem_rect.center = (center_x, center_y)
                except:
                    # En cas d'erreur, réinitialiser le rectangle
                    elem_rect = Rect(elem_x, elem_y, element_width, element_height)
                
                # Dessiner l'ombre de l'élément pour effet de flottement
                shadow_rect = elem_rect.copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                try:
                    draw.rect(ecr, (10, 10, 20), shadow_rect, border_radius=15)
                except:
                    # En cas d'erreur, ignorer l'ombre
                    pass
                
                # Dessiner le fond de l'élément avec des coins bien arrondis
                try:
                    draw.rect(ecr, bg_color, elem_rect, border_radius=15)
                    draw.rect(ecr, border_color, elem_rect, 2, border_radius=15)
                    
                    # Ajouter un léger dégradé/éclat en haut de l'élément
                    highlight_rect = Rect(elem_rect.x + 3, elem_rect.y + 3, elem_rect.width - 6, 10)
                    highlight_color = (
                        min(255, bg_color[0] + 30),
                        min(255, bg_color[1] + 30),
                        min(255, bg_color[2] + 30),
                    )
                    draw.rect(ecr, highlight_color, highlight_rect, border_radius=8)
                except:
                    # En cas d'erreur, utiliser un rectangle simple
                    draw.rect(ecr, bg_color, elem_rect)
                    draw.rect(ecr, border_color, elem_rect, 2)
                
                # Vérifier si l'élément est découvert
                is_discovered = int(elem_id) in discovered_elements
                
                # Si l'élément est découvert, afficher son image et son nom
                if is_discovered:
                    try:
                        # Utiliser le cache d'images si disponible
                        if elem_id in image_cache:
                            elem_img = image_cache[elem_id]
                        else:
                            # Si l'image est une liste, prendre la première
                            img_path = elem_data["Image"]
                            if ',' in img_path:
                                img_path = img_path.split(',')[0].strip().strip('"')
                                
                            # Charger et redimensionner l'image
                            elem_img = image.load(img_path)
                            
                            # Calculer les dimensions pour préserver le ratio
                            img_w, img_h = elem_img.get_size()
                            max_dim = min(elem_rect.width, elem_rect.height) - 25
                            scale_factor = min(max_dim / img_w, max_dim / img_h)
                            new_w, new_h = int(img_w * scale_factor), int(img_h * scale_factor)
                            
                            elem_img = transform.scale(elem_img, (new_w, new_h))
                            
                            # Stocker dans le cache
                            image_cache[elem_id] = elem_img
                        
                        # Centrer l'image dans son rectangle
                        img_rect = elem_img.get_rect(center=elem_rect.center)
                        img_rect.y -= 5  # Décaler légèrement vers le haut pour le texte
                        ecr.blit(elem_img, img_rect)
                        
                        # Afficher le nom en bas de l'élément
                        name = elem_data["Nom"]
                        if len(name) > 12:
                            name = name[:10] + "..."
                            
                        name_text = element_font.render(name, True, color_scheme["text"])
                        name_rect = name_text.get_rect(midbottom=(elem_rect.centerx, elem_rect.bottom - 5))
                        ecr.blit(name_text, name_rect)
                        
                        # Indicateur de catégorie (petit cercle coloré)
                        category = get_element_category(elem_id)
                        if category > 0 and category < 5:  # Limiter à 4 catégories
                            cat_color_key = f"category_{category}"
                            if cat_color_key in color_scheme:
                                cat_color = color_scheme[cat_color_key]
                                draw.circle(ecr, cat_color, (elem_rect.left + 10, elem_rect.top + 10), 5)
                        
                    except Exception as e:
                        # Afficher un placeholder en cas d'erreur
                        draw.rect(ecr, (80, 40, 40), Rect(elem_rect.x + 10, elem_rect.y + 10, 
                                                        elem_rect.width - 20, elem_rect.height - 20))
                        error_text = small_font.render("Erreur", True, color_scheme["text"])
                        ecr.blit(error_text, (elem_rect.centerx - error_text.get_width()//2, 
                                            elem_rect.centery - error_text.get_height()//2))
                
                # Sinon, afficher un cadenas et une silhouette
                else:
                    try:
                        # Utiliser un fond mystérieux avec effet de brillance, mais pas de silhouette grise
                        
                        # Créer un dégradé subtil pour le fond au lieu d'un rectangle gris
                        gradient_rect = Rect(elem_rect.x + 8, elem_rect.y + 8, 
                                          elem_rect.width - 16, elem_rect.height - 16)
                        
                        # Déterminer une couleur de fond basée sur la catégorie
                        category = get_element_category(elem_id)
                        if category == 1:  # Base
                            gradient_color = (30, 30, 55)
                        elif category == 2:  # Plantes
                            gradient_color = (20, 40, 30)
                        elif category == 3:  # Animaux
                            gradient_color = (40, 30, 20)
                        elif category == 4:  # Outils
                            gradient_color = (40, 25, 25)
                        else:
                            gradient_color = (30, 30, 50)
                        
                        # Dessiner un fond élégant avec dégradé
                        draw.rect(ecr, gradient_color, gradient_rect, border_radius=10)
                        
                        # Ajouter un effet de brillance subtil en haut
                        highlight_rect = Rect(gradient_rect.x + 5, gradient_rect.y + 5, 
                                           gradient_rect.width - 10, 8)
                        highlight_color = (
                            min(255, gradient_color[0] + 15),
                            min(255, gradient_color[1] + 15),
                            min(255, gradient_color[2] + 15)
                        )
                        draw.rect(ecr, highlight_color, highlight_rect, border_radius=4)
                            
                        # Afficher un cadenas stylisé avec effet de brillance
                        lock_rect = icons["lock"].get_rect(center=elem_rect.center)
                        
                        # Ajouter un léger effet de lueur autour du cadenas
                        glow_size = 3
                        glow_surface = Surface((lock_rect.width + glow_size*2, lock_rect.height + glow_size*2), SRCALPHA)
                        glow_rect = Rect(glow_size, glow_size, lock_rect.width, lock_rect.height)
                        
                        # Réduire l'opacité pour les éléments récemment survolés
                        lock_alpha = 180 if elem_rect.collidepoint(mouse_pos) else 220
                        
                        # Appliquer l'icône du cadenas avec une légère transparence
                        lock_copy = icons["lock"].copy()
                        lock_copy.set_alpha(lock_alpha)
                        ecr.blit(lock_copy, lock_rect)
                        
                        # Texte "???" avec style amélioré - plus petit et plus discret
                        unknown_text = element_font.render("???", True, (180, 180, 210))
                        unknown_rect = unknown_text.get_rect(midbottom=(elem_rect.centerx, elem_rect.bottom - 5))
                        ecr.blit(unknown_text, unknown_rect)
                    except:
                        # En cas d'erreur, afficher simplement un rectangle
                        draw.rect(ecr, (40, 40, 55), Rect(elem_rect.x + 10, elem_rect.y + 10, 
                                                     elem_rect.width - 20, elem_rect.height - 20))
        
        # Si la liste est vide
        if not all_elements:
            no_result_text = description_font.render("Aucun élément trouvé", True, color_scheme["text_dim"])
            no_result_rect = no_result_text.get_rect(center=(grid_area.centerx, grid_area.centery))
            ecr.blit(no_result_text, no_result_rect)
        
        # Réinitialiser la zone de clippage
        ecr.set_clip(None)
        
        # Dessiner la scrollbar si nécessaire
        if total_rows > max_visible_rows:
            # Fond de la scrollbar
            scrollbar_bg = Rect(scrollbar_x, scrollbar_y + float_offset, scrollbar_width, scrollbar_height)
            draw.rect(ecr, color_scheme["scrollbar_bg"], scrollbar_bg, border_radius=8)
            
            # Poignée (thumb) de la scrollbar
            thumb_height = max(30, scrollbar_height * (max_visible_rows / total_rows))
            thumb_position = scrollbar_y + (scroll_offset / max_scroll) * (scrollbar_height - thumb_height)
            
            thumb_rect = Rect(scrollbar_x, thumb_position + float_offset, scrollbar_width, thumb_height)
            draw.rect(ecr, color_scheme["scrollbar_fg"], thumb_rect, border_radius=8)
            
            # Surbrillance si la souris est sur la scrollbar
            if thumb_rect.collidepoint(mouse_pos) or scrollbar_active:
                draw.rect(ecr, color_scheme["highlight"], thumb_rect, 2, border_radius=8)
        
        # Dessiner l'ombre du panneau d'informations pour effet de flottement
        if selected_element is not None and int(selected_element) in discovered_elements:
            info_height = 220
            info_shadow = Rect(menu_x + grid_padding + 6, grid_y + scrollbar_height + 20 + 6 + float_offset,
                             menu_largeur - 2*grid_padding, info_height)
            draw.rect(ecr, (0, 0, 0, 80), info_shadow, border_radius=25)
        
        # Afficher les informations de l'élément sélectionné
        if selected_element is not None and int(selected_element) in discovered_elements:
            # Zone d'information en bas avec design amélioré
            info_height = 220
            info_area = Rect(menu_x + grid_padding, grid_y + scrollbar_height + 20 + float_offset,
                         menu_largeur - 2*grid_padding, info_height)
            
            # Effet d'ombre pour donner de la profondeur
            shadow_area = Rect(info_area.x + 3, info_area.y + 3, info_area.width, info_area.height)
            draw.rect(ecr, (25, 30, 50), shadow_area, border_radius=22)
            
            # Rectangle principal avec coins plus arrondis
            draw.rect(ecr, color_scheme["info_bg"], info_area, border_radius=22)
            
            # Bordure plus subtile
            draw.rect(ecr, color_scheme["border_light"], info_area, 1, border_radius=22)
            
            # Ajouter un effet de dégradé en haut
            highlight = Rect(info_area.x + 4, info_area.y + 4, info_area.width - 8, 20)
            highlight_color = (50, 60, 100)
            draw.rect(ecr, highlight_color, highlight, border_radius=12)
            
            try:
                # Ajouter un léger effet de dégradé
                gradient = Surface((info_area.width, 20), SRCALPHA)
                for i in range(20):
                    alpha = 80 - i * 4
                    draw.line(gradient, (0, 0, 0, alpha), (0, i), (info_area.width, i), 1)
                ecr.blit(gradient, (info_area.x, info_area.y))
            except:
                # Ignorer en cas d'erreur
                pass
            
            # Afficher les détails de l'élément sélectionné
            elem_data = all_elements[selected_element]
            
            # Côté gauche: image et nom
            try:
                # Charger l'image si nécessaire
                if selected_element in image_cache:
                    detail_img = image_cache[selected_element]
                else:
                    # Charger l'image
                    img_path = elem_data["Image"]
                    if ',' in img_path:
                        img_path = img_path.split(',')[0].strip().strip('"')
                    
                    detail_img = image.load(img_path)
                    
                    # Redimensionner pour l'affichage dans les détails
                    img_w, img_h = detail_img.get_size()
                    max_dim = 100  # Taille maximale pour l'image de détail
                    scale_factor = min(max_dim / img_w, max_dim / img_h)
                    new_w, new_h = int(img_w * scale_factor), int(img_h * scale_factor)
                    
                    detail_img = transform.scale(detail_img, (new_w, new_h))
                    
                img_rect = detail_img.get_rect(topleft=(info_area.x + 20, info_area.y + 20))
                ecr.blit(detail_img, img_rect)
                
                # Nom de l'élément avec effet d'ombre
                detail_name_shadow = subtitle_font.render(elem_data["Nom"], True, (0, 0, 0))
                detail_name = subtitle_font.render(elem_data["Nom"], True, color_scheme["highlight"])
                
                name_x = img_rect.right + 15
                name_y = info_area.y + 30
                ecr.blit(detail_name_shadow, (name_x + 1, name_y + 1))
                ecr.blit(detail_name, (name_x, name_y))
                
                # Type (catégorie)
                category = get_element_category(int(selected_element))
                if category > 0 and category < 5:  # Limiter à 4 catégories
                    cat_names = ["Base", "Plantes", "Animaux", "Outils"]
                    cat_name = cat_names[category-1] if category-1 < len(cat_names) else "Autre"
                    cat_color_key = f"category_{category}"
                    cat_color = color_scheme[cat_color_key] if cat_color_key in color_scheme else color_scheme["text"]
                    
                    type_text = small_font.render(f"Catégorie: {cat_name}", True, cat_color)
                    ecr.blit(type_text, (name_x, name_y + 35))
                
                # Côté droit: propriétés et informations
                right_x = info_area.centerx + 20
                
                # Propriétés principales
                props_y = info_area.y + 25
                props_spacing = 25
                
                # Est-ce que l'élément disparaît après fusion
                dr_text = "Se consomme: " + ("Oui" if elem_data["DR"] == 0 else "Non")
                dr_surface = description_font.render(dr_text, True, 
                                                  color_scheme["warning"] if elem_data["DR"] == 0 else color_scheme["positive"])
                ecr.blit(dr_surface, (right_x, props_y))
                
                # Nombre de créations possibles
                creation_count = len(elem_data["Creations"]) if elem_data["Creations"] else 0
                creation_text = f"Combinaisons: {creation_count}"
                creation_surface = description_font.render(creation_text, True, color_scheme["text"])
                ecr.blit(creation_surface, (right_x, props_y + props_spacing))
                
                # Section du bas: créations possibles
                bottom_y = info_area.y + 120
                
                # Ligne de séparation
                separator_y = bottom_y - 15
                draw.line(ecr, color_scheme["border_dark"], 
                        (info_area.x + 15, separator_y), 
                        (info_area.right - 15, separator_y), 1)
                
                # Titre "Combinaisons possibles"
                title_y = bottom_y
                if elem_data["Creations"]:
                    recipe_title = description_font.render("Peut créer:", True, color_scheme["text"])
                    ecr.blit(recipe_title, (info_area.x + 20, title_y))
                    
                    # Afficher les combinaisons sous forme d'icônes avec texte
                    recipe_x = info_area.x + 20
                    recipe_y = title_y + 30
                    recipe_spacing = 75
                    
                    for i, creation_id in enumerate(elem_data["Creations"][:4]):  # Limiter à 4 pour l'espace
                        if i >= 4:  # Limiter à 4 pour ne pas déborder
                            # Indiquer qu'il y en a plus
                            more_text = small_font.render("+ d'autres...", True, color_scheme["text_dim"])
                            ecr.blit(more_text, (recipe_x, recipe_y + 15))
                            break
                            
                        # Dessiner chaque recette comme miniature + texte
                        if str(creation_id) in all_elements:
                            creation_data = all_elements[str(creation_id)]
                            
                            # Position de cette recette
                            this_x = recipe_x + i * recipe_spacing
                            
                            # Cadre de la recette
                            recipe_frame = Rect(this_x, recipe_y, 65, 65)
                            
                            # Effet d'ombre pour effet de flottement
                            recipe_shadow = Rect(this_x + 2, recipe_y + 2, 65, 65)
                            draw.rect(ecr, (20, 20, 30), recipe_shadow, border_radius=12)
                            
                            if int(creation_id) in discovered_elements:
                                # Élément découvert: montrer l'image et le nom
                                try:
                                    # Charger l'image si nécessaire
                                    if creation_id in image_cache:
                                        recipe_img = image_cache[creation_id]
                                    else:
                                        img_path = creation_data["Image"]
                                        if ',' in img_path:
                                            img_path = img_path.split(',')[0].strip().strip('"')
                                        
                                        recipe_img = image.load(img_path)
                                        
                                        # Redimensionner pour l'icône
                                        img_w, img_h = recipe_img.get_size()
                                        max_dim = 45
                                        scale_factor = min(max_dim / img_w, max_dim / img_h)
                                        new_w, new_h = int(img_w * scale_factor), int(img_h * scale_factor)
                                        
                                        recipe_img = transform.scale(recipe_img, (new_w, new_h))
                                        image_cache[creation_id] = recipe_img
                                    
                                    # Dessiner le fond avec la couleur de la catégorie
                                    cat = get_element_category(creation_id)
                                    cat_color_key = f"category_{cat}"
                                    cat_color = color_scheme[cat_color_key] if cat_color_key in color_scheme else color_scheme["border_light"]
                                    
                                    # Cadre arrondi avec couleur de catégorie
                                    draw.rect(ecr, (50, 50, 70), recipe_frame, border_radius=12)
                                    draw.rect(ecr, cat_color, recipe_frame, 1, border_radius=12)
                                    
                                    # Effet de brillance en haut
                                    recipe_highlight = Rect(recipe_frame.x + 3, recipe_frame.y + 3, 
                                                           recipe_frame.width - 6, 6)
                                    draw.rect(ecr, (70, 70, 90), recipe_highlight, border_radius=3)
                                    
                                    # Image au centre
                                    img_rect = recipe_img.get_rect(center=recipe_frame.center)
                                    ecr.blit(recipe_img, img_rect)
                                    
                                    # Nom en dessous
                                    name = creation_data["Nom"]
                                    if len(name) > 10:
                                        name = name[:8] + "..."
                                    
                                    name_text = small_font.render(name, True, color_scheme["text"])
                                    name_rect = name_text.get_rect(midtop=(recipe_frame.centerx, recipe_frame.bottom + 5))
                                    ecr.blit(name_text, name_rect)
                                    
                                except Exception as e:
                                    # En cas d'erreur, afficher un rectangle simple
                                    draw.rect(ecr, (80, 50, 50), recipe_frame)
                            else:
                                # Élément non découvert: montrer un cadenas
                                draw.rect(ecr, (40, 40, 55), recipe_frame, border_radius=12)
                                
                                # Afficher le cadenas
                                lock_small = transform.scale(icons["lock"], (30, 30))
                                lock_rect = lock_small.get_rect(center=recipe_frame.center)
                                ecr.blit(lock_small, lock_rect)
                                
                                # Texte "???"
                                unknown_text = small_font.render("???", True, color_scheme["text_dim"])
                                unknown_rect = unknown_text.get_rect(midtop=(recipe_frame.centerx, recipe_frame.bottom + 5))
                                ecr.blit(unknown_text, unknown_rect)
                else:
                    # Message si aucune création possible
                    no_recipe_text = description_font.render("Aucune combinaison connue", True, color_scheme["text_dim"])
                    ecr.blit(no_recipe_text, (info_area.x + 20, title_y))
                    
                    # Suggestion
                    tip_text = small_font.render("Essayez de combiner cet élément avec d'autres!", True, color_scheme["text_dim"])
                    ecr.blit(tip_text, (info_area.x + 20, title_y + 30))
                
            except Exception as e:
                # En cas d'erreur, afficher un message simple
                error_text = description_font.render("Erreur d'affichage des détails", True, color_scheme["text"])
                ecr.blit(error_text, (info_area.x + 20, info_area.centery))
        
        # Dessiner le bouton de fermeture
        close_button["rect"].x = menu_x + menu_largeur - 40
        close_button["rect"].y = 20 + float_offset
        close_button["hover"] = close_button["rect"].collidepoint(mouse_pos)
        
        # Ombre du bouton de fermeture
        if close_button["hover"]:
            shadow_close = Rect(close_button["rect"].x + 2, close_button["rect"].y + 2, 
                              close_button["rect"].width, close_button["rect"].height)
            draw.rect(ecr, (0, 0, 0, 50), shadow_close, border_radius=15)
            draw.rect(ecr, color_scheme["button_hover"], close_button["rect"], border_radius=15)
        
        # Dessiner l'icône X
        ecr.blit(icons["close"], (close_button["rect"].x + 2, close_button["rect"].y + 2))
        
        # Afficher conseils clavier
        keyboard_tip = small_font.render("Échap: fermer", True, color_scheme["text_dim"])
        keyboard_rect = keyboard_tip.get_rect(midbottom=(menu_x + menu_largeur//2, htr - 15 + float_offset))
        ecr.blit(keyboard_tip, keyboard_rect)
        
        # Mise à jour de l'écran
        display.flip()
        
        # Traitement des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
                
            # Gestion du bouton Échap pour fermer
            elif evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    if ouvert:
                        ouvert = False
                    else:
                        menu_actif = False
            
            # Gestion de la molette pour le scroll
            elif evt.type == MOUSEBUTTONDOWN:
                if evt.button == 4:  # Molette vers le haut
                    scroll_target = max(0, scroll_target - 1)
                elif evt.button == 5:  # Molette vers le bas
                    scroll_target = min(max_scroll, scroll_target + 1)
                
                # Gestion du clic gauche
                elif evt.button == 1:
                    # Vérifier si le clic est sur un élément
                    if hover_element is not None:
                        selected_element = hover_element
                    
                    # Vérifier si le clic est sur le bouton de fermeture
                    if close_button["rect"].collidepoint(evt.pos):
                        if ouvert:
                            ouvert = False
                        else:
                            menu_actif = False
                    
                    # Gestion du clic sur la scrollbar
                    if total_rows > max_visible_rows:
                        scrollbar_area = Rect(scrollbar_x, scrollbar_y + float_offset, scrollbar_width, scrollbar_height)
                        if scrollbar_area.collidepoint(evt.pos):
                            scrollbar_active = True
                            # Déplacer directement la scrollbar à la position du clic
                            y_rel = evt.pos[1] - scrollbar_y - float_offset
                            scroll_ratio = y_rel / scrollbar_height
                            scroll_target = min(max_scroll, max(0, scroll_ratio * max_scroll))
                
            # Gestion du relâchement du bouton de la souris
            elif evt.type == MOUSEBUTTONUP:
                if evt.button == 1:
                    scrollbar_active = False
            
            # Gestion du déplacement de la scrollbar
            elif evt.type == MOUSEMOTION and scrollbar_active:
                # Calculer la nouvelle position du scroll
                y_rel = evt.pos[1] - scrollbar_y - float_offset
                scroll_ratio = y_rel / scrollbar_height
                scroll_target = min(max_scroll, max(0, scroll_ratio * max_scroll))
    
    return True