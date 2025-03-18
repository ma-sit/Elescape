from pygame import *
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from shared.components.color_config import *
from shared.utils.user_account_manager import (
    get_current_user,
    get_all_users,
    set_current_user,
    load_progression
)
from interface.login import afficher_login

def profil_utilisateur(background_image=None):
    """
    Affiche le profil de l'utilisateur actuel.
    Permet de changer d'utilisateur ou de se déconnecter.
    
    Args:
        background_image: Image d'arrière-plan (optionnel)
        
    Returns:
        True si l'interface doit rester ouverte, False pour quitter
    """
    init
    
    clock = time.Clock()
    
    # Récupérer l'utilisateur courant
    current_user = get_current_user()
    if not current_user:
        # Si aucun utilisateur, afficher l'écran de connexion
        return afficher_login()
    
    # Charger la progression de l'utilisateur
    progression = load_progression(current_user)
    
    # Polices
    title_font = font.Font(None, 60)
    subtitle_font = font.Font(None, 40)
    info_font = font.Font(None, 32)
    button_font = font.Font(None, 36)
    
    # Couleurs
    bg_color = FOND
    title_color = TEXTE
    info_color = TEXTE_INTERACTIF
    button_color = MENU_BOUTON
    button_hover_color = MENU_BOUTON_SURVOL
    
    # Utiliser l'image de fond fournie ou charger le fond standard
    if background_image is not None:
        fond = background_image
    else:
        try:
            fond = image.load("data/images/bg/image_menu.png").convert()
            fond = transform.scale(fond, (rec.right, rec.bottom))
        except:
            fond = Surface((lrg, htr))
            fond.fill(bg_color)
    
    # Dimensions des boutons
    button_width = 250
    button_height = 50
    button_padding = 20
    
    # Créer les rectangles pour les boutons
    change_user_button = Rect(lrg//2 - button_width//2, htr - 200, button_width, button_height)
    logout_button = Rect(lrg//2 - button_width//2, htr - 200 + button_height + button_padding, button_width, button_height)
    back_button = Rect(50, htr - 80, 150, 50)
    
    # Statistiques à afficher
    niveaux_debloques = progression.get("niveaux_debloques", [1])
    elements_decouverts = progression.get("elements_decouverts", [])
    stats = [
        f"Niveau le plus élevé : {max(niveaux_debloques) if niveaux_debloques else 1}",
        f"Éléments découverts : {len(elements_decouverts)}",
        f"Niveaux débloqués : {len(niveaux_debloques)}"
    ]
    
    # Variables pour l'état des boutons
    button_states = {
        "change_user": {"hover": False},
        "logout": {"hover": False},
        "back": {"hover": False}
    }
    
    # Boucle principale
    running = True
    while running:
        # Afficher le fond
        ecr.blit(fond, (0, 0))
        
        # Superposition semi-transparente
        overlay = Surface((lrg, htr), SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Noir semi-transparent
        ecr.blit(overlay, (0, 0))
        
        # Dessiner le panneau principal
        panel_width = 600
        panel_height = 500
        panel_x = (lrg - panel_width) // 2
        panel_y = (htr - panel_height) // 2
        
        panel = Rect(panel_x, panel_y, panel_width, panel_height)
        draw.rect(ecr, PARAM_PANEL_BG, panel, border_radius=20)
        draw.rect(ecr, PARAM_PANEL_BORDER, panel, 2, border_radius=20)
        
        # Titre
        title = title_font.render("Profil Utilisateur", True, title_color)
        title_rect = title.get_rect(center=(lrg//2, panel_y + 60))
        ecr.blit(title, title_rect)
        
        # Nom d'utilisateur
        username_text = subtitle_font.render(f"Connecté en tant que : {current_user}", True, title_color)
        username_rect = username_text.get_rect(center=(lrg//2, panel_y + 120))
        ecr.blit(username_text, username_rect)
        
        # Statistiques
        for i, stat in enumerate(stats):
            stat_text = info_font.render(stat, True, info_color)
            stat_rect = stat_text.get_rect(center=(lrg//2, panel_y + 180 + i * 40))
            ecr.blit(stat_text, stat_rect)
        
        # Boutons
        # Changer d'utilisateur
        change_color = button_hover_color if button_states["change_user"]["hover"] else button_color
        draw.rect(ecr, change_color, change_user_button, border_radius=10)
        draw.rect(ecr, (90, 90, 90), change_user_button, 2, border_radius=10)
        change_text = button_font.render("Changer d'utilisateur", True, TEXTE)
        change_rect = change_text.get_rect(center=change_user_button.center)
        ecr.blit(change_text, change_rect)
        
        # Déconnexion
        logout_color = button_hover_color if button_states["logout"]["hover"] else button_color
        draw.rect(ecr, logout_color, logout_button, border_radius=10)
        draw.rect(ecr, (90, 90, 90), logout_button, 2, border_radius=10)
        logout_text = button_font.render("Déconnexion", True, TEXTE)
        logout_rect = logout_text.get_rect(center=logout_button.center)
        ecr.blit(logout_text, logout_rect)
        
        # Retour
        back_color = button_hover_color if button_states["back"]["hover"] else button_color
        draw.rect(ecr, back_color, back_button, border_radius=10)
        draw.rect(ecr, (90, 90, 90), back_button, 2, border_radius=10)
        back_text = button_font.render("Retour", True, TEXTE)
        back_rect = back_text.get_rect(center=back_button.center)
        ecr.blit(back_text, back_rect)
        
        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
                
            elif evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    running = False
            
            elif evt.type == MOUSEBUTTONDOWN:
                mouse_pos = evt.pos
                
                # Vérifier les clics sur les boutons
                if change_user_button.collidepoint(mouse_pos):
                    # Afficher l'écran de connexion
                    if afficher_login():
                        # Rafraîchir l'affichage avec le nouvel utilisateur
                        current_user = get_current_user()
                        progression = load_progression(current_user)
                        niveaux_debloques = progression.get("niveaux_debloques", [1])
                        elements_decouverts = progression.get("elements_decouverts", [])
                        stats = [
                            f"Niveau le plus élevé : {max(niveaux_debloques) if niveaux_debloques else 1}",
                            f"Éléments découverts : {len(elements_decouverts)}",
                            f"Niveaux débloqués : {len(niveaux_debloques)}"
                        ]
                    else:
                        # Si l'utilisateur a annulé, quitter le jeu
                        return False
                
                elif logout_button.collidepoint(mouse_pos):
                    # Déconnexion et retour à l'écran de connexion
                    with open("data/accounts.json", "r") as f:
                        accounts = json.load(f)
                    if "current_user" in accounts:
                        del accounts["current_user"]
                    with open("data/accounts.json", "w") as f:
                        json.dump(accounts, f)
                    
                    # Afficher l'écran de connexion
                    if not afficher_login():
                        return False
                    # Rafraîchir l'affichage avec le nouvel utilisateur
                    current_user = get_current_user()
                    progression = load_progression(current_user)
                    niveaux_debloques = progression.get("niveaux_debloques", [1])
                    elements_decouverts = progression.get("elements_decouverts", [])
                    stats = [
                        f"Niveau le plus élevé : {max(niveaux_debloques) if niveaux_debloques else 1}",
                        f"Éléments découverts : {len(elements_decouverts)}",
                        f"Niveaux débloqués : {len(niveaux_debloques)}"
                    ]
                
                elif back_button.collidepoint(mouse_pos):
                    running = False
            
            elif evt.type == MOUSEMOTION:
                mouse_pos = evt.pos
                
                # Mettre à jour l'état de survol des boutons
                button_states["change_user"]["hover"] = change_user_button.collidepoint(mouse_pos)
                button_states["logout"]["hover"] = logout_button.collidepoint(mouse_pos)
                button_states["back"]["hover"] = back_button.collidepoint(mouse_pos)
        
        display.flip()
        clock.tick(30)
    
    return True