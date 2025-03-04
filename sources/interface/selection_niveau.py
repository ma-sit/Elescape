from pygame import *
import sys
import os
from math import *
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from shared.components.color_config import *  # Import des couleurs standardisées
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

# Fonction pour charger la progression des niveaux
def charger_progression():
    try:
        with open("data/progression.json", "r") as f:
            return json.load(f)
    except:
        # Si le fichier n'existe pas, créer une progression par défaut
        progression = {"niveaux_debloques": [1]}
        sauvegarder_progression(progression)
        return progression

# Fonction pour sauvegarder la progression
def sauvegarder_progression(progression):
    try:
        with open("data/progression.json", "w") as f:
            json.dump(progression, f)
        return True
    except:
        print("Erreur lors de la sauvegarde de la progression")
        return False

# Fonction pour débloquer le niveau suivant
def debloquer_niveau_suivant(niveau_actuel):
    progression = charger_progression()
    if niveau_actuel + 1 not in progression["niveaux_debloques"]:
        progression["niveaux_debloques"].append(niveau_actuel + 1)
        sauvegarder_progression(progression)
        return True
    return False

# Fonction pour réinitialiser la progression
def reinitialiser_progression():
    progression = {"niveaux_debloques": [1]}
    return sauvegarder_progression(progression)

