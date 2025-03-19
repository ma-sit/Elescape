from pygame import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from shared.components.color_config import *
from shared.utils.user_account_manager import (
    initialize_system, 
    get_all_users, 
    create_user, 
    set_current_user, 
    get_current_user
)

def afficher_login():
    """
    Affiche l'écran de connexion/création de compte.
    Retourne True si l'utilisateur se connecte avec succès, False sinon.
    """
    init()
    clock = time.Clock()
    
    # Initialiser le système de comptes utilisateurs
    initialize_system()
    
    # Récupérer la liste des utilisateurs existants
    users = get_all_users()
    
    # État initial
    mode = "select"  # "select", "create", "input"
    selected_user = None
    new_username = ""
    input_active = False
    error_message = ""
    error_display_time = 0
    
    # Pour la détection du double-clic
    last_click_time = 0
    double_click_threshold = 300  # millisecondes
    
    # Polices
    title_font = font.Font(None, 60)
    button_font = font.Font(None, 40)
    user_font = font.Font(None, 36)
    input_font = font.Font(None, 36)
    error_font = font.Font(None, 28)
    
    # Couleurs
    bg_color = FOND
    title_color = TEXTE
    button_color = MENU_BOUTON
    button_hover_color = MENU_BOUTON_SURVOL
    input_color = (50, 50, 50)
    input_active_color = (70, 70, 70)
    error_color = (255, 50, 50)
    
    # Chargement du fond (si disponible)
    try:
        background = image.load("data/images/bg/image_menu.png").convert()
        background = transform.scale(background, (rec.right, rec.bottom))
    except:
        background = Surface((lrg, htr))
        background.fill(bg_color)
    
    # Dimensions des boutons et zones
    button_width = 300
    button_height = 60
    button_padding = 20
    input_width = 400
    input_height = 50
    user_button_width = 300
    user_button_height = 50
    user_buttons_y_start = 200
    max_visible_users = 6  # Nombre maximum d'utilisateurs visibles sans défilement
    scroll_offset = 0  # Pour le défilement de la liste des utilisateurs
    
    # Créer les rectangles pour les boutons principaux
    login_button = Rect(lrg//2 - button_width//2, htr - 150, button_width, button_height)
    create_button = Rect(lrg//2 - button_width//2, htr - 150 - button_height - button_padding, button_width, button_height)
    back_button = Rect(50, htr - 80, 150, 50)
    
    # Rectangle pour la zone de saisie
    input_rect = Rect(lrg//2 - input_width//2, 250, input_width, input_height)
    
    # Créer les rectangles pour les boutons d'utilisateurs
    user_buttons = []
    for i, username in enumerate(users):
        user_buttons.append({
            "username": username,
            "rect": Rect(lrg//2 - user_button_width//2, user_buttons_y_start + i * (user_button_height + 10), 
                         user_button_width, user_button_height),
            "hover": False
        })
    
    # Boucle principale
    running = True
    while running:
        current_time = time.get_ticks()
        
        # Afficher le fond
        ecr.blit(background, (0, 0))
        
        # Superposition semi-transparente
        overlay = Surface((lrg, htr), SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Noir semi-transparent
        ecr.blit(overlay, (0, 0))
        
        # Afficher le titre
        title = title_font.render("Elescape", True, title_color)
        title_rect = title.get_rect(center=(lrg//2, 100))
        ecr.blit(title, title_rect)
        
        # Logique d'affichage selon le mode
        if mode == "select":
            # Sous-titre
            subtitle = button_font.render("Sélectionnez un utilisateur", True, title_color)
            subtitle_rect = subtitle.get_rect(center=(lrg//2, 160))
            ecr.blit(subtitle, subtitle_rect)
            
            # Afficher les boutons d'utilisateurs avec défilement
            visible_count = min(len(user_buttons), max_visible_users)
            visible_height = visible_count * (user_button_height + 10)
            
            # Zone de la liste (pour le clippage)
            list_area = Rect(lrg//2 - user_button_width//2 - 10, 
                            user_buttons_y_start - 10, 
                            user_button_width + 20, 
                            visible_height + 20)
            
            # Dessiner le fond de la zone de liste
            draw.rect(ecr, (40, 40, 40), list_area, border_radius=10)
            draw.rect(ecr, (60, 60, 60), list_area, 2, border_radius=10)
            
            # Clipper pour n'afficher que les utilisateurs visibles
            ecr.set_clip(list_area)
            
            # Afficher les boutons d'utilisateurs
            no_users = len(user_buttons) == 0
            for i, btn in enumerate(user_buttons):
                # Position Y ajustée avec le défilement
                btn_y = user_buttons_y_start + i * (user_button_height + 10) - int(scroll_offset * (user_button_height + 10))
                btn["rect"].y = btn_y
                
                # Ne dessiner que les boutons visibles
                if list_area.y - user_button_height < btn_y < list_area.y + list_area.height:
                    # Couleur selon survol
                    color = button_hover_color if btn["hover"] else button_color
                    draw.rect(ecr, color, btn["rect"], border_radius=5)
                    draw.rect(ecr, (90, 90, 90), btn["rect"], 2, border_radius=5)
                    
                    # Texte du bouton
                    text = user_font.render(btn["username"], True, TEXTE)
                    text_rect = text.get_rect(center=btn["rect"].center)
                    ecr.blit(text, text_rect)
            
            # Réinitialiser le clippage
            ecr.set_clip(None)
            
            # Message si aucun utilisateur
            if no_users:
                no_users_text = user_font.render("Aucun utilisateur trouvé", True, TEXTE_INTERACTIF)
                no_users_rect = no_users_text.get_rect(center=(lrg//2, user_buttons_y_start + 50))
                ecr.blit(no_users_text, no_users_rect)
            
            # Boutons Connexion et Créer un compte
            create_text = button_font.render("Créer un compte", True, TEXTE)
            create_text_rect = create_text.get_rect(center=create_button.center)
            draw.rect(ecr, button_color, create_button, border_radius=10)
            draw.rect(ecr, (90, 90, 90), create_button, 2, border_radius=10)
            ecr.blit(create_text, create_text_rect)
            
            # Le bouton de connexion est désactivé s'il n'y a pas d'utilisateur sélectionné
            login_color = button_color if selected_user else (100, 100, 100)
            draw.rect(ecr, login_color, login_button, border_radius=10)
            draw.rect(ecr, (90, 90, 90), login_button, 2, border_radius=10)
            login_text = button_font.render("Se connecter", True, TEXTE)
            login_text_rect = login_text.get_rect(center=login_button.center)
            ecr.blit(login_text, login_text_rect)
            
        elif mode == "create":
            # Sous-titre
            subtitle = button_font.render("Créer un compte", True, title_color)
            subtitle_rect = subtitle.get_rect(center=(lrg//2, 160))
            ecr.blit(subtitle, subtitle_rect)
            
            # Zone de saisie
            input_color_current = input_active_color if input_active else input_color
            draw.rect(ecr, input_color_current, input_rect, border_radius=5)
            draw.rect(ecr, (90, 90, 90), input_rect, 2, border_radius=5)
            
            # Texte dans la zone de saisie
            if new_username:
                input_text = input_font.render(new_username, True, TEXTE)
                # Limiter le texte à la largeur de la zone de saisie
                input_surface = Surface((input_rect.width - 20, input_rect.height - 10), SRCALPHA)
                input_surface.blit(input_text, (0, 0))
                ecr.blit(input_surface, (input_rect.x + 10, input_rect.y + 5))
            else:
                placeholder = input_font.render("Entrez votre nom d'utilisateur", True, (150, 150, 150))
                ecr.blit(placeholder, (input_rect.x + 10, input_rect.y + 10))
            
            # Afficher les boutons
            create_text = button_font.render("Créer", True, TEXTE)
            create_text_rect = create_text.get_rect(center=login_button.center)
            draw.rect(ecr, button_color, login_button, border_radius=10)
            draw.rect(ecr, (90, 90, 90), login_button, 2, border_radius=10)
            ecr.blit(create_text, create_text_rect)
            
            # Bouton retour
            back_text = button_font.render("Retour", True, TEXTE)
            back_text_rect = back_text.get_rect(center=back_button.center)
            draw.rect(ecr, button_color, back_button, border_radius=10)
            draw.rect(ecr, (90, 90, 90), back_button, 2, border_radius=10)
            ecr.blit(back_text, back_text_rect)
        
        # Afficher les messages d'erreur si nécessaire
        if error_message and current_time - error_display_time < 5000:  # Afficher pendant 5 secondes
            error_text = error_font.render(error_message, True, error_color)
            error_rect = error_text.get_rect(center=(lrg//2, htr - 200))
            ecr.blit(error_text, error_rect)
        
        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
                
            elif evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    if mode == "create":
                        mode = "select"
                        input_active = False
                        new_username = ""
                    else:
                        return False
                
                elif mode == "create" and input_active:
                    if evt.key == K_RETURN:
                        # Créer le compte si le nom n'est pas vide
                        if new_username.strip():
                            if create_user(new_username.strip()):
                                # Définir comme utilisateur actuel et connecter
                                set_current_user(new_username.strip())
                                return True
                            else:
                                error_message = f"Le nom d'utilisateur '{new_username}' existe déjà."
                                error_display_time = current_time
                        else:
                            error_message = "Le nom d'utilisateur ne peut pas être vide."
                            error_display_time = current_time
                    
                    elif evt.key == K_BACKSPACE:
                        new_username = new_username[:-1]
                    
                    else:
                        # Ajouter le caractère si ce n'est pas un caractère spécial
                        if evt.unicode.isprintable() and len(new_username) < 20:
                            new_username += evt.unicode
            
            elif evt.type == MOUSEBUTTONDOWN:
                mouse_pos = evt.pos
                
                if mode == "select":
                    # Vérifier les clics sur les boutons d'utilisateurs
                    for btn in user_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            selected_user = btn["username"]
                            
                            # Vérifier si c'est un double-clic
                            current_time = time.get_ticks()
                            if evt.button == 1 and current_time - last_click_time < double_click_threshold:
                                if set_current_user(selected_user):
                                    return True
                            
                            last_click_time = current_time
                    
                    # Vérifier le clic sur le bouton de connexion
                    if login_button.collidepoint(mouse_pos) and selected_user:
                        if set_current_user(selected_user):
                            return True
                    
                    # Vérifier le clic sur le bouton de création de compte
                    if create_button.collidepoint(mouse_pos):
                        mode = "create"
                        input_active = True
                    
                    # Gestion du défilement
                    if evt.button == 4:  # Molette vers le haut
                        scroll_offset = max(0, scroll_offset - 0.5)
                    elif evt.button == 5:  # Molette vers le bas
                        max_scroll = max(0, len(user_buttons) - max_visible_users)
                        scroll_offset = min(max_scroll, scroll_offset + 0.5)
                
                elif mode == "create":
                    # Vérifier le clic sur la zone de saisie
                    if input_rect.collidepoint(mouse_pos):
                        input_active = True
                    else:
                        input_active = False
                    
                    # Vérifier le clic sur le bouton de création
                    if login_button.collidepoint(mouse_pos):
                        if new_username.strip():
                            if create_user(new_username.strip()):
                                # Définir comme utilisateur actuel et connecter
                                set_current_user(new_username.strip())
                                return True
                            else:
                                error_message = f"Le nom d'utilisateur '{new_username}' existe déjà."
                                error_display_time = current_time
                        else:
                            error_message = "Le nom d'utilisateur ne peut pas être vide."
                            error_display_time = current_time
                    
                    # Vérifier le clic sur le bouton retour
                    if back_button.collidepoint(mouse_pos):
                        mode = "select"
                        input_active = False
                        new_username = ""
            
            elif evt.type == MOUSEMOTION:
                mouse_pos = evt.pos
                
                # Mettre à jour l'état de survol des boutons d'utilisateurs
                for btn in user_buttons:
                    btn["hover"] = btn["rect"].collidepoint(mouse_pos)
        
        display.flip()
        clock.tick(30)
    
    return False