#Projet : Elescape
#Auteurs : Mathis MENNESSIER ; Julien MONGENET ; Simon BILLE


import pygame
import sys
import math

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Déplacement fluide avec images")

# Chargement des images pour les différentes directions
walk_down = [pygame.image.load(f'walk_down_{i}.png') for i in range(1, 5)]  # vers le bas
walk_up = [pygame.image.load(f'walk_up_{i}.png') for i in range(1, 5)]      # vers le haut
walk_left = [pygame.image.load(f'walk_left_{i}.png') for i in range(1, 5)]  # vers la gauche
walk_right = [pygame.image.load(f'walk_right_{i}.png') for i in range(1, 5)]  # vers la droite

# Paramètres du personnage
x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # Position initiale
speed = 3  # Vitesse du déplacement
current_image = 0  # Index de l'image en cours pour l'animation

# Variables pour le mouvement
target_x, target_y = x, y  # Position cible
moving = False

# Fonction pour changer l'index de l'image (en fonction de la direction)
def get_next_image(direction):
    global current_image
    current_image = (current_image + 1) % 4  # Passer d'une image à l'autre (quatre images)
    
    if direction == 'down':
        return walk_down[current_image]
    elif direction == 'up':
        return walk_up[current_image]
    elif direction == 'left':
        return walk_left[current_image]
    elif direction == 'right':
        return walk_right[current_image]

# Boucle principale du jeu
clock = pygame.time.Clock()

while True:
    screen.fill((255, 255, 255))  # Fond blanc
    
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Récupérer la position de la souris
            target_x, target_y = pygame.mouse.get_pos()
            moving = True

    # Calculer le mouvement fluide vers la cible
    if moving:
        # Calculer la direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Déterminer la direction principale en fonction de l'angle
        direction = ''
        if abs(dx) > abs(dy):  # Mouvement horizontal
            if dx > 0:
                direction = 'right'
            else:
                direction = 'left'
        else:  # Mouvement vertical
            if dy > 0:
                direction = 'down'
            else:
                direction = 'up'

        # Si la distance est assez grande, on avance un peu
        if distance > speed:
            x += (dx / distance) * speed
            y += (dy / distance) * speed
        else:
            # Arrêter lorsque l'on arrive assez près de la cible
            x, y = target_x, target_y
            moving = False

        # Afficher l'image correspondante pour le mouvement
        screen.blit(get_next_image(direction), (x - walk_down[0].get_width() // 2, y - walk_down[0].get_height() // 2))
    else:
        # Si on n'est pas en mouvement, afficher une image statique ou autre
        screen.blit(walk_down[0], (x - walk_down[0].get_width() // 2, y - walk_down[0].get_height() // 2))

    # Actualiser l'écran
    pygame.display.flip()

    # Limiter les FPS pour un mouvement fluide
    clock.tick(30)
