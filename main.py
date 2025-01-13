import pygame
pygame.init()


# Génération de la fenêtre
pygame.display.set_caption("Escalchy")
screen = pygame.display.set_mode((900, 600))

# Charger et redimensionner le background
background = pygame.image.load('Background/prison_cellule.jpg')
background = pygame.transform.scale(background, (900, 600))


# Boucle principale du jeu
running = True

while running:
    # Afficher le background
    screen.blit(background, (0, 0))
        
    # Mettre à jour l'écran
    pygame.display.flip()
    
    # Gérer les événements (fermeture de la fenêtre)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quitter Pygame proprement
pygame.quit()
