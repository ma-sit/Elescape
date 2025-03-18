import os
import json
import shutil
from pygame import *
from math import sin
import sys
import uuid

# Assurer le chemin pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from shared.components.color_config import *

# Chemins des fichiers
DATA_DIR = "data"
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")

def load_or_create_profiles():
    """
    Charge les profils existants ou crée un fichier de profils par défaut.
    """
    if not os.path.exists(PROFILES_FILE):
        # Créer le répertoire data si nécessaire
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Créer un profil par défaut avec ID unique
        default_profile_id = str(uuid.uuid4())
            
        profiles = {
            "active_profile": default_profile_id,
            "profiles": [
                {
                    "id": default_profile_id,
                    "name": "Joueur 1",
                    "created_at": time.get_ticks(),
                    "last_used": time.get_ticks(),
                    "progression": {"niveaux_debloques": [1], "elements_decouverts": []}
                }
            ]
        }
        
        with open(PROFILES_FILE, "w") as f:
            json.dump(profiles, f)
        
        return profiles
    
    try:
        with open(PROFILES_FILE, "r") as f:
            profiles = json.load(f)
            return profiles
    except:
        # En cas d'erreur, retourner une structure par défaut
        return {"active_profile": None, "profiles": []}

def save_profiles(profiles):
    """
    Sauvegarde les profils dans le fichier.
    """
    try:
        with open(PROFILES_FILE, "w") as f:
            json.dump(profiles, f)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des profils: {e}")
        return False

def set_active_profile(profile_id):
    """
    Définit le profil actif et met à jour le fichier de profils.
    """
    try:
        # Mettre à jour le fichier de profils
        profiles = load_or_create_profiles()
        profiles["active_profile"] = profile_id
        
        # Mettre à jour la date de dernière utilisation
        for profile in profiles["profiles"]:
            if profile["id"] == profile_id:
                profile["last_used"] = time.get_ticks()
                break
                
        save_profiles(profiles)
        return True
    except Exception as e:
        print(f"Erreur lors de la définition du profil actif: {e}")
        return False

def create_profile(name):
    """
    Crée un nouveau profil avec un ID unique et une progression par défaut.
    """
    # Générer un ID unique
    profile_id = str(uuid.uuid4())
    
    # Créer une progression par défaut
    progression = {"niveaux_debloques": [1], "elements_decouverts": []}
    
    # Mettre à jour les profils
    profiles = load_or_create_profiles()
    profiles["profiles"].append({
        "id": profile_id,
        "name": name,
        "created_at": time.get_ticks(),
        "last_used": time.get_ticks(),
        "progression": progression
    })
    
    save_profiles(profiles)
    return profile_id

def delete_profile(profile_id):
    """
    Supprime un profil.
    """
    # Vérifier si le profil existe
    profiles = load_or_create_profiles()
    
    # Ne pas supprimer le profil s'il est le seul
    if len(profiles["profiles"]) <= 1:
        return False
    
    # Mettre à jour la liste des profils
    profiles["profiles"] = [p for p in profiles["profiles"] if p["id"] != profile_id]
    
    # Si le profil supprimé était le profil actif, en définir un nouveau
    if profiles["active_profile"] == profile_id:
        profiles["active_profile"] = profiles["profiles"][0]["id"]
        set_active_profile(profiles["active_profile"])
    
    save_profiles(profiles)
    return True

def get_active_profile():
    """
    Récupère le profil actif.
    """
    profiles = load_or_create_profiles()
    return profiles.get("active_profile")

def get_profile_progression(profile_id=None):
    """
    Récupère la progression du profil spécifié ou du profil actif.
    """
    profiles = load_or_create_profiles()
    if profile_id is None:
        profile_id = profiles.get("active_profile")
    
    for profile in profiles["profiles"]:
        if profile["id"] == profile_id:
            return profile.get("progression", {"niveaux_debloques": [1], "elements_decouverts": []})
    
    return {"niveaux_debloques": [1], "elements_decouverts": []}

def save_profile_progression(progression, profile_id=None):
    """
    Sauvegarde la progression pour un profil spécifié ou le profil actif.
    """
    profiles = load_or_create_profiles()
    if profile_id is None:
        profile_id = profiles.get("active_profile")
    
    for profile in profiles["profiles"]:
        if profile["id"] == profile_id:
            profile["progression"] = progression
            save_profiles(profiles)
            return True
    
    return False

def selection_profil():
    """
    Affiche l'interface de sélection de profil et permet à l'utilisateur de choisir, 
    créer ou supprimer un profil.
    """
    # Initialisation
    init()
    
    # Charger les profils existants
    profiles = load_or_create_profiles()
    active_profile_id = profiles.get("active_profile")
    
    # Dimensions
    panel_width = 600
    panel_height = 500
    panel_x = (lrg - panel_width) // 2
    panel_y = (htr - panel_height) // 2
    
    # Dimensions pour les boutons de profil
    profile_btn_width = panel_width - 100
    profile_btn_height = 80
    profile_btn_spacing = 20
    
    # Bouton de création de profil
    create_btn = {
        "rect": Rect(panel_x + (panel_width - profile_btn_width) // 2, 
                   panel_y + panel_height - 100, 
                   profile_btn_width, 60),
        "text": "Créer un nouveau profil",
        "hover": False,
        "a_joue_son": False
    }
    
    # Bouton de retour
    back_btn = {
        "rect": Rect(panel_x + 20, panel_y + 20, 40, 40),
        "text": "←",
        "hover": False,
        "a_joue_son": False
    }
    
    # Boucle principale
    running = True
    scroll_offset = 0
    clock = time.Clock()
    max_visible_profiles = 4
    
    # Mode de création de profil
    creating_profile = False
    new_profile_name = "Nouveau joueur"
    cursor_pos = len(new_profile_name)
    cursor_visible = True
    cursor_timer = 0
    blink_rate = 500  # ms
    
    # Mode confirmation de suppression
    deleting_profile = None
    
    # Chargement du fond
    try:
        background = image.load("data/images/bg/image_menu.png").convert()
        background = transform.scale(background, (rec.right, rec.bottom))
    except:
        background = Surface((lrg, htr))
        background.fill(FOND)
    
    while running:
        current_time = time.get_ticks()
        
        # Afficher le fond
        ecr.blit(background, (0, 0))
        
        # Créer une surface semi-transparente pour l'arrière-plan
        overlay = Surface((lrg, htr), SRCALPHA)
        overlay.fill((20, 20, 30, 200))  # Couleur sombre semi-transparente
        ecr.blit(overlay, (0, 0))
        
        # Dessiner le panneau principal
        panel = Rect(panel_x, panel_y, panel_width, panel_height)
        draw.rect(ecr, PARAM_PANEL_BG, panel, border_radius=20)  # Fond
        draw.rect(ecr, PARAM_PANEL_BORDER, panel, 2, border_radius=20)  # Bordure
        
        # Titre
        title_font = font.Font(None, 50)
        title_text = "Sélection du profil" if not creating_profile else "Créer un profil"
        title_surface = title_font.render(title_text, True, TEXTE)
        title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + 50))
        ecr.blit(title_surface, title_rect)
        
        # Dessiner le bouton de retour
        back_btn["hover"] = back_btn["rect"].collidepoint(mouse.get_pos())
        back_color = PARAM_BUTTON_HOVER if back_btn["hover"] else PARAM_BUTTON_BG
        draw.rect(ecr, back_color, back_btn["rect"], border_radius=15)
        draw.rect(ecr, PARAM_PANEL_BORDER, back_btn["rect"], 2, border_radius=15)
        
        back_font = font.Font(None, 40)
        back_text = back_font.render(back_btn["text"], True, TEXTE)
        back_rect = back_text.get_rect(center=back_btn["rect"].center)
        ecr.blit(back_text, back_rect)
        
        if back_btn["hover"] and not back_btn["a_joue_son"]:
            son_survol.play()
            back_btn["a_joue_son"] = True
        elif not back_btn["hover"]:
            back_btn["a_joue_son"] = False
        
        if creating_profile:
            # Interface de création de profil
            input_box = Rect(panel_x + 100, panel_y + 150, panel_width - 200, 60)
            draw.rect(ecr, VOLUME_BAR_BG, input_box, border_radius=10)
            draw.rect(ecr, VOLUME_BAR_BORDER, input_box, 2, border_radius=10)
            
            # Texte d'entrée
            input_font = font.Font(None, 40)
            input_text = input_font.render(new_profile_name, True, TEXTE)
            input_rect = input_text.get_rect(center=(input_box.centerx, input_box.centery))
            ecr.blit(input_text, input_rect)
            
            # Curseur clignotant
            cursor_timer += clock.get_time()
            if cursor_timer >= blink_rate:
                cursor_visible = not cursor_visible
                cursor_timer = 0
                
            if cursor_visible:
                # Calculer la position du curseur
                cursor_offset = input_font.size(new_profile_name[:cursor_pos])[0]
                cursor_x = input_rect.left + cursor_offset
                cursor_y1 = input_box.top + 15
                cursor_y2 = input_box.bottom - 15
                draw.line(ecr, TEXTE, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
            
            # Instructions
            instr_font = font.Font(None, 30)
            instr_text = instr_font.render("Entrez le nom du nouveau profil", True, TEXTE_INTERACTIF)
            instr_rect = instr_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 120))
            ecr.blit(instr_text, instr_rect)
            
            # Boutons Confirmer/Annuler
            confirm_btn = {
                "rect": Rect(panel_x + 100, panel_y + 250, 180, 60),
                "text": "Confirmer",
                "hover": False
            }
            
            cancel_btn = {
                "rect": Rect(panel_x + panel_width - 280, panel_y + 250, 180, 60),
                "text": "Annuler",
                "hover": False
            }
            
            # Dessiner bouton Confirmer
            confirm_btn["hover"] = confirm_btn["rect"].collidepoint(mouse.get_pos())
            confirm_color = MENU_JEU_BUTTON_HOVER if confirm_btn["hover"] else MENU_JEU_BUTTON
            draw.rect(ecr, confirm_color, confirm_btn["rect"], border_radius=15)
            draw.rect(ecr, MENU_JEU_BORDER, confirm_btn["rect"], 2, border_radius=15)
            
            confirm_text = font.Font(None, 35).render(confirm_btn["text"], True, TEXTE)
            confirm_text_rect = confirm_text.get_rect(center=confirm_btn["rect"].center)
            ecr.blit(confirm_text, confirm_text_rect)
            
            # Dessiner bouton Annuler
            cancel_btn["hover"] = cancel_btn["rect"].collidepoint(mouse.get_pos())
            cancel_color = MENU_JEU_BUTTON_HOVER if cancel_btn["hover"] else MENU_JEU_BUTTON
            draw.rect(ecr, cancel_color, cancel_btn["rect"], border_radius=15)
            draw.rect(ecr, MENU_JEU_BORDER, cancel_btn["rect"], 2, border_radius=15)
            
            cancel_text = font.Font(None, 35).render(cancel_btn["text"], True, TEXTE)
            cancel_text_rect = cancel_text.get_rect(center=cancel_btn["rect"].center)
            ecr.blit(cancel_text, cancel_text_rect)
            
        elif deleting_profile is not None:
            # Confirmation de suppression
            profile_to_delete = None
            for profile in profiles["profiles"]:
                if profile["id"] == deleting_profile:
                    profile_to_delete = profile
                    break
            
            if profile_to_delete:
                # Message de confirmation
                confirm_font = font.Font(None, 35)
                confirm_text1 = confirm_font.render(f"Êtes-vous sûr de vouloir supprimer", True, TEXTE)
                confirm_text2 = confirm_font.render(f"le profil '{profile_to_delete['name']}' ?", True, TEXTE)
                
                confirm_rect1 = confirm_text1.get_rect(center=(panel_x + panel_width // 2, panel_y + 150))
                confirm_rect2 = confirm_text2.get_rect(center=(panel_x + panel_width // 2, panel_y + 190))
                
                ecr.blit(confirm_text1, confirm_rect1)
                ecr.blit(confirm_text2, confirm_rect2)
                
                warning_font = font.Font(None, 30)
                warning_text = warning_font.render("Cette action est irréversible !", True, BOUTON_REINIT_FOND)
                warning_rect = warning_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 240))
                ecr.blit(warning_text, warning_rect)
                
                # Boutons Oui/Non
                yes_btn = {
                    "rect": Rect(panel_x + 100, panel_y + 300, 180, 60),
                    "text": "Oui, supprimer",
                    "hover": False
                }
                
                no_btn = {
                    "rect": Rect(panel_x + panel_width - 280, panel_y + 300, 180, 60),
                    "text": "Annuler",
                    "hover": False
                }
                
                # Dessiner bouton Oui
                yes_btn["hover"] = yes_btn["rect"].collidepoint(mouse.get_pos())
                yes_color = BOUTON_OUI_SURVOL if yes_btn["hover"] else BOUTON_OUI_FOND
                draw.rect(ecr, yes_color, yes_btn["rect"], border_radius=15)
                draw.rect(ecr, PARAM_PANEL_BORDER, yes_btn["rect"], 2, border_radius=15)
                
                yes_text = font.Font(None, 35).render(yes_btn["text"], True, TEXTE)
                yes_text_rect = yes_text.get_rect(center=yes_btn["rect"].center)
                ecr.blit(yes_text, yes_text_rect)
                
                # Dessiner bouton Non
                no_btn["hover"] = no_btn["rect"].collidepoint(mouse.get_pos())
                no_color = BOUTON_NON_SURVOL if no_btn["hover"] else BOUTON_NON_FOND
                draw.rect(ecr, no_color, no_btn["rect"], border_radius=15)
                draw.rect(ecr, PARAM_PANEL_BORDER, no_btn["rect"], 2, border_radius=15)
                
                no_text = font.Font(None, 35).render(no_btn["text"], True, TEXTE)
                no_text_rect = no_text.get_rect(center=no_btn["rect"].center)
                ecr.blit(no_text, no_text_rect)
        else:
            # Interface de sélection de profil
            profile_list = profiles.get("profiles", [])
            
            # Zone de contenu pour les profils avec clippage
            content_area = Rect(panel_x + 50, panel_y + 100, panel_width - 100, panel_height - 220)
            draw.rect(ecr, VOLUME_BAR_BG, content_area, border_radius=15)
            draw.rect(ecr, VOLUME_BAR_BORDER, content_area, 2, border_radius=15)
            
            # Limiter le scroll
            max_scroll = max(0, len(profile_list) - max_visible_profiles)
            scroll_offset = max(0, min(scroll_offset, max_scroll))
            
            # Définir la zone de clippage
            ecr.set_clip(content_area)
            
            # Afficher les profils
            profile_y = content_area.y + 20 - int(scroll_offset * (profile_btn_height + profile_btn_spacing))
            
            for i, profile in enumerate(profile_list):
                btn_rect = Rect(
                    panel_x + (panel_width - profile_btn_width) // 2,
                    profile_y + i * (profile_btn_height + profile_btn_spacing),
                    profile_btn_width,
                    profile_btn_height
                )
                
                # Vérifier si le profil est visible dans la zone de contenu
                if btn_rect.bottom < content_area.y or btn_rect.y > content_area.bottom:
                    continue
                
                # Calculer l'état du bouton
                hover = btn_rect.collidepoint(mouse.get_pos())
                is_active = profile["id"] == active_profile_id
                
                # Choisir la couleur en fonction de l'état
                if is_active:
                    # Profil actif avec une couleur plus foncée
                    bg_color = NIVEAU_DEBLOQUE_FOND if not hover else NIVEAU_DEBLOQUE_SURVOL_FOND
                else:
                    bg_color = PARAM_BUTTON_BG if not hover else PARAM_BUTTON_HOVER
                
                # Dessiner le bouton principal
                draw.rect(ecr, bg_color, btn_rect, border_radius=15)
                
                # Ajouter une bordure plus visible pour le profil actif
                if is_active:
                    border_width = 3
                    pulse = 0.7 + 0.3 * sin(current_time / 300)
                    border_color = (
                        int(INDICATEUR_NOUVEAU[0] * pulse),
                        int(INDICATEUR_NOUVEAU[1] * pulse),
                        int(INDICATEUR_NOUVEAU[2] * pulse)
                    )
                else:
                    border_width = 2
                    border_color = PARAM_PANEL_BORDER
                
                draw.rect(ecr, border_color, btn_rect, border_width, border_radius=15)
                
                # Texte du profil
                profile_font = font.Font(None, 35)
                profile_text = profile_font.render(profile["name"], True, TEXTE)
                text_rect = profile_text.get_rect(midleft=(btn_rect.left + 20, btn_rect.centery))
                ecr.blit(profile_text, text_rect)
                
                # Badge "Actif" pour le profil actif
                if is_active:
                    active_font = font.Font(None, 22)
                    active_text = active_font.render("Actif", True, INDICATEUR_NOUVEAU)
                    active_rect = active_text.get_rect(midright=(btn_rect.right - 50, btn_rect.centery))
                    ecr.blit(active_text, active_rect)
                
                # Bouton de suppression
                delete_btn_rect = Rect(btn_rect.right - 40, btn_rect.centery - 15, 30, 30)
                delete_hover = delete_btn_rect.collidepoint(mouse.get_pos())
                
                delete_color = BOUTON_NON_SURVOL if delete_hover else BOUTON_NON_FOND
                draw.rect(ecr, delete_color, delete_btn_rect, border_radius=15)
                
                # Croix de suppression
                cross_size = 12
                cross_x, cross_y = delete_btn_rect.center
                draw.line(ecr, TEXTE, (cross_x - cross_size//2, cross_y - cross_size//2), 
                          (cross_x + cross_size//2, cross_y + cross_size//2), 2)
                draw.line(ecr, TEXTE, (cross_x + cross_size//2, cross_y - cross_size//2), 
                          (cross_x - cross_size//2, cross_y + cross_size//2), 2)
            
            # Réinitialiser la zone de clippage
            ecr.set_clip(None)
            
            # Dessiner la scrollbar si nécessaire
            if len(profile_list) > max_visible_profiles:
                scrollbar_width = 10
                scrollbar_height = content_area.height - 40
                scrollbar_x = content_area.right - scrollbar_width - 10
                scrollbar_y = content_area.y + 20
                
                # Fond de la scrollbar
                draw.rect(ecr, BARRE_FOND_BLANC, Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=5)
                
                # Poignée (thumb) de la scrollbar
                thumb_height = max(30, scrollbar_height * (max_visible_profiles / len(profile_list)))
                thumb_pos = scrollbar_y + (scroll_offset / max_scroll) * (scrollbar_height - thumb_height) if max_scroll > 0 else scrollbar_y
                
                thumb_rect = Rect(scrollbar_x, thumb_pos, scrollbar_width, thumb_height)
                draw.rect(ecr, VOLUME_HANDLE, thumb_rect, border_radius=5)
                draw.rect(ecr, VOLUME_BAR_BORDER, thumb_rect, 1, border_radius=5)
            
            # Bouton de création de profil
            create_btn["hover"] = create_btn["rect"].collidepoint(mouse.get_pos())
            create_color = MENU_JEU_BUTTON_HOVER if create_btn["hover"] else MENU_JEU_BUTTON
            draw.rect(ecr, create_color, create_btn["rect"], border_radius=15)
            draw.rect(ecr, MENU_JEU_BORDER, create_btn["rect"], 2, border_radius=15)
            
            create_text = font.Font(None, 35).render(create_btn["text"], True, TEXTE)
            create_text_rect = create_text.get_rect(center=create_btn["rect"].center)
            ecr.blit(create_text, create_text_rect)
            
            if create_btn["hover"] and not create_btn["a_joue_son"]:
                son_survol.play()
                create_btn["a_joue_son"] = True
            elif not create_btn["hover"]:
                create_btn["a_joue_son"] = False
        
        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
                
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    if creating_profile:
                        creating_profile = False
                    elif deleting_profile is not None:
                        deleting_profile = None
                    else:
                        running = False
                        
                elif creating_profile:
                    if evt.key == K_RETURN:
                        # Créer le profil si le nom n'est pas vide
                        if new_profile_name.strip():
                            profile_id = create_profile(new_profile_name)
                            # Recharger les profils
                            profiles = load_or_create_profiles()
                            creating_profile = False
                    elif evt.key == K_BACKSPACE:
                        if cursor_pos > 0:
                            new_profile_name = new_profile_name[:cursor_pos-1] + new_profile_name[cursor_pos:]
                            cursor_pos -= 1
                    elif evt.key == K_DELETE:
                        if cursor_pos < len(new_profile_name):
                            new_profile_name = new_profile_name[:cursor_pos] + new_profile_name[cursor_pos+1:]
                    elif evt.key == K_LEFT:
                        cursor_pos = max(0, cursor_pos - 1)
                    elif evt.key == K_RIGHT:
                        cursor_pos = min(len(new_profile_name), cursor_pos + 1)
                    elif evt.unicode and ord(evt.unicode) >= 32:
                        # Limiter la longueur du nom
                        if len(new_profile_name) < 20:
                            new_profile_name = new_profile_name[:cursor_pos] + evt.unicode + new_profile_name[cursor_pos:]
                            cursor_pos += 1
                    
                    # Réinitialiser le timer du curseur
                    cursor_timer = 0
                    cursor_visible = True
                    
            elif evt.type == MOUSEBUTTONDOWN:
                if evt.button == 1:
                    # Clic sur le bouton de retour
                    if back_btn["rect"].collidepoint(evt.pos):
                        son_clicmenu.play()
                        if creating_profile:
                            creating_profile = False
                        elif deleting_profile is not None:
                            deleting_profile = None
                        else:
                            running = False
                    
                    # Gestion selon le mode actuel
                    if creating_profile:
                        # Clic sur la zone de saisie
                        if input_box.collidepoint(evt.pos):
                            # Calculer la position du curseur en fonction du clic
                            input_font = font.Font(None, 40)
                            x_rel = evt.pos[0] - input_box.x
                            
                            # Trouver la position la plus proche dans le texte
                            cursor_pos = 0
                            min_diff = float('inf')
                            
                            for i in range(len(new_profile_name) + 1):
                                width = input_font.size(new_profile_name[:i])[0]
                                diff = abs(width - x_rel)
                                
                                if diff < min_diff:
                                    min_diff = diff
                                    cursor_pos = i
                            
                            # Réinitialiser le timer du curseur
                            cursor_timer = 0
                            cursor_visible = True
                            
                        # Clic sur le bouton Confirmer
                        elif confirm_btn["rect"].collidepoint(evt.pos):
                            son_clicmenu.play()
                            # Créer le profil si le nom n'est pas vide
                            if new_profile_name.strip():
                                profile_id = create_profile(new_profile_name)
                                # Recharger les profils
                                profiles = load_or_create_profiles()
                                creating_profile = False
                        
                        # Clic sur le bouton Annuler
                        elif cancel_btn["rect"].collidepoint(evt.pos):
                            son_clicmenu.play()
                            creating_profile = False
                    
                    elif deleting_profile is not None:
                        # Mode de confirmation de suppression
                        if yes_btn["rect"].collidepoint(evt.pos):
                            son_clicmenu.play()
                            if delete_profile(deleting_profile):
                                # Recharger les profils
                                profiles = load_or_create_profiles()
                                active_profile_id = profiles.get("active_profile")
                            deleting_profile = None
                            
                        elif no_btn["rect"].collidepoint(evt.pos):
                            son_clicmenu.play()
                            deleting_profile = None
                    
                    else:
                        # Mode de sélection de profil
                        if create_btn["rect"].collidepoint(evt.pos):
                            son_clicmenu.play()
                            creating_profile = True
                            new_profile_name = "Nouveau joueur"
                            cursor_pos = len(new_profile_name)
                        
                        # Vérification des clics sur les profils
                        profile_list = profiles.get("profiles", [])
                        profile_y = content_area.y + 20 - int(scroll_offset * (profile_btn_height + profile_btn_spacing))
                        
                        for i, profile in enumerate(profile_list):
                            btn_rect = Rect(
                                panel_x + (panel_width - profile_btn_width) // 2,
                                profile_y + i * (profile_btn_height + profile_btn_spacing),
                                profile_btn_width,
                                profile_btn_height
                            )
                            
                            # Ignorer les profils hors de la zone visible
                            if btn_rect.bottom < content_area.y or btn_rect.y > content_area.bottom:
                                continue
                            
                            # Clic sur le bouton de suppression
                            delete_btn_rect = Rect(btn_rect.right - 40, btn_rect.centery - 15, 30, 30)
                            if delete_btn_rect.collidepoint(evt.pos):
                                son_clicmenu.play()
                                # Vérifier s'il s'agit du dernier profil
                                if len(profiles["profiles"]) <= 1:
                                    # Message d'avertissement
                                    warning_font = font.Font(None, 28)
                                    warning_message = "Impossible de supprimer le dernier profil."
                                    warning_message2 = "Veuillez créer un autre profil avant de supprimer celui-ci."
                                    
                                    # Créer une surface pour le message d'avertissement
                                    warning_width, warning_height = 500, 120
                                    warning_bg = Surface((warning_width, warning_height), SRCALPHA)
                                    warning_bg.fill((20, 20, 30, 230))
                                    warning_rect = Rect((lrg - warning_width) // 2, 
                                                    (htr - warning_height) // 2, 
                                                    warning_width, warning_height)
                                    
                                    # Dessiner le fond et la bordure
                                    draw.rect(ecr, (0, 0, 0, 230), warning_rect, border_radius=15)
                                    draw.rect(ecr, PARAM_PANEL_BORDER, warning_rect, 2, border_radius=15)
                                    
                                    # Texte du message
                                    text1 = warning_font.render(warning_message, True, BOUTON_REINIT_FOND)
                                    text2 = warning_font.render(warning_message2, True, BOUTON_REINIT_FOND)
                                    text_rect1 = text1.get_rect(center=(lrg // 2, warning_rect.centery - 20))
                                    text_rect2 = text2.get_rect(center=(lrg // 2, warning_rect.centery + 20))
                                    ecr.blit(text1, text_rect1)
                                    ecr.blit(text2, text_rect2)
                                    
                                    display.flip()
                                    
                                    # Attendre que l'utilisateur clique pour fermer le message
                                    waiting = True
                                    while waiting:
                                        for wait_evt in event.get():
                                            if wait_evt.type == MOUSEBUTTONDOWN or wait_evt.type == KEYDOWN:
                                                waiting = False
                                            if wait_evt.type == QUIT:
                                                return False
                                else:
                                    deleting_profile = profile["id"]
                            
                            # Clic sur le profil (pour l'activer)
                            elif btn_rect.collidepoint(evt.pos) and not delete_btn_rect.collidepoint(evt.pos):
                                son_clicmenu.play()
                                if profile["id"] != active_profile_id:
                                    # Définir ce profil comme actif
                                    set_active_profile(profile["id"])
                                    # Recharger les profils
                                    profiles = load_or_create_profiles()
                                    active_profile_id = profiles.get("active_profile")
                
                elif evt.button == 4:  # Molette vers le haut
                    if not creating_profile and deleting_profile is None:
                        scroll_offset = max(0, scroll_offset - 0.5)
                        
                elif evt.button == 5:  # Molette vers le bas
                    if not creating_profile and deleting_profile is None:
                        profile_list = profiles.get("profiles", [])
                        max_scroll = max(0, len(profile_list) - max_visible_profiles)
                        scroll_offset = min(max_scroll, scroll_offset + 0.5)
            
            elif evt.type == MOUSEMOTION:
                # Gestion du survol pour les sons
                pass
        
        display.flip()
        clock.tick(60)
    
    return True