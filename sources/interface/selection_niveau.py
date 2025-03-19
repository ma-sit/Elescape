from pygame import *
import sys
import os
from math import *
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from shared.components.color_config import *
from interface.jeu import page_jeu
from interface.menu import bouton
from shared.utils.progression_utils import (
    charger_progression, 
    sauvegarder_progression, 
    debloquer_niveau_suivant, 
    reinitialiser_progression
)

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

def afficher_niveau_a_venir(ecran, niveau):
    """Affiche un message simple pour un niveau à venir"""
    # Sauvegarder l'écran actuel
    ecran_sauvegarde = ecran.copy()
    
    # Créer un fond semi-transparent
    overlay = Surface((lrg, htr), SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Noir semi-transparent
    ecran.blit(overlay, (0, 0))
    
    # Police et texte
    titre_font = font.Font(None, 80)
    sous_titre_font = font.Font(None, 40)
    
    # Titre
    titre_texte = titre_font.render(f"Niveau {niveau}", True, TEXTE)
    titre_rect = titre_texte.get_rect(center=(lrg//2, htr//3))
    
    # Message
    message_texte = sous_titre_font.render("Ce niveau arrive prochainement", True, TEXTE_INTERACTIF)
    message_rect = message_texte.get_rect(center=(lrg//2, htr//2))
    
    # Instructions
    instructions_texte = sous_titre_font.render("Appuyez sur une touche pour revenir au menu", True, TEXTE_INTERACTIF)
    instructions_rect = instructions_texte.get_rect(center=(lrg//2, 2*htr//3))
    
    # Afficher les textes
    ecran.blit(titre_texte, titre_rect)
    ecran.blit(message_texte, message_rect)
    ecran.blit(instructions_texte, instructions_rect)
    
    display.flip()
    
    # Attendre une action utilisateur
    en_attente = True
    while en_attente:
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN or evt.type == MOUSEBUTTONDOWN:
                en_attente = False
    
    # Restaurer l'écran
    ecran.blit(ecran_sauvegarde, (0, 0))
    return True

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
    
    title = title_font.render("Elescape", True, NOM_JEU)
    
    title_rect = title.get_rect(center=(lrg//2, htr//8))
    
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
        level["scale"] = 1.0  # Facteur d'échelle pour l'animation
    
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
        
        # Vérifier si l'animation de déverrouillage est terminée
        if newly_unlocked is not None:
            anim_progress = (current_time - unlock_anim_time) / unlock_anim_duration
            if anim_progress >= 1.0:
                # Animation terminée, réinitialiser le statut de niveau nouvellement débloqué
                newly_unlocked = None
        
        try:
            # Charger et adapter l'image de fond
            if background is None:  # Charger l'image une seule fois
                background = image.load("data/images/bg/image_selection_niveau.png").convert()
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
        
        # Mettre à jour l'état de survol et l'échelle de chaque niveau
        mouse_pos = mouse.get_pos()
        for level in levels:
            level["hover"] = level["rect"].collidepoint(mouse_pos)
            
            # Animer l'échelle en fonction du survol
            target_scale = 1.08 if level["hover"] and level["available"] else 1.0
            
            # Animation spéciale pour le niveau nouvellement débloqué
            if newly_unlocked and level["id"] == newly_unlocked:
                target_scale = 1.12 + sin(current_time / 150.0) * 0.05  # Animation de pulsation plus prononcée
                
            # Transition fluide de l'échelle
            level["scale"] += (target_scale - level["scale"]) * 0.2
        
        # Vérifier le survol du bouton de réinitialisation
        reset_button["hover"] = reset_button["rect"].collidepoint(mouse_pos)
        reset_scale = 1.05 if reset_button["hover"] else 1.0
        
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
                
                # Calculer les dimensions et position du bouton avec l'échelle
                scaled_width = level["rect"].width * level["scale"]
                scaled_height = level["rect"].height * level["scale"]
                center_x, center_y = level["rect"].center
                
                # Créer un rectangle mis à l'échelle
                scaled_rect = Rect(
                    center_x - scaled_width/2,
                    center_y - scaled_height/2,
                    scaled_width,
                    scaled_height
                )
                
                # Dessiner l'ombre (qui bouge avec le bouton)
                shadow_offset = level["shadow_offset"] + (2 if level["hover"] and level["available"] else 0)
                shadow_rect = Rect(
                    scaled_rect.x + shadow_offset,
                    scaled_rect.y + shadow_offset,
                    scaled_rect.width,
                    scaled_rect.height
                )
                shadow_surface = Surface((shadow_rect.width, shadow_rect.height), SRCALPHA)
                draw_rect_alpha = lambda surface, color, rect, border_radius=0: draw.rect(surface, color, rect, border_radius=border_radius) # Fonction pour contourner le problème de portée
                draw_rect_alpha(shadow_surface, OMBRE, Rect(0, 0, shadow_rect.width, shadow_rect.height), border_radius=15) # Ombre
                ecr.blit(shadow_surface, shadow_rect) # Appliquer l'ombre
                
                # Surface du bouton avec coins arrondis
                button_surface = Surface((scaled_rect.width, scaled_rect.height), SRCALPHA) # Surface transparente
                draw.rect(button_surface, color, Rect(0, 0, scaled_rect.width, scaled_rect.height), border_radius=15) # Fond du bouton (avec coins arrondis) 
                
                # Bordure (plus visible pour niveau nouvellement débloqué)
                border_width = 3 if is_newly_unlocked else 2
                draw.rect(button_surface, border_color, Rect(0, 0, scaled_rect.width, scaled_rect.height), border_width, border_radius=15)
                
                # Texte du niveau (mis à l'échelle complète comme le bouton)
                text_scale = level["scale"]  # Utiliser la même échelle que le bouton
                font_size = int(38 * text_scale)  # Taille de base 38 avec mise à l'échelle
                level_text_font = font.Font(None, font_size)
                text_surf = level_text_font.render(level["text"], True, text_color)
                text_rect = text_surf.get_rect(center=(scaled_rect.width//2, scaled_rect.height//2))
                button_surface.blit(text_surf, text_rect)
                
                # Appliquer le bouton sur l'écran
                ecr.blit(button_surface, scaled_rect)
                
                # Indicateur visuel pour le niveau disponible - se déplace avec le bouton
                if level["available"]:
                    indicator_radius = 6
                    # Position relative par rapport au coin supérieur droit du bouton mis à l'échelle
                    indicator_pos = (scaled_rect.right - 15, scaled_rect.top + 15)
                    indicator_color = INDICATEUR_NOUVEAU if is_newly_unlocked else INDICATEUR_DISPONIBLE
                    
                    # Effet de pulsation sur l'indicateur en survol
                    if level["hover"] or is_newly_unlocked:
                        pulse = 1.0 + sin(current_time / 200.0) * 0.2
                        indicator_radius = int(6 * pulse)
                    
                    draw.circle(ecr, indicator_color, indicator_pos, indicator_radius)
                    
                # Son de survol
                if level["hover"] and level["available"] and not level["a_joue_son"]:
                    son_survol.play()
                    level["a_joue_son"] = True
                elif not level["hover"]:
                    level["a_joue_son"] = False
                    
            except Exception as e:
                print(f"Erreur lors du dessin du niveau {level['id']}: {e}")
        
        # Dessiner le bouton de réinitialisation avec effet de survol
        try:
            # Couleur selon l'état de survol
            color = BOUTON_REINIT_SURVOL if reset_button["hover"] else BOUTON_REINIT_FOND
            
            # Calculer les dimensions et position avec échelle
            scaled_width = reset_button["rect"].width * reset_scale
            scaled_height = reset_button["rect"].height * reset_scale
            center_x, center_y = reset_button["rect"].center
            
            # Créer un rectangle mis à l'échelle
            scaled_reset_rect = Rect(
                center_x - scaled_width/2,
                center_y - scaled_height/2,
                scaled_width,
                scaled_height
            )
            
            # Dessiner l'ombre du bouton de réinitialisation
            shadow_offset = reset_button["shadow_offset"] + (2 if reset_button["hover"] else 0)
            shadow_rect = Rect(
                scaled_reset_rect.x + shadow_offset,
                scaled_reset_rect.y + shadow_offset,
                scaled_reset_rect.width,
                scaled_reset_rect.height
            )
            shadow_surface = Surface((shadow_rect.width, shadow_rect.height), SRCALPHA)
            draw.rect(shadow_surface, OMBRE, Rect(0, 0, shadow_rect.width, shadow_rect.height), border_radius=15)
            ecr.blit(shadow_surface, shadow_rect)
            
            # Surface du bouton avec coins arrondis
            button_surface = Surface((scaled_reset_rect.width, scaled_reset_rect.height), SRCALPHA)
            draw.rect(button_surface, color, Rect(0, 0, scaled_reset_rect.width, scaled_reset_rect.height), border_radius=15)
            
            # Bordure
            draw.rect(button_surface, BOUTON_REINIT_BORDURE, Rect(0, 0, scaled_reset_rect.width, scaled_reset_rect.height), 2, border_radius=15)
            
            # Texte du bouton (mis à l'échelle)
            text_scale = reset_scale
            font_size = int(38 * text_scale)
            reset_text_font = font.Font(None, font_size)
            text_surf = reset_text_font.render(reset_button["text"], True, TEXTE)
            text_rect = text_surf.get_rect(center=(scaled_reset_rect.width//2, scaled_reset_rect.height//2))
            button_surface.blit(text_surf, text_rect)
            
            # Appliquer le bouton sur l'écran
            ecr.blit(button_surface, scaled_reset_rect)
            
            # Son de survol
            if reset_button["hover"] and not reset_button["a_joue_son"]:
                son_survol.play()
                reset_button["a_joue_son"] = True
            elif not reset_button["hover"]:
                reset_button["a_joue_son"] = False
                
        except Exception as e:
            print(f"Erreur lors du dessin du bouton de réinitialisation: {e}")
            
        display.flip()

        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            
            # Modification ici pour retourner au menu principal 
            # quand on appuie sur Échap au lieu de quitter le jeu
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                # Retourne True pour revenir au menu principal
                return True
                
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
                    # Utiliser le rectangle mis à l'échelle pour la détection de collision
                    scaled_width = level["rect"].width * level["scale"]
                    scaled_height = level["rect"].height * level["scale"]
                    center_x, center_y = level["rect"].center
                    scaled_rect = Rect(
                        center_x - scaled_width/2,
                        center_y - scaled_height/2,
                        scaled_width,
                        scaled_height
                    )
                    
                    if scaled_rect.collidepoint(mouse_pos):
                        son_clicmenu.play()
                        if level["available"]:
                            # Cas spécial pour le niveau 3
                            if level["id"] == 3:
                                afficher_niveau_a_venir(ecr, level["id"])
                            else:
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