from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def afficher_victoire_niveau(ecr, niveau, element_final=None):
    """
    Affiche l'écran de victoire lorsqu'un niveau est terminé
    
    Args:
        ecr: Surface d'affichage
        niveau: Numéro du niveau terminé
        element_final: L'élément qui a déclenché la victoire (optionnel)
        
    Returns:
        True si le joueur clique pour continuer, False s'il quitte
    """
    # Flouter l'écran du jeu
    blurred_surface = ecr.copy()
    blurred_surface.fill((180, 180, 180), special_flags=BLEND_RGBA_MULT)
    
    # Création d'un calque semi-transparent
    overlay = Surface((lrg, htr), SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Fond noir semi-transparent
    blurred_surface.blit(overlay, (0, 0))
    
    # Titre de victoire
    victoire_font = font.Font(None, 80)
    victoire_text = victoire_font.render(f"Niveau {niveau} terminé !", True, (255, 255, 255))
    victoire_rect = victoire_text.get_rect(center=(lrg//2, htr//3))
    
    # Instructions
    instruction_font = font.Font(None, 40)
    instruction_text = instruction_font.render("Cliquez pour continuer", True, (200, 200, 200))
    instruction_rect = instruction_text.get_rect(center=(lrg//2, htr*2//3 + 80))
    
    # Félicitations
    bonus_font = font.Font(None, 50)
    bonus_text = bonus_font.render("Félicitations !", True, (255, 215, 0))
    bonus_rect = bonus_text.get_rect(center=(lrg//2, htr//3 - 80))
    
    # Message personnel
    message_font = font.Font(None, 36)
    message_text = message_font.render("Vous avez débloqué le niveau suivant", True, (220, 220, 250))
    message_rect = message_text.get_rect(center=(lrg//2, htr//3 + 80))
    
    # Animation
    clock = time.Clock()
    start_time = time.get_ticks()
    anim_duration = 3000  # 3 secondes
    
    # Boucle d'attente de clic
    attente_clic = True
    while attente_clic:
        current_time = time.get_ticks()
        elapsed = current_time - start_time
        progress = min(1.0, elapsed / anim_duration)
        
        # Effet de fondu
        alpha = int(255 * progress)
        
        # Copier l'arrière-plan flouté
        ecr.blit(blurred_surface, (0, 0))
        
        # Titre avec effet de scale
        scale_factor = 0.5 + 0.5 * progress
        scaled_title = transform.scale(victoire_text, 
                                    (int(victoire_text.get_width() * scale_factor),
                                     int(victoire_text.get_height() * scale_factor)))
        scaled_rect = scaled_title.get_rect(center=victoire_rect.center)
        ecr.blit(scaled_title, scaled_rect)
        
        # Afficher les autres textes avec fondu
        if progress > 0.3:  # Afficher le bonus après 30% de l'animation
            bonus_text.set_alpha(min(255, int((progress - 0.3) * 255 * 1.5)))
            ecr.blit(bonus_text, bonus_rect)
        
        if progress > 0.5:  # Afficher le message après 50% de l'animation
            message_text.set_alpha(min(255, int((progress - 0.5) * 255 * 2.0)))
            ecr.blit(message_text, message_rect)
        
        if progress > 0.7:  # Afficher les instructions après 70% de l'animation
            instruction_alpha = min(255, int((progress - 0.7) * 255 * 3.0))
            instruction_text.set_alpha(instruction_alpha)
            ecr.blit(instruction_text, instruction_rect)
            
            # Effet de pulsation sur les instructions
            if progress > 0.9:
                pulse = abs((time.get_ticks() % 1000) / 1000 - 0.5) * 0.2 + 0.9
                scaled_instr = transform.scale(instruction_text,
                                            (int(instruction_text.get_width() * pulse),
                                             int(instruction_text.get_height() * pulse)))
                scaled_instr_rect = scaled_instr.get_rect(center=instruction_rect.center)
                ecr.blit(scaled_instr, scaled_instr_rect)
        
        display.flip()
        clock.tick(60)
        
        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == MOUSEBUTTONDOWN:
                if progress > 0.7:  # Permettre de cliquer uniquement après l'apparition des instructions
                    attente_clic = False
                    son_clicmenu.play()
                    return True
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                attente_clic = False
                return True
    
    return True