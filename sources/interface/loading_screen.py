#Projet : Elescape
#Auteurs : Mathis MENNESSIER ; Julien MONGENET ; Simon BILLE

from pygame import *
import sys
import os
from math import *

# Assurer que le chemin est correct pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from shared.components.color_config import *

def loading_screen():
    """
    Affiche un écran de chargement simple avec une barre de progression
    Utilise le fond du menu principal (image_menu.png)
    """
    # Initialisation de pygame
    try:
        init()
    except Exception as e:
        print(f"Erreur lors de l'initialisation de pygame: {e}")
        return False
    
    # Chargement de l'image de fond
    try:
        fond = image.load("data/images/bg/image_menu.png").convert()
        fond = transform.scale(fond, (rec.right, rec.bottom))
    except Exception as e:
        print(f"Erreur lors du chargement de l'image de fond: {e}")
        fond = Surface((lrg, htr))
        fond.fill(FOND)  # Utiliser la couleur de fond par défaut
    
    # Configuration de la barre de progression centrée
    progress_width = 600
    progress_height = 20
    progress_x = (lrg - progress_width) // 2
    progress_y = htr // 2 + 50  # Centré verticalement avec un léger décalage vers le bas
    
    # Police pour le texte
    police_loading = font.Font(None, 60)
    police_tip = font.Font(None, 30)
    
    # Texte de chargement
    texte_loading = police_loading.render("Chargement...", True, TEXTE)
    texte_rect = texte_loading.get_rect(center=(lrg // 2, progress_y - 60))
    
    # Astuces
    astuces = [
        "Astuce: Combinez des objets pour en créer de nouveaux",
        "Astuce: Certains objets disparaissent en les combinant",
        "Astuce: Consultez l'encyclopédie pour voir vos découvertes",
        "Astuce: Pour vous déplacer, utilisez le clic droit",
        "Astuce: Le dernier niveau débloqué est indiqué par un halo doré",
        "Astuce: Vous pouvez déplacer tous les élements comme vous le souhaitez",
        "Astuce: Vous pouvez réinitialiser la progression à tout moment"
    ]
    
    # Choisir une astuce aléatoire
    import random
    astuce = random.choice(astuces)
    
    # Créer l'ombre du texte d'astuce
    texte_astuce_shadow = police_tip.render(astuce, True, (10, 10, 10))
    astuce_shadow_rect = texte_astuce_shadow.get_rect(center=(lrg // 2 + 2, progress_y + 62))

    # Créer le texte d'astuce principal
    texte_astuce = police_tip.render(astuce, True, TEXTE_INTERACTIF)
    astuce_rect = texte_astuce.get_rect(center=(lrg // 2, progress_y + 60))
    
    # Animation de la barre de progression
    # Durée minimale de 5 secondes (150 frames à 30 FPS)
    total_frames = 150
    current_frame = 0
    clock = time.Clock()
    
    # Calcul du temps minimum de 5 secondes
    start_time = time.get_ticks()
    min_duration = 5000  # 5 secondes en millisecondes
    
    # Ajouter un logo ou un titre du jeu centré verticalement
    titre_jeu = police_titre.render("Elescape", True, NOM_JEU)
    titre_rect = titre_jeu.get_rect(center=(lrg // 2, htr // 2 - 120))
    
    # Boucle d'animation
    running = True
    while running:
        current_time = time.get_ticks()
        elapsed_time = current_time - start_time
        
        # Vérifier si le temps minimum est écoulé
        if elapsed_time >= min_duration and current_frame >= total_frames:
            break
            
        for evt in event.get():
            if evt.type == QUIT:
                return False
            # L'échap ne fonctionne qu'après le temps minimum
            if evt.type == KEYDOWN and evt.key == K_ESCAPE and elapsed_time >= min_duration:
                return True
        
        # Progression basée sur le temps écoulé mais plafonnée à total_frames
        current_frame = min(total_frames, int((elapsed_time / min_duration) * total_frames))
        progress = current_frame / total_frames
        
        # Affichage
        ecr.blit(fond, (0, 0))
        
        # Animation du titre (légère pulsation)
        scale = 1.0 + 0.05 * abs(sin(time.get_ticks() / 500))
        scaled_titre = transform.scale(titre_jeu, 
                                     (int(titre_jeu.get_width() * scale),
                                      int(titre_jeu.get_height() * scale)))
        scaled_rect = scaled_titre.get_rect(center=titre_rect.center)
        ecr.blit(scaled_titre, scaled_rect)
        
        # Affichage de la barre de progression (fond)
        draw.rect(ecr, VOLUME_CHARG_BG, (progress_x, progress_y, progress_width, progress_height), border_radius=10)
        
        # Barre de progression (remplissage)
        if progress > 0:
            fill_width = int(progress_width * progress)
            draw.rect(ecr, MENU_BOUTON_SURVOL, (progress_x, progress_y, fill_width, progress_height), border_radius=10)
        
        # Contour de la barre
        draw.rect(ecr, VOLUME_BAR_BORDER, (progress_x, progress_y, progress_width, progress_height), 2, border_radius=10)
        
        # Affichage texte
        ecr.blit(texte_loading, texte_rect)
        
        # Afficher l'ombre de l'astuce en premier
        ecr.blit(texte_astuce_shadow, astuce_shadow_rect)
        ecr.blit(texte_astuce, astuce_rect)
        
        # Pourcentage
        pourcentage = int(progress * 100)
        texte_pourcentage = police_tip.render(f"{pourcentage}%", True, TEXTE)
        pourcentage_rect = texte_pourcentage.get_rect(center=(lrg // 2, progress_y + progress_height // 2))
        ecr.blit(texte_pourcentage, pourcentage_rect)
        
        display.flip()
        clock.tick(30)
    
    # Fondu final
    for alpha in range(255, 0, -5):
        fade = Surface((lrg, htr), SRCALPHA)
        fade.fill((0, 0, 0, alpha))
        ecr.blit(fade, (0, 0))
        display.flip()
        time.delay(10)
    
    return True

if __name__ == "__main__":
    # Pour test direct
    loading_screen()