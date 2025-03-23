#Projet : Elescape
#Auteurs : Mathis MENNESSIER ; Julien MONGENET ; Simon BILLE

from pygame import *
from shared.components.config import *
from shared.components.color_config import *
import json
from interface.menu import bouton

# Variables globales pour stocker les volumes absolus (sans multiplicateur)
global_volume_general = 1.0
global_volume_musique = 1.0
global_volume_sfx = 1.0

# Touches par défaut qui serviront pour la réinitialisation
TOUCHES_DEFAUT = {
    'Déplacement': BUTTON_RIGHT,
    'Action': K_SPACE,
    'Retour': K_ESCAPE,
    'Plein écran': K_f,
    'Paramètres': K_s,
    'Jouer': K_p,
    'Quitter': K_q
}

# Version standard des paramètres (utilisée depuis le menu principal)
def page_parametres():
    """Page des paramètres"""
    # Utilise simplement la version superposée mais sans fond spécifique
    return page_parametres_interne()

# Version superposée des paramètres (utilisée depuis le jeu en pause)
def page_parametres_superpose(background_image=None):
    """Page des paramètres superposée au jeu"""
    return page_parametres_interne(background_image)

def page_parametres_interne(background_image=None):
    """Implémentation commune des paramètres qui peut fonctionner en superposition"""
    global global_volume_general, global_volume_musique, global_volume_sfx
    
    act = True
    volume_general = global_volume_general
    volume_musique = global_volume_musique
    volume_sfx = global_volume_sfx
    clic_souris = False
    barre_active = None
    horloge = time.Clock()
    section_active = "Audio"
    
    # Variables pour le défilement fluide des touches
    scroll_offset = 0.0  # Utiliser un float pour des transitions fluides
    target_scroll_offset = 0.0  # Position cible du défilement
    scroll_speed = 0.0  # Vitesse de défilement pour l'inertie
    max_visible_touches = 5
    scroll_active = False
    scroll_friction = 0.15  # Facteur de friction pour l'effet d'inertie
    
    # Dimensions générales pour garantir la symétrie
    panel_width = 700
    panel_height = 500
    panel_x = (lrg - panel_width) // 2
    panel_y = (htr - panel_height) // 2
    
    # Calculs pour les onglets centrés sous le titre (comme dans l'image)
    section_width = 140
    section_height = 40
    section_spacing = 10
    total_section_width = (3 * section_width) + (2 * section_spacing)
    section_start_x = (lrg - total_section_width) // 2
    section_y = panel_y + 120  # Position Y des onglets sous le titre
    
    # Variables pour les transitions fluides entre les sections
    section_transition = 1.0  # 1.0 = transition complète
    old_section = section_active
    
    # Onglets positionnés comme dans l'image
    section_buttons = [
        {"rect": Rect(section_start_x, section_y, section_width, section_height), "image": None, "a_joue_son": False, "text": "Audio"},
        {"rect": Rect(section_start_x + section_width + section_spacing, section_y, section_width, section_height), "image": None, "a_joue_son": False, "text": "Interface"},
        {"rect": Rect(section_start_x + (2 * (section_width + section_spacing)), section_y, section_width, section_height), "image": None, "a_joue_son": False, "text": "Touches"}
    ]
    
    # Bouton de retour centré en bas comme sur l'image
    retour_width = 150
    retour_button = {"rect": Rect(lrg // 2 - retour_width // 2, panel_y + panel_height - 70, retour_width, section_height), "image": None, "a_joue_son": False, "text": "Retour"}
    
    # Chargement des touches
    try:
        with open("data/touches.json", "r") as f:
            touches = json.load(f)
    except:
        touches = TOUCHES_DEFAUT.copy()
        # Sauvegarde du fichier par défaut
        try:
            with open("data/touches.json", "w") as f:
                json.dump(touches, f)
        except:
            print("Impossible de sauvegarder le fichier touches.json par défaut")
    
    # Dimensions pour les boutons de touches
    touch_width = panel_width - 100  # Largeur selon l'image
    touch_height = 40
    touch_spacing = 50
    
    # Créer une liste des touches pour l'affichage
    touch_buttons = []
    
    # Position Y de base pour les touches (sera ajustée avec le défilement)
    base_touch_y = panel_y + 220
    
    for i, nom in enumerate(touches):
        touch_buttons.append({
            "rect": Rect(panel_x + 50, base_touch_y + i * touch_spacing, touch_width - 40, touch_height),
            "image": None,
            "a_joue_son": False,
            "text": f"{nom}",
            "key": nom,
            "code": touches[nom]
        })
        
    # Appliquer les volumes initiaux
    volume_musique_final = volume_musique * volume_general
    volume_sfx_final = volume_sfx * volume_general
    
    # Mettre à jour tous les sons
    mixer.music.set_volume(volume_musique_final)
    son_clic.set_volume(volume_sfx_final)
    son_survol.set_volume(volume_sfx_final)
    son_clicmenu.set_volume(volume_sfx_final)
    
    # Utiliser l'image de fond fournie ou charger le fond standard
    if background_image is not None:
        fond = background_image
    else:
        try:
            fond = image.load("data/images/image_menu.png").convert()
            fond = transform.scale(fond, (rec.right, rec.bottom))
        except:
            fond = Surface((lrg, htr))
            fond.fill(FOND)  # Fond par défaut

    # Calcul des positions des barres de volume pour symétrie
    bar_width = panel_width - 140
    bar_height = 12
    bar_x = panel_x + 70
    bar_spacing = 60
    bar_start_y = panel_y + 240
    
    # Positions pour les barres de volume
    bar_positions = [
        ("général", bar_start_y),
        ("musique", bar_start_y + bar_spacing),
        ("interface", bar_start_y + 2 * bar_spacing)
    ]
    
    # Configuration de la zone de contenu (panneau principal sous les onglets)
    content_width = panel_width - 100
    content_height = 240
    content_x = panel_x + 50
    content_y = panel_y + 170
    
    # Configuration de la barre de défilement
    scrollbar_width = 20
    scrollbar_height = content_height - 40  # Hauteur de la barre de défilement
    scrollbar_x = content_x + content_width - scrollbar_width - 10
    scrollbar_y = content_y + 20
    
    # Variables pour l'animation des textes
    text_animations = {}  # Stocke les animations de texte en cours

    # Fonction pour le rendu animé du texte
    def animated_text(key, text, x, y, font_obj, color, align="center", alpha=255):
        # Créer une animation pour un nouveau texte
        if key not in text_animations:
            text_animations[key] = {
                "current_text": text,
                "target_text": text,
                "alpha": alpha,
                "target_alpha": alpha
            }
        
        # Si le texte a changé, commencer une nouvelle transition
        anim = text_animations[key]
        if text != anim["target_text"]:
            anim["current_text"] = anim["target_text"]
            anim["target_text"] = text
            anim["alpha"] = 0  # Fade in du nouveau texte
            anim["target_alpha"] = alpha
            
        # Animations de fondu
        if anim["alpha"] < anim["target_alpha"]:
            anim["alpha"] = min(anim["alpha"] + 25, anim["target_alpha"])
        
        # Rendu du texte
        text_surf = font_obj.render(anim["target_text"], True, color)
        text_surf.set_alpha(anim["alpha"])
        
        # Positionnement
        rect = text_surf.get_rect()
        if align == "center":
            rect.center = (x, y)
        elif align == "left":
            rect.midleft = (x, y)
        elif align == "right":
            rect.midright = (x, y)
            
        return text_surf, rect

    # Fonction pour obtenir le nom d'une touche à partir de son code
    def get_key_name(key_code):
        if key_code == BUTTON_RIGHT:
            return "Clic droit"
        elif key_code == BUTTON_LEFT:
            return "Clic gauche"
        elif key_code == BUTTON_MIDDLE:
            return "Clic milieu"
        else:
            try:
                # Gérer le cas où key.name() échoue
                return key.name(key_code).upper()
            except:
                return f"Touche {key_code}"

    # Calcul de la taille du "thumb" (poignée) de la barre de défilement
    def calculate_thumb_height():
        if len(touch_buttons) <= max_visible_touches:
            return scrollbar_height
        return max(30, int(scrollbar_height * (max_visible_touches / len(touch_buttons))))
    
    # Calcul de la position Y du "thumb"
    def calculate_thumb_y():
        if len(touch_buttons) <= max_visible_touches:
            return scrollbar_y
        
        max_offset = len(touch_buttons) - max_visible_touches
        if max_offset <= 0:
            return scrollbar_y
            
        scroll_ratio = scroll_offset / max_offset if max_offset > 0 else 0
        available_space = scrollbar_height - calculate_thumb_height()
        return scrollbar_y + int(scroll_ratio * available_space)

    while act:
        dt = horloge.tick(60) / 1000.0  # Delta time en secondes pour des animations fluides
        
        # Afficher le fond
        ecr.blit(fond, (0, 0))
        
        # Créer une surface semi-transparente pour l'arrière-plan des paramètres
        overlay = Surface((lrg, htr), SRCALPHA)
        overlay.fill((20, 20, 30, 200))  # Couleur sombre semi-transparente
        ecr.blit(overlay, (0, 0))
        
        # Dessiner le panneau principal avec bordure arrondie
        panel = Rect(panel_x, panel_y, panel_width, panel_height)
        draw.rect(ecr, PARAM_PANEL_BG, panel, border_radius=20)  # Fond
        draw.rect(ecr, PARAM_PANEL_BORDER, panel, 2, border_radius=20)  # Bordure
        
        # Titre
        titre_surface = police_titre.render("Paramètres", True, TEXTE)
        titre_rect = titre_surface.get_rect(center=(lrg // 2, panel_y + 60))
        ecr.blit(titre_surface, titre_rect)
        
        # Dessiner les onglets
        for btn in section_buttons:
            # Si c'est l'onglet actif, utiliser le gris, sinon blanc
            if btn["text"] == section_active:
                text_color = GRIS  # Gris pour l'actif
            else:
                text_color = TEXTE  # Blanc pour les inactifs
                
            # Animation du texte
            text_surf, text_rect = animated_text(
                f"tab_{btn['text']}", 
                btn["text"], 
                btn["rect"].centerx, 
                btn["rect"].centery, 
                font.Font(None, 35), 
                text_color
            )
            ecr.blit(text_surf, text_rect)
            
            # Gestion du survol
            if btn["rect"].collidepoint(mouse.get_pos()):
                if not btn["a_joue_son"] and btn["text"] != section_active:
                    son_survol.play()
                    btn["a_joue_son"] = True
            else:
                btn["a_joue_son"] = False
        
        # Mise à jour du défilement avec animation fluide
        if abs(target_scroll_offset - scroll_offset) > 0.01:
            # Animation fluide vers la cible
            scroll_offset += (target_scroll_offset - scroll_offset) * 0.2
        
        # Appliquer l'inertie au défilement
        if not scroll_active and abs(scroll_speed) > 0.01:
            target_scroll_offset += scroll_speed * dt * 60  # Ajuster pour 60 FPS
            scroll_speed *= (1 - scroll_friction)  # Réduire progressivement la vitesse
            
            # Limites de défilement
            max_scroll = max(0, len(touch_buttons) - max_visible_touches)
            if target_scroll_offset < 0:
                target_scroll_offset = 0
                scroll_speed = 0
            elif target_scroll_offset > max_scroll:
                target_scroll_offset = max_scroll
                scroll_speed = 0
        
        # Zone de contenu (panneau rectangulaire bleu foncé)
        content_panel = Rect(content_x, content_y, content_width, content_height)
        draw.rect(ecr, VOLUME_BAR_BG, content_panel, border_radius=15)  # Bleu foncé
        draw.rect(ecr, VOLUME_BAR_BORDER, content_panel, 2, border_radius=15)  # Bordure bleue
        
        # Section Audio
        if section_active == "Audio":
            # Titre de la section
            section_title, title_rect = animated_text(
                "section_title", 
                "Réglages Audio", 
                content_x + content_width // 2, 
                content_y + 25, 
                font.Font(None, 30), 
                TEXTE
            )
            ecr.blit(section_title, title_rect)
            
            # Afficher les textes et barres de volume
            for i, (name, y_pos) in enumerate(bar_positions):
                # Texte du volume
                volume_value = volume_general if i == 0 else (volume_musique if i == 1 else volume_sfx)
                volume_text = f"Volume {name} : {int(volume_value * 100)}%"
                
                # Animation du texte du volume
                vol_text_surf, vol_text_rect = animated_text(
                    f"vol_{i}", 
                    volume_text, 
                    bar_x, 
                    y_pos - 20, 
                    police_options, 
                    TEXTE, 
                    "left"
                )
                ecr.blit(vol_text_surf, vol_text_rect)
                
                # Barre de fond
                bar_bg = Rect(bar_x, y_pos, bar_width, bar_height)
                draw.rect(ecr, BARRE_FOND_BLANC, bar_bg, border_radius=6)  # Fond blanc pour les barres
                
                # Partie remplie de la barre
                if volume_value > 0:
                    bar_fill = Rect(bar_x, y_pos, int(bar_width * volume_value), bar_height)
                    draw.rect(ecr, VOLUME_BAR_FILL, bar_fill, border_radius=6)
                
                # Contour de la barre
                draw.rect(ecr, VOLUME_BAR_BORDER, bar_bg, 1, border_radius=6)
                
                # Poignée de la barre
                if volume_value > 0:
                    handle_x = bar_x + int(bar_width * volume_value)
                    handle_y = y_pos + bar_height // 2
                    handle_radius = 8
                    draw.circle(ecr, VOLUME_HANDLE, (handle_x, handle_y), handle_radius)
                    draw.circle(ecr, VOLUME_BAR_BORDER, (handle_x, handle_y), handle_radius, 1)

        # Section Touches
        elif section_active == "Touches":
            # Titre de la section
            section_title, title_rect = animated_text(
                "section_title", 
                "Configuration des touches", 
                content_x + content_width // 2, 
                content_y + 25, 
                font.Font(None, 28), 
                TEXTE
            )
            ecr.blit(section_title, title_rect)
            
            # Définir la zone de clippage pour les touches
            touch_area = Rect(content_x + 10, content_y + 50, content_width - 30, content_height - 70)
            
            # Dessiner la scrollbar si nécessaire
            if len(touch_buttons) > max_visible_touches:
                # Piste de la scrollbar (fond)
                draw.rect(ecr, BARRE_FOND_BLANC, Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=8)
                
                # Poignée (thumb) de la scrollbar
                thumb_height = calculate_thumb_height()
                thumb_y = calculate_thumb_y()
                thumb_rect = Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
                draw.rect(ecr, VOLUME_HANDLE, thumb_rect, border_radius=8)
                draw.rect(ecr, VOLUME_BAR_BORDER, thumb_rect, 1, border_radius=8)
            
            # Afficher les boutons de touche avec défilement
            ecr.set_clip(touch_area)
            for i, btn in enumerate(touch_buttons):
                # Ne dessiner que les touches visibles et partiellement visibles pour une transition fluide
                visible_index = i - int(scroll_offset)
                if -1 <= visible_index <= max_visible_touches:
                    # Ajuster la position Y en fonction du défilement
                    offset_y = (scroll_offset - int(scroll_offset)) * touch_spacing
                    btn_y = content_y + 60 + visible_index * touch_spacing - offset_y
                    btn["rect"].y = btn_y
                    
                    # Mettre à jour le texte du bouton
                    nom_touche = get_key_name(btn["code"])
                    
                    text_key = f"touch_{btn['key']}"
                    btn["text"] = f"{btn['key']} : {nom_touche}"
                    
                    # Calcul de l'opacité en fonction de la position
                    alpha = 255
                    if btn_y < content_y + 60:  # Apparition par le haut
                        fade_zone = 40
                        alpha = max(0, min(255, int(255 * (btn_y - (content_y + 60 - fade_zone)) / fade_zone)))
                    elif btn_y > content_y + content_height - 70:  # Disparition par le bas
                        fade_zone = 40
                        alpha = max(0, min(255, int(255 * (content_y + content_height - 30 - btn_y) / fade_zone)))
                    
                    # Animation du texte avec fondu
                    text_surf, text_rect = animated_text(
                        text_key, 
                        btn["text"], 
                        btn["rect"].centerx, 
                        btn["rect"].centery, 
                        font.Font(None, 30), 
                        TEXTE, 
                        "center", 
                        alpha
                    )
                    
                    ecr.blit(text_surf, text_rect)
            
            # Réinitialiser la zone de clippage
            ecr.set_clip(None)
            
            # Afficher le message indiquant que les touches seront modifiables prochainement
            message_text = "Les touches pourront être modifiées prochainement"
            message_surf, message_rect = animated_text(
                "future_feature", 
                message_text, 
                content_x + content_width // 2, 
                panel_y + panel_height - 140, 
                font.Font(None, 28), 
                TEXTE_INTERACTIF
            )
            ecr.blit(message_surf, message_rect)

        # Section Interface (vide pour le moment)
        elif section_active == "Interface":
            section_title, title_rect = animated_text(
                "section_title", 
                "Paramètres d'interface", 
                content_x + content_width // 2, 
                content_y + 25, 
                font.Font(None, 30), 
                TEXTE
            )
            ecr.blit(section_title, title_rect)
            
            # Message provisoire
            info_text, info_rect = animated_text(
                "interface_info", 
                "Paramètres d'interface à venir", 
                content_x + content_width // 2, 
                content_y + content_height // 2, 
                font.Font(None, 24), 
                TEXTE_INTERACTIF
            )
            ecr.blit(info_text, info_rect)

        # Bouton de retour
        draw.rect(ecr, PARAM_BUTTON_BG, retour_button["rect"], border_radius=15)
        draw.rect(ecr, PARAM_PANEL_BORDER, retour_button["rect"], 2, border_radius=15)
        retour_text, retour_text_rect = animated_text(
            "retour_btn", 
            retour_button["text"], 
            retour_button["rect"].centerx, 
            retour_button["rect"].centery, 
            font.Font(None, 30), 
            TEXTE
        )
        ecr.blit(retour_text, retour_text_rect)
        
        # Gestion du survol du bouton retour
        if retour_button["rect"].collidepoint(mouse.get_pos()):
            if not retour_button["a_joue_son"]:
                son_survol.play()
                retour_button["a_joue_son"] = True
        else:
            retour_button["a_joue_son"] = False

        for evt in event.get():
            if evt.type == QUIT:
                # Mise à jour des volumes globaux avant de quitter
                global_volume_general = volume_general
                global_volume_musique = volume_musique
                global_volume_sfx = volume_sfx
                return False

            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    # Mise à jour des volumes globaux avant de quitter
                    global_volume_general = volume_general
                    global_volume_musique = volume_musique
                    global_volume_sfx = volume_sfx
                    act = False

            # Gestion de la molette de la souris pour le défilement
            if evt.type == MOUSEBUTTONDOWN and section_active == "Touches":
                if evt.button == 4:  # Molette vers le haut
                    # Défilement plus fluide
                    target_scroll_offset = max(0, target_scroll_offset - 1)
                    scroll_speed = -8  # Impulsion négative pour l'inertie
                elif evt.button == 5:  # Molette vers le bas
                    max_scroll = max(0, len(touch_buttons) - max_visible_touches)
                    target_scroll_offset = min(max_scroll, target_scroll_offset + 1)
                    scroll_speed = 8  # Impulsion positive pour l'inertie

            if evt.type == MOUSEBUTTONDOWN:
                x, y = evt.pos
                
                # Gestion des clics sur les onglets
                for btn in section_buttons:
                    if btn["rect"].collidepoint(x, y):
                        son_clicmenu.play()
                        # Animation de transition entre sections
                        old_section = section_active
                        section_active = btn["text"]
                        section_transition = 0.0
                
                # Gestion de la barre de défilement
                if section_active == "Touches" and len(touch_buttons) > max_visible_touches:
                    scrollbar_rect = Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
                    if scrollbar_rect.collidepoint(x, y):
                        scroll_active = True
                        scroll_speed = 0  # Arrêter l'inertie
                        # Calculer directement la position du défilement
                        track_pos = (y - scrollbar_y) / scrollbar_height
                        target_scroll_offset = track_pos * (len(touch_buttons) - max_visible_touches)
                        target_scroll_offset = max(0, min(len(touch_buttons) - max_visible_touches, target_scroll_offset))
                
                # Gestion des barres de volume
                if section_active == "Audio":
                    if bar_x <= x <= bar_x + bar_width:
                        for i, (name, y_pos) in enumerate(bar_positions):
                            if y_pos - 5 <= y <= y_pos + bar_height + 5:
                                barre_active = i  # 0=general, 1=musique, 2=sfx
                                clic_souris = True
                                # Mettre à jour directement au clic
                                new_volume = max(0.0, min(1.0, (x - bar_x) / bar_width))
                                
                                if i == 0:
                                    volume_general = new_volume
                                elif i == 1:
                                    volume_musique = new_volume
                                else:
                                    volume_sfx = new_volume
                                
                                # Appliquer les changements de volume
                                volume_musique_final = volume_musique * volume_general
                                volume_sfx_final = volume_sfx * volume_general
                                mixer.music.set_volume(volume_musique_final)
                                son_clic.set_volume(volume_sfx_final)
                                son_survol.set_volume(volume_sfx_final)
                                son_clicmenu.set_volume(volume_sfx_final)
                                break
                
                # Gestion du clic sur le bouton de retour
                if retour_button["rect"].collidepoint(x, y):
                    son_clicmenu.play()
                    # Mise à jour des volumes globaux avant de quitter
                    global_volume_general = volume_general
                    global_volume_musique = volume_musique
                    global_volume_sfx = volume_sfx
                    act = False

            # Gestion du défilement de la scrollbar quand on glisse
            if evt.type == MOUSEMOTION and scroll_active:
                prev_offset = target_scroll_offset
                scroll_pos = (evt.pos[1] - scrollbar_y) / scrollbar_height
                target_scroll_offset = scroll_pos * (len(touch_buttons) - max_visible_touches)
                target_scroll_offset = max(0, min(len(touch_buttons) - max_visible_touches, target_scroll_offset))
                
                # Calculer la vitesse pour l'inertie
                scroll_speed = (target_scroll_offset - prev_offset) * 0.5

            if evt.type == MOUSEBUTTONUP:
                clic_souris = False
                barre_active = None
                scroll_active = False

            if evt.type == MOUSEMOTION and clic_souris and section_active == "Audio":
                x = evt.pos[0]
                nouveau_volume = max(0.0, min(1.0, (x - bar_x) / bar_width))
                
                if barre_active == 0:
                    volume_general = nouveau_volume
                elif barre_active == 1:
                    volume_musique = nouveau_volume
                elif barre_active == 2:
                    volume_sfx = nouveau_volume

                volume_musique_final = volume_musique * volume_general
                volume_sfx_final = volume_sfx * volume_general
                
                # Mettre à jour tous les sons avec les nouveaux volumes
                mixer.music.set_volume(volume_musique_final)
                son_clic.set_volume(volume_sfx_final)
                son_survol.set_volume(volume_sfx_final)
                son_clicmenu.set_volume(volume_sfx_final)

        display.flip()
        
    return True

def afficher_texte(texte, x, y, plc, couleur, align="center"):
    surface_texte = plc.render(texte, True, couleur)
    rect_texte = surface_texte.get_rect()
    if align == "center":
        rect_texte.center = (x, y)
    elif align == "right":
        rect_texte.midright = (x, y)
    elif align == "left":
        rect_texte.midleft = (x, y)
    ecr.blit(surface_texte, rect_texte)