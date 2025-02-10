from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def get_next_image(current_image, walk_images):
    """Change l'image d'animation et retourne la nouvelle image avec l'index mis à jour."""
    current_image = (current_image + 1) % len(walk_images)
    return walk_images[current_image], current_image

def page_jeu():
    """Menu du jeu avec déplacement du personnage"""
    init()
    
    ecr = display.set_mode((lrg, htr))  # Créer la fenêtre
    walk_images = [image.load(f"data/images/perso/i{i}.jpg") for i in range(1, 7)]  # Charger les images
    
    x, y = lrg // 2, htr // 2  # Position initiale du personnage
    speed = 5  # Vitesse de déplacement
    current_image = 0
    target_x, target_y = x, y  # Position cible
    moving = False
    clock = time.Clock()

    act = True
    while act:
        ecr.fill(BLC)  # Efface l'écran avec la couleur de fond
        
        # Récupération des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            elif evt.type == KEYDOWN and evt.key == K_ESCAPE:
                act = False
            elif evt.type == MOUSEBUTTONDOWN and evt.button ==3:  # Clic pour définir la cible
                target_x, target_y = mouse.get_pos()
                moving = True  # On active le mouvement

        # Gestion du déplacement en continu
        if moving:
            dx = target_x - x
            dy = target_y - y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > speed:  # On avance progressivement vers la cible
                x += (dx / distance) * speed
                y += (dy / distance) * speed
                image_to_blit, current_image = get_next_image(current_image, walk_images)  # Changer d'image
            else:
                x, y = target_x, target_y  # On atteint la cible
                moving = False

        else:
            image_to_blit = walk_images[0]  # Image statique

        # Affichage du personnage
        ecr.blit(image_to_blit, (x - image_to_blit.get_width() // 2, y - image_to_blit.get_height() // 2))
        display.flip()

        clock.tick(30)  # Limite la vitesse d'affichage à 30 FPS

    return True