# Fonction pour afficher une boîte de dialogue de confirmation
def afficher_confirmation(ecr, message):
    # Sauvegarder l'écran actuel
    ecran_sauvegarde = ecr.copy()
    
    # Crée une surface semi-transparente
    overlay = Surface((lrg, htr), SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Noir semi-transparent
    ecr.blit(overlay, (0, 0))
    
    # Dimensions et position de la boîte de dialogue
    dialog_width, dialog_height = 500, 200
    dialog_x, dialog_y = (lrg - dialog_width) // 2, (htr - dialog_height) // 2
    
    # Dessiner la boîte de dialogue
    dialog_rect = Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    draw.rect(ecr, CONFIRMATION_FOND, dialog_rect, border_radius=15)  # Fond
    draw.rect(ecr, CONFIRMATION_BORDURE, dialog_rect, 2, border_radius=15)  # Bordure
    
    # Texte du message
    msg_font = font.Font(None, 30)
    msg_lines = message.split('\n')
    for i, line in enumerate(msg_lines):
        text_surf = msg_font.render(line, True, TEXTE)
        text_rect = text_surf.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 60 + i*30))
        ecr.blit(text_surf, text_rect)
    
    # Boutons
    btn_width, btn_height = 150, 50
    btn_spacing = 40
    
    # Bouton Oui
    yes_rect = Rect(dialog_x + dialog_width//2 - btn_width - btn_spacing//2, 
                   dialog_y + dialog_height - 70, 
                   btn_width, btn_height)
    yes_btn = {"rect": yes_rect, "image": None, "a_joue_son": False, "text": "Oui"}
    
    # Bouton Non
    no_rect = Rect(dialog_x + dialog_width//2 + btn_spacing//2, 
                  dialog_y + dialog_height - 70, 
                  btn_width, btn_height)
    no_btn = {"rect": no_rect, "image": None, "a_joue_son": False, "text": "Non"}
    
    # Gestion des événements
    while True:
        # Dessiner les boutons
        bouton(ecr, BOUTON_OUI_FOND, yes_btn, "Oui", son_survol, son_clicmenu, 10, surbrillance=BOUTON_OUI_SURVOL)
        bouton(ecr, BOUTON_NON_FOND, no_btn, "Non", son_survol, son_clicmenu, 10, surbrillance=BOUTON_NON_SURVOL)
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    # Restaurer l'écran précédent
                    ecr.blit(ecran_sauvegarde, (0, 0))
                    return False
            
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if yes_btn["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    # Restaurer l'écran précédent
                    ecr.blit(ecran_sauvegarde, (0, 0))
                    return True
                
                if no_btn["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    # Restaurer l'écran précédent
                    ecr.blit(ecran_sauvegarde, (0, 0))
                    return False
    
    return False

def selection_niveau():
    running = True
    
    # Charger la progression
    progression = charger_progression()
    niveaux_debloques = progression["niveaux_debloques"]
    
    # Dimensions et style pour les rectangles des niveaux
    box_width = 180
    box_height = 80
    
    # Polices et titre améliorés
    title_font = font.Font(None, 120)
    subtitle_font = font.Font(None, 40)
    level_font = font.Font(None, 40)
    
    title = title_font.render("Vitanox", True, NOM_JEU)
    subtitle = subtitle_font.render("Sélection du niveau", True, TEXTE_INTERACTIF)
    
    title_rect = title.get_rect(center=(lrg//2, htr//8))
    subtitle_rect = subtitle.get_rect(center=(lrg//2, htr//8 + 80))
    
    # Définition des niveaux avec leurs positions
    levels = [
        {"id": 1, "pos": (lrg//6, htr//4), "text": "Niveau 1", "available": 1 in niveaux_debloques},
        {"id": 2, "pos": (lrg//2 - 120, htr//2 - 50), "text": "Niveau 2", "available": 2 in niveaux_debloques},
        {"id": 3, "pos": (lrg//2 + 20, htr//4), "text": "Niveau 3", "available": 3 in niveaux_debloques},
        {"id": 4, "pos": (4*lrg//5, htr//4), "text": "Niveau 4", "available": 4 in niveaux_debloques},
        {"id": 5, "pos": (2*lrg//3, htr//2), "text": "Niveau 5", "available": 5 in niveaux_debloques},
        {"id": 6, "pos": (lrg//6, 3*htr//5), "text": "Niveau 6", "available": 6 in niveaux_debloques},
        {"id": 7, "pos": (lrg//2, 3*htr//4), "text": "Niveau 7", "available": 7 in niveaux_debloques},
        {"id": 8, "pos": (4*lrg//5, 3*htr//4), "text": "Niveau 8", "available": 8 in niveaux_debloques}
    ]
    
    # Bouton de réinitialisation en bas de l'écran
    reset_button = {
        "rect": Rect(lrg//2 - 120, htr - 80, 240, 60),
        "image": None,
        "a_joue_son": False,
        "text": "Réinitialiser le jeu",
        "hover": False,
        "shadow_offset": 4
    }
    
    # Variables d'animation pour le niveau nouvellement débloqué
    newly_unlocked = None
    unlock_anim_time = 0
    unlock_anim_duration = 2000  # Durée de l'animation en ms
    
    # Créer des rectangles pour chaque niveau avec des états de survol et de clic
    for level in levels:
        level["rect"] = Rect(level["pos"][0] - box_width//2, level["pos"][1] - box_height//2, box_width, box_height)
        level["a_joue_son"] = False
        level["image"] = None
        level["hover"] = False
        level["shadow_offset"] = 4
    
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
    
    # Image de fond de l'écran de sélection
    background = None
    
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.get_ticks()
        
        try:
            # Charger et adapter l'image de fond
            if background is None:  # Charger l'image une seule fois
                background = image.load("data/images/image_selection_niveau.png").convert()
                background = transform.scale(background, (rec.right, rec.bottom))
        except Exception as e:
            print(f"Erreur lors du chargement de l'image de fond: {e}")
            if background is None:
                background = Surface((lrg, htr))
                background.fill((240, 240, 245))
        
        ecr.blit(background, (0, 0))
        
        # Dessiner les connexions avec des lignes pointillées en noir
        for conn in connections:
            try:
                start_level = levels[conn[0]]
                end_level = levels[conn[1]]
                start_pos = start_level["rect"].center
                end_pos = end_level["rect"].center
                
                # Ligne pointillée noire
                draw_dashed_line(ecr, BORDURE, start_pos, end_pos, dash_length=8, width=3)
            except Exception as e:
                print(f"Erreur lors du dessin des connexions: {e}")
        
        # Afficher le titre et sous-titre
        ecr.blit(title, title_rect)
        ecr.blit(subtitle, subtitle_rect)
        
        # Mettre à jour l'état de survol
        mouse_pos = mouse.get_pos()
        for level in levels:
            level["hover"] = level["rect"].collidepoint(mouse_pos)
        
        # Vérifier le survol du bouton de réinitialisation
        reset_button["hover"] = reset_button["rect"].collidepoint(mouse_pos)
        
        # Dessiner d'abord les ombres des boutons
        for level in levels:
            try:
                if level["hover"] or (newly_unlocked and level["id"] == newly_unlocked):
                    shadow_offset = level["shadow_offset"] + 2
                else:
                    shadow_offset = level["shadow_offset"]
                
                shadow_rect = Rect(
                    level["rect"].x + shadow_offset,
                    level["rect"].y + shadow_offset,
                    level["rect"].width,
                    level["rect"].height
                )
                
                shadow_surface = Surface((shadow_rect.width, shadow_rect.height), SRCALPHA)
                draw.rect(shadow_surface, OMBRE, Rect(0, 0, shadow_rect.width, shadow_rect.height), border_radius=15)
                ecr.blit(shadow_surface, shadow_rect)
            except Exception as e:
                print(f"Erreur lors du dessin de l'ombre pour le niveau {level['id']}: {e}")
        
        # Dessiner l'ombre du bouton de réinitialisation
        shadow_offset = reset_button["shadow_offset"] + (2 if reset_button["hover"] else 0)
        shadow_rect = Rect(
            reset_button["rect"].x + shadow_offset,
            reset_button["rect"].y + shadow_offset,
            reset_button["rect"].width,
            reset_button["rect"].height
        )
        shadow_surface = Surface((shadow_rect.width, shadow_rect.height), SRCALPHA)
        draw.rect(shadow_surface, OMBRE, Rect(0, 0, shadow_rect.width, shadow_rect.height), border_radius=15)
        ecr.blit(shadow_surface, shadow_rect)
        
        # Dessiner les boutons de niveau
        for level in levels:
            try:
                # Animation spéciale pour le niveau nouvellement débloqué
                is_newly_unlocked = newly_unlocked and level["id"] == newly_unlocked
                
                # Couleurs selon l'état du niveau (disponible ou bloqué)
                if level["available"]:
                    base_color = NIVEAU_DEBLOQUE_FOND
                    hover_color = NIVEAU_DEBLOQUE_SURVOL_FOND
                    border_color = NIVEAU_DEBLOQUE_BORDURE
                    text_color = NIVEAU_DEBLOQUE_TEXTE
                else:
                    base_color = NIVEAU_BLOQUE_FOND
                    hover_color = NIVEAU_BLOQUE_FOND  # Pas de changement pour les niveaux bloqués
                    border_color = NIVEAU_BLOQUE_BORDURE
                    text_color = NIVEAU_BLOQUE_TEXTE
                
                # Couleur selon l'état (avec animation pour niveau débloqué)
                if is_newly_unlocked:
                    # Animation de pulsation pour le niveau nouvellement débloqué
                    anim_progress = (current_time - unlock_anim_time) / unlock_anim_duration
                    pulse_intensity = 0.5 * (1 - anim_progress)
                    pulse_value = abs(sin(current_time / 100.0)) * pulse_intensity
                    
                    # Couleur qui pulse entre normal et doré
                    color = (
                        int(base_color[0] * (1 - pulse_value) + 255 * pulse_value),  # Rouge vers 255
                        int(base_color[1] * (1 - pulse_value) + 215 * pulse_value),  # Vert vers 215
                        int(base_color[2] * (1 - pulse_value) + 0 * pulse_value)     # Bleu vers 0
                    )
                    border_color = INDICATEUR_NOUVEAU  # Bordure dorée
                elif level["hover"] and level["available"]:
                    color = hover_color
                else:
                    color = base_color
                
                # Surface du bouton avec coins arrondis
                button_surface = Surface((level["rect"].width, level["rect"].height), SRCALPHA)
                draw.rect(button_surface, color, Rect(0, 0, level["rect"].width, level["rect"].height), border_radius=15)
                
                # Bordure (plus visible pour niveau nouvellement débloqué)
                border_width = 3 if is_newly_unlocked else 2
                draw.rect(button_surface, border_color, Rect(0, 0, level["rect"].width, level["rect"].height), border_width, border_radius=15)
                
                # Texte du niveau
                text_surf = level_font.render(level["text"], True, text_color)
                text_rect = text_surf.get_rect(center=(level["rect"].width//2, level["rect"].height//2))
                button_surface.blit(text_surf, text_rect)
                
                # Appliquer effet d'animation et de survol
                if level["hover"] and level["available"]:
                    hover_scale = 1.0 + sin(current_time / 200.0) * 0.03
                    scaled_surface = transform.scale(
                        button_surface, 
                        (int(button_surface.get_width() * hover_scale), 
                         int(button_surface.get_height() * hover_scale))
                    )
                    scaled_rect = scaled_surface.get_rect(center=level["rect"].center)
                    ecr.blit(scaled_surface, scaled_rect)
                    
                    if not level["a_joue_son"]:
                        son_survol.play()
                        level["a_joue_son"] = True
                elif is_newly_unlocked:
                    # Animation plus prononcée pour niveau débloqué
                    unlock_scale = 1.0 + sin(current_time / 150.0) * 0.08
                    scaled_surface = transform.scale(
                        button_surface, 
                        (int(button_surface.get_width() * unlock_scale), 
                         int(button_surface.get_height() * unlock_scale))
                    )
                    scaled_rect = scaled_surface.get_rect(center=level["rect"].center)
                    ecr.blit(scaled_surface, scaled_rect)
                    
                    # Arrêter l'animation après sa durée
                    if current_time - unlock_anim_time > unlock_anim_duration:
                        newly_unlocked = None
                else:
                    ecr.blit(button_surface, level["rect"])
                    level["a_joue_son"] = False
                
                # Indicateur visuel pour le niveau disponible
                if level["available"]:
                    indicator_radius = 6
                    indicator_pos = (level["rect"].right - 15, level["rect"].top + 15)
                    indicator_color = INDICATEUR_NOUVEAU if is_newly_unlocked else INDICATEUR_DISPONIBLE
                    draw.circle(ecr, indicator_color, indicator_pos, indicator_radius)
                    
            except Exception as e:
                print(f"Erreur lors du dessin du niveau {level['id']}: {e}")
        
        # Dessiner le bouton de réinitialisation
        try:
            # Couleur selon l'état de survol
            color = BOUTON_REINIT_SURVOL if reset_button["hover"] else BOUTON_REINIT_FOND
            
            # Surface du bouton avec coins arrondis
            button_surface = Surface((reset_button["rect"].width, reset_button["rect"].height), SRCALPHA)
            draw.rect(button_surface, color, Rect(0, 0, reset_button["rect"].width, reset_button["rect"].height), border_radius=15)
            
            # Bordure
            draw.rect(button_surface, BOUTON_REINIT_BORDURE, Rect(0, 0, reset_button["rect"].width, reset_button["rect"].height), 2, border_radius=15)
            
            # Texte du bouton
            text_surf = level_font.render(reset_button["text"], True, TEXTE)
            text_rect = text_surf.get_rect(center=(reset_button["rect"].width//2, reset_button["rect"].height//2))
            button_surface.blit(text_surf, text_rect)
            
            # Appliquer effet de survol
            if reset_button["hover"]:
                hover_scale = 1.0 + sin(current_time / 200.0) * 0.03
                scaled_surface = transform.scale(
                    button_surface, 
                    (int(button_surface.get_width() * hover_scale), 
                     int(button_surface.get_height() * hover_scale))
                )
                scaled_rect = scaled_surface.get_rect(center=reset_button["rect"].center)
                ecr.blit(scaled_surface, scaled_rect)
                
                if not reset_button["a_joue_son"]:
                    son_survol.play()
                    reset_button["a_joue_son"] = True
            else:
                ecr.blit(button_surface, reset_button["rect"])
                reset_button["a_joue_son"] = False
        except Exception as e:
            print(f"Erreur lors du dessin du bouton de réinitialisation: {e}")
            
        display.flip()

        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                running = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                mouse_pos = mouse.get_pos()
                
                # Vérifier si clic sur le bouton de réinitialisation
                if reset_button["rect"].collidepoint(mouse_pos):
                    son_clicmenu.play()
                    # Demander confirmation
                    message = "Êtes-vous sûr de vouloir réinitialiser\nle jeu et perdre toute progression ?"
                    if afficher_confirmation(ecr, message):
                        # Réinitialiser la progression
                        reinitialiser_progression()
                        # Mettre à jour l'interface
                        progression = charger_progression()
                        niveaux_debloques = progression["niveaux_debloques"]
                        for lvl in levels:
                            lvl["available"] = lvl["id"] in niveaux_debloques
                            
                # Vérifier si clic sur un niveau
                for level in levels:
                    if level["rect"].collidepoint(mouse_pos):
                        son_clicmenu.play()
                        if level["available"]:
                            # Lancer le niveau correspondant
                            resultat = page_jeu(level["id"])
                            
                            if resultat:
                                # Si le niveau est terminé avec succès, débloquer le suivant
                                if level["id"] < 8:  # Ne pas dépasser niveau 8
                                    if debloquer_niveau_suivant(level["id"]):
                                        print(f"Niveau {level['id']+1} débloqué !")
                                        newly_unlocked = level["id"] + 1
                                        unlock_anim_time = time.get_ticks()
                                
                                # Mettre à jour l'état des niveaux
                                progression = charger_progression()
                                niveaux_debloques = progression["niveaux_debloques"]
                                for lvl in levels:
                                    lvl["available"] = lvl["id"] in niveaux_debloques
                        else:
                            print(f"{level['text']} non disponible")

    return True