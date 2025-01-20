import pygame
import sys

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Déplacement fluide avec images")

# Chargement des images pour le mouvement
walk_images = [
    pygame.image.load('i1.jpg'),  # Remplacer par le chemin vers vos images
    pygame.image.load('i2.jpg'),
    pygame.image.load('i3.jpg'),
    pygame.image.load('i4.jpg'),
    pygame.image.load('i5.jpg'),
    pygame.image.load('i6.jpg'),
    pygame.image.load('i7.jpg')
]

# Paramètres du personnage
x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # Position initiale
speed = 7  # Vitesse du déplacement
current_image = 0  # Index de l'image en cours pour l'animation

# Variables pour le mouvement
target_x, target_y = x, y  # Position cible
moving = False

# Fonction pour changer l'index de l'image
def get_next_image():
    global current_image
    current_image = (current_image + 1) % len(walk_images)
    return walk_images[current_image]

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
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # Si la distance est assez grande, on avance un peu
        if distance > speed:
            x += (dx / distance) * speed
            y += (dy / distance) * speed
        else:
            # Arrêter lorsque l'on arrive assez près de la cible
            x, y = target_x, target_y
            moving = False

        # Afficher l'image correspondante pour le mouvement
        screen.blit(get_next_image(), (x - walk_images[0].get_width() // 2, y - walk_images[0].get_height() // 2))
    else:
        # Si on n'est pas en mouvement, afficher une image statique ou autre
        screen.blit(walk_images[0], (x - walk_images[0].get_width() // 2, y - walk_images[0].get_height() // 2))

    # Actualiser l'écran
    pygame.display.flip()

    # Limiter les FPS pour un mouvement fluide
    clock.tick(10)