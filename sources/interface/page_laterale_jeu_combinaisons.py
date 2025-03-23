#Projet : Elescape
#Auteurs : Mathis MENNESSIER ; Julien MONGENET ; Simon BILLE

from pygame import *
from shared.components.config import *
from shared.components.color_config import *
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
    
    # Position du bouton d'encyclopédie
    button_pos_y = btn_ency["rect"].centery
    
    # Tailles optimisées pour les éléments
    grid_cols = 4
    element_size = 80  # Taille fixe des éléments
    element_width = element_size
    element_height = element_size
    grid_spacing = 15  # Espacement entre les éléments
    
    # Calcul du nombre de lignes nécessaires
    total_items = len(all_elements)
    grid_rows = (total_items + grid_cols - 1) // grid_cols
    visible_rows = min(grid_rows, 4)  # Au maximum 4 lignes visibles à la fois
    
    # Calcul de la largeur et hauteur nécessaires pour la grille
    grid_width = (grid_cols * element_width) + ((grid_cols - 1) * grid_spacing) + 30  # +30 pour les marges
    grid_height = (visible_rows * element_height) + ((visible_rows - 1) * grid_spacing) + 30  # +30 pour les marges
    
    # Dimensions et position du menu - ajusté pour être plus compact
    menu_largeur = grid_width + 20  # Juste assez large pour la grille
    menu_marge_droite = 10  
    menu_y = button_pos_y - 250  # Position verticale alignée avec le bouton
    menu_hauteur = grid_height + 105  # Hauteur = grille + espace pour titre
    menu_x = lrg
    
    # Si le nombre d'éléments est faible, réduire encore la hauteur
    if grid_rows <= 2:
        menu_hauteur = grid_height + 80
    
    # Ajuster la position Y si trop haute ou trop basse
    if menu_y < 10:
        menu_y = 10
    if menu_y + menu_hauteur > htr - 10:
        menu_y = max(10, htr - menu_hauteur - 10)
    
    # Taille de la section description (sous le rectangle principal)
    description_height = 130  # Taille fixe pour la description
    
    vitesse = 20
    menu_actif = True
    ouvert = True
    
    # Position de la grille (centrée dans le menu)
    grid_padding = (menu_largeur - grid_width) // 2 + 15  # Centrage horizontal
    grid_x = menu_x + grid_padding
    grid_y = menu_y + 100  # Position Y après le titre (plus d'espace)
    
    # Chargement des icônes et ressources
    icons = {}
    
    # Icône de fermeture (X)
    close_icon = Surface((25, 25), SRCALPHA)
    draw.line(close_icon, GRIS_CLAIR, (5, 5), (20, 20), 2)
    draw.line(close_icon, GRIS_CLAIR, (5, 20), (20, 5), 2)
    icons["close"] = close_icon
    
    # Cache pour les images des éléments
    image_cache = {}
    
    # Paramètres pour le scroll
    scroll_offset = 0
    scroll_target = 0
    scroll_animation_speed = 0.2
    max_visible_rows = visible_rows
    total_rows = grid_rows
    
    # Paramètres pour la scrollbar
    scrollbar_width = 8
    scrollbar_padding = 5
    scrollbar_x = menu_x + menu_largeur - scrollbar_width - scrollbar_padding
    scrollbar_y = grid_y
    scrollbar_height = grid_height - 30
    scrollbar_active = False
    
    # Paramètres pour l'élément sélectionné
    selected_element = None
    
    # Polices pour le texte
    title_font = font.Font(None, 42)
    subtitle_font = font.Font(None, 32)
    element_font = font.Font(None, 20)
    description_font = font.Font(None, 24)
    small_font = font.Font(None, 18)
    stats_font = font.Font(None, 22)
    
    # Horloge pour le framerate
    clock = time.Clock()
    
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
        except:
            element_categories[elem_id] = 1  # Catégorie par défaut
    
    # Bouton de fermeture
    close_button = {
        "rect": Rect(menu_x + menu_largeur - 40, menu_y + 20, 30, 30),
        "hover": False
    }
    
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
    
    # Fonction sécurisée pour charger une image (avec gestion des erreurs)
    def safe_load_image(path, default_size=(50, 50)):
        try:
            if not path:
                raise ValueError("Chemin d'image vide")
                
            if ',' in path:
                paths = path.split(',')
                path = paths[0].strip().strip('"')
            
            img = image.load(path)
            return img
        except:
            # En cas d'erreur, créer une surface grise
            fallback = Surface(default_size, SRCALPHA)
            fallback.fill((80, 80, 90, 180))
            return fallback
    
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
        
        # Afficher d'abord l'écran de jeu
        ecr.blit(game_screen, (0, 0))
        
        # Animation d'ouverture/fermeture du menu
        target_x = lrg - menu_largeur - menu_marge_droite if ouvert else lrg
        
        if abs(menu_x - target_x) > 1:
            menu_x += (target_x - menu_x) * 0.2
            menu_animation = abs((menu_x - lrg) / (lrg - (lrg - menu_largeur - menu_marge_droite)))
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
            overlay_alpha = int(150 * min(1.0, max(0.0, menu_animation)))
            overlay.fill((0, 0, 0, overlay_alpha))
            ecr.blit(overlay, (0, 0))
        except:
            # En cas d'erreur, utiliser une approche plus simple
            dark_overlay = Surface((lrg, htr))
            dark_overlay.fill(NOIR)
            dark_overlay.set_alpha(120)
            ecr.blit(dark_overlay, (0, 0))
        
        # Dessin du panneau latéral avec coins très arrondis
        panel_surface = Surface((menu_largeur, menu_hauteur), SRCALPHA)
        panel_surface.fill(ENCYC_PANEL_BG)
        
        # Appliquer un masque avec des coins très arrondis au panneau
        try:
            mask = Surface((menu_largeur, menu_hauteur), SRCALPHA)
            mask.fill((0, 0, 0, 0))
            radius = 20  # Rayon des coins arrondis
            
            # Dessiner un rectangle avec des coins très arrondis
            draw.rect(mask, (255, 255, 255, 255), Rect(0, 0, menu_largeur, menu_hauteur), border_radius=radius)
            
            # Appliquer le masque
            panel_surface.blit(mask, (0, 0), special_flags=BLEND_RGBA_MULT)
        except:
            pass
        
        # Dessiner le panneau principal (STATIQUE)
        ecr.blit(panel_surface, (menu_x, menu_y))
        
        # Dessiner une bordure avec des coins arrondis
        try:
            draw.rect(ecr, ENCYC_PANEL_BORDER, 
                    Rect(menu_x, menu_y, menu_largeur, menu_hauteur), 
                    2, border_radius=20)
        except:
            pass
        
        # Dessin du titre
        try:
            titre = title_font.render("Encyclopédie", True, TEXTE)
            titre_rect = titre.get_rect(center=(menu_x + menu_largeur//2, menu_y + 35))
            ecr.blit(titre, titre_rect)
        except:
            pass
        
        # Afficher le compteur d'éléments découverts
        try:
            counter_text = f"{count_discovered}/{count_total} éléments découverts ({int(completion_percentage)}%)"
            counter_surface = stats_font.render(counter_text, True, TEXTE_INTERACTIF)
            counter_rect = counter_surface.get_rect(center=(menu_x + menu_largeur//2, menu_y + 65))
            ecr.blit(counter_surface, counter_rect)
        except:
            pass
        
        # Calculer le rectangle pour la grille d'éléments
        grid_width_actual = (grid_cols * element_width) + ((grid_cols - 1) * grid_spacing)
        grid_area = Rect(grid_x - 10, grid_y - 10, 
                        grid_width_actual + 20, 
                        grid_height)
        
        # Rectangle principal avec coins plus arrondis
        draw.rect(ecr, ENCYC_GRID_BG, grid_area, border_radius=15)
        
        # Bordure plus fine et élégante
        draw.rect(ecr, ENCYC_PANEL_BORDER, grid_area, 1, border_radius=15)
        
        # Calculer le nombre total de lignes nécessaires
        total_rows = (len(all_elements) + grid_cols - 1) // grid_cols
        max_scroll = max(0, total_rows - max_visible_rows)
        
        # Limiter la position de défilement
        scroll_target = max(0, min(scroll_target, max_scroll))
        
        # Dessiner les éléments visibles
        hover_element = None
        
        # Paramètres pour déterminer quels éléments sont visibles
        start_row = int(scroll_offset)
        end_row = min(total_rows, start_row + max_visible_rows + 1)
        
        # Définir la zone de clippage pour les éléments
        ecr.set_clip(grid_area)
        
        # Dessiner les éléments
        element_items = sorted(all_elements.items(), key=lambda x: int(x[0]))
        
        # Recalculer la dernière ligne pour centrage
        total_items = len(element_items)
        if total_items > 0:
            remaining_items_last_row = total_items % grid_cols
            if remaining_items_last_row == 0:
                remaining_items_last_row = grid_cols
            
            if remaining_items_last_row < grid_cols:
                # Ajuster la position X pour centrer les éléments de la dernière ligne
                last_row_width = remaining_items_last_row * element_width + (remaining_items_last_row - 1) * grid_spacing
                last_row_offset = (grid_width_actual - last_row_width) / 2
            else:
                last_row_offset = 0
        else:
            last_row_offset = 0
        
        for i, (elem_id, elem_data) in enumerate(element_items):
            row = i // grid_cols
            col = i % grid_cols
            
            # Ne dessiner que les éléments dans les lignes visibles
            if start_row <= row < end_row:
                # Position de l'élément avec scroll
                # Centrer les éléments si c'est la dernière ligne et qu'elle n'est pas complète
                if row == total_rows - 1 and col < remaining_items_last_row and remaining_items_last_row < grid_cols:
                    # Dernière ligne, centrer les éléments
                    elem_x = grid_x + last_row_offset + col * (element_width + grid_spacing)
                else:
                    # Lignes normales, distribuer régulièrement
                    elem_x = grid_x + col * (element_width + grid_spacing)
                
                elem_y = grid_y + (row - scroll_offset) * (element_height + grid_spacing)
                
                # Créer un rect pour l'élément
                elem_rect = Rect(elem_x, elem_y, element_width, element_height)
                
                # Vérifier si la souris survole cet élément
                is_hover = elem_rect.collidepoint(mouse_pos)
                if is_hover and grid_area.collidepoint(mouse_pos):
                    hover_element = elem_id
                
                # Vérifier si c'est l'élément sélectionné
                is_selected = selected_element == elem_id
                
                # Couleur de fond en fonction de l'état
                if is_selected:
                    bg_color = ENCYC_ITEM_SELECTED
                    border_color = INDICATEUR_NOUVEAU
                elif is_hover:
                    bg_color = ENCYC_ITEM_HOVER
                    border_color = PARAM_PANEL_BORDER
                else:
                    bg_color = ENCYC_GRID_BG
                    border_color = ENCYC_PANEL_BORDER
                
                # Appliquer une couleur subtile selon la catégorie
                try:
                    category = get_element_category(elem_id)
                    if category == 1:
                        cat_color = ENCYC_CATEGORY_BASE
                    elif category == 2:
                        cat_color = ENCYC_CATEGORY_PLANT
                    elif category == 3:
                        cat_color = ENCYC_CATEGORY_ANIMAL
                    elif category == 4:
                        cat_color = ENCYC_CATEGORY_TOOL
                    else:
                        cat_color = bg_color
                        
                    # Mélanger la couleur de catégorie avec la couleur de fond
                    bg_color = (
                        int(bg_color[0] * 0.8 + cat_color[0] * 0.2),
                        int(bg_color[1] * 0.8 + cat_color[1] * 0.2),
                        int(bg_color[2] * 0.8 + cat_color[2] * 0.2)
                    )
                except:
                    pass
                
                # Dessiner le fond de l'élément avec des coins bien arrondis
                try:
                    draw.rect(ecr, bg_color, elem_rect, border_radius=15)
                    draw.rect(ecr, border_color, elem_rect, 2, border_radius=15)
                except:
                    # En cas d'erreur, utiliser un rectangle simple
                    draw.rect(ecr, bg_color, elem_rect)
                    draw.rect(ecr, border_color, elem_rect, 2)
                
                # Vérifier si l'élément est découvert
                is_discovered = int(elem_id) in discovered_elements
                
                # Si l'élément est découvert, afficher son image et son nom
                if is_discovered:
                    try:
                        # Charger l'image de manière sécurisée
                        if elem_id in image_cache:
                            elem_img = image_cache[elem_id]
                        else:
                            img_path = elem_data["Image"]
                            elem_img = safe_load_image(img_path, (element_width - 20, element_height - 20))
                            
                            # Calculer les dimensions pour préserver le ratio
                            img_w, img_h = elem_img.get_size()
                            max_dim = min(elem_rect.width, elem_rect.height) - 25
                            scale_factor = min(max_dim / max(img_w, 1), max_dim / max(img_h, 1))
                            new_w, new_h = int(img_w * scale_factor), int(img_h * scale_factor)
                            
                            # Éviter les dimensions trop petites
                            new_w = max(new_w, 10)
                            new_h = max(new_h, 10)
                            
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
                            
                        name_text = element_font.render(name, True, TEXTE)
                        name_rect = name_text.get_rect(midbottom=(elem_rect.centerx, elem_rect.bottom - 5))
                        ecr.blit(name_text, name_rect)
                        
                    except:
                        # Afficher un placeholder simple et propre en cas d'erreur
                        gray_rect = Rect(elem_rect.x + 10, elem_rect.y + 10, 
                                       elem_rect.width - 20, elem_rect.height - 25)
                        draw.rect(ecr, GRIS_FONCE, gray_rect, border_radius=10)
                        
                        name = elem_data.get("Nom", "???")
                        name_text = element_font.render(name, True, TEXTE)
                        name_rect = name_text.get_rect(midbottom=(elem_rect.centerx, elem_rect.bottom - 5))
                        ecr.blit(name_text, name_rect)
                
                # Sinon, afficher une ombre grise propre
                else:
                    # Rectangle gris foncé avec coins arrondis
                    gray_rect = Rect(elem_rect.x + 10, elem_rect.y + 10, 
                                    elem_rect.width - 20, elem_rect.height - 20)
                    draw.rect(ecr, FOND, gray_rect, border_radius=10)
                    
                    # Texte "???" 
                    unknown_text = element_font.render("???", True, GRIS_CLAIR)
                    unknown_rect = unknown_text.get_rect(midbottom=(elem_rect.centerx, elem_rect.bottom - 5))
                    ecr.blit(unknown_text, unknown_rect)
        
        # Si la liste est vide
        if not all_elements:
            no_result_text = description_font.render("Aucun élément trouvé", True, TEXTE_INTERACTIF)
            no_result_rect = no_result_text.get_rect(center=(grid_area.centerx, grid_area.centery))
            ecr.blit(no_result_text, no_result_rect)
        
        # Réinitialiser la zone de clippage
        ecr.set_clip(None)
        
        # Dessiner la scrollbar si nécessaire
        if total_rows > max_visible_rows:
            # Fond de la scrollbar
            scrollbar_bg = Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
            draw.rect(ecr, VOLUME_BAR_BG, scrollbar_bg, border_radius=4)
            
            # Poignée (thumb) de la scrollbar
            thumb_height = max(30, scrollbar_height * (max_visible_rows / total_rows))
            thumb_position = scrollbar_y + (scroll_offset / max_scroll) * (scrollbar_height - thumb_height)
            
            thumb_rect = Rect(scrollbar_x, thumb_position, scrollbar_width, thumb_height)
            draw.rect(ecr, VOLUME_HANDLE, thumb_rect, border_radius=4)
            draw.rect(ecr, VOLUME_BAR_BORDER, thumb_rect, 1, border_radius=4)
            
            # Surbrillance si la souris est sur la scrollbar
            if thumb_rect.collidepoint(mouse_pos) or scrollbar_active:
                draw.rect(ecr, INDICATEUR_NOUVEAU, thumb_rect, 2, border_radius=4)
        
        # ===== SECTION D'INFORMATION DÉTAILLÉE - EN DESSOUS DU RECTANGLE PRINCIPAL =====
        if selected_element is not None and int(selected_element) in discovered_elements:
            try:
                # Zone d'information SOUS le panneau principal, pas dedans
                info_panel_height = description_height
                info_margin = 10
                info_area = Rect(
                    menu_x, 
                    menu_y + menu_hauteur + 10,  # Juste en-dessous du panneau principal
                    menu_largeur, 
                    info_panel_height
                )
                
                # Rectangle principal avec coins plus arrondis
                draw.rect(ecr, ENCYC_GRID_BG, info_area, border_radius=15)
                
                # Bordure plus subtile
                draw.rect(ecr, ENCYC_PANEL_BORDER, info_area, 1, border_radius=15)
                
                # Afficher les détails de l'élément sélectionné
                elem_data = all_elements[selected_element]
                
                # Titre (nom de l'élément) au centre en haut
                name_text = elem_data["Nom"]
                name_font = font.Font(None, 36)
                name_surface = name_font.render(name_text, True, TEXTE)
                name_rect = name_surface.get_rect(midtop=(info_area.centerx, info_area.y + 15))
                ecr.blit(name_surface, name_rect)
                
                # Image à gauche
                try:
                    # Charger l'image de manière sécurisée
                    info_img_size = min(info_area.height - 40, 80)
                    
                    if selected_element in image_cache:
                        detail_img = image_cache[selected_element]
                    else:
                        img_path = elem_data["Image"]
                        detail_img = safe_load_image(img_path, (info_img_size, info_img_size))
                        
                        # Redimensionner pour l'affichage dans les détails
                        img_w, img_h = detail_img.get_size()
                        max_dim = info_img_size
                        scale_factor = min(max_dim / max(img_w, 1), max_dim / max(img_h, 1))
                        new_w, new_h = int(img_w * scale_factor), int(img_h * scale_factor)
                        
                        # Éviter les dimensions trop petites
                        new_w = max(new_w, 10)
                        new_h = max(new_h, 10)
                        
                        detail_img = transform.scale(detail_img, (new_w, new_h))
                    
                    img_rect = detail_img.get_rect()
                    img_rect.topleft = (info_area.x + 20, info_area.y + 50)
                    ecr.blit(detail_img, img_rect)
                    
                    # Informations de l'élément
                    # Catégorie
                    category = get_element_category(int(selected_element))
                    cat_names = ["Base", "Plantes", "Animaux", "Outils"]
                    cat_name = cat_names[category-1] if category-1 < len(cat_names) else "Autre"
                    
                    # Déterminer la couleur de catégorie
                    if category == 1:
                        cat_color = ENCYC_CATEGORY_BASE
                    elif category == 2:
                        cat_color = ENCYC_CATEGORY_PLANT
                    elif category == 3:
                        cat_color = ENCYC_CATEGORY_ANIMAL
                    elif category == 4:
                        cat_color = ENCYC_CATEGORY_TOOL
                    else:
                        cat_color = GRIS
                    
                    cat_text = stats_font.render(f"Catégorie: {cat_name}", True, cat_color)
                    cat_rect = cat_text.get_rect(topleft=(img_rect.right + 30, info_area.y + 50))
                    ecr.blit(cat_text, cat_rect)
                    
                    # Consommation
                    dr_text = "Se consomme: " + ("Oui" if elem_data["DR"] == 0 else "Non")
                    dr_color = GRIS if elem_data["DR"] == 0 else GRIS_CLAIR
                    dr_surface = description_font.render(dr_text, True, dr_color)
                    dr_rect = dr_surface.get_rect(topleft=(img_rect.right + 30, info_area.y + 75))
                    ecr.blit(dr_surface, dr_rect)
                    
                    # Nombre de combinaisons
                    creation_count = len(elem_data["Creations"]) if elem_data["Creations"] else 0
                    creation_text = f"Combinaisons: {creation_count}"
                    creation_surface = description_font.render(creation_text, True, TEXTE)
                    creation_rect = creation_surface.get_rect(topleft=(img_rect.right + 30, info_area.y + 100))
                    ecr.blit(creation_surface, creation_rect)
                    
                except:
                    # En cas d'erreur, afficher juste le nom
                    try:
                        text_center = description_font.render("Informations non disponibles", True, TEXTE_INTERACTIF)
                        text_rect = text_center.get_rect(center=(info_area.centerx, info_area.centery))
                        ecr.blit(text_center, text_rect)
                    except:
                        pass
            except:
                pass
        
        # Dessiner le bouton de fermeture
        close_button["rect"].x = menu_x + menu_largeur - 40
        close_button["rect"].y = menu_y + 20
        close_button["hover"] = close_button["rect"].collidepoint(mouse_pos)
        
        # Ombre du bouton de fermeture
        if close_button["hover"]:
            draw.rect(ecr, PARAM_BUTTON_HOVER, close_button["rect"], border_radius=15)
        
        # Dessiner l'icône X
        ecr.blit(icons["close"], (close_button["rect"].x + 2, close_button["rect"].y + 2))
        
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
                        scrollbar_area = Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
                        if scrollbar_area.collidepoint(evt.pos):
                            scrollbar_active = True
                            # Déplacer directement la scrollbar à la position du clic
                            y_rel = evt.pos[1] - scrollbar_y
                            scroll_ratio = y_rel / scrollbar_height
                            scroll_target = min(max_scroll, max(0, scroll_ratio * max_scroll))
                
            # Gestion du relâchement du bouton de la souris
            elif evt.type == MOUSEBUTTONUP:
                if evt.button == 1:
                    scrollbar_active = False
            
            # Gestion du déplacement de la scrollbar
            elif evt.type == MOUSEMOTION and scrollbar_active:
                # Calculer la nouvelle position du scroll
                y_rel = evt.pos[1] - scrollbar_y
                scroll_ratio = y_rel / scrollbar_height
                scroll_target = min(max_scroll, max(0, scroll_ratio * max_scroll))
    
    return True