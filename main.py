import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)  # Fenêtre redimensionnable
pygame.display.set_caption("Menu Principal")

# Chargement du fond d'écran
background = pygame.image.load("background/prison-cellulaire.jpg").convert()
background = pygame.transform.scale(background, (screen_width, screen_height))

# Couleurs
white = (255, 255, 255)
black = (0, 0, 0)

# Police pour les boutons
font = pygame.font.Font(None, 50)

# Boutons (définis par des rectangles)
button_play = pygame.Rect(300, 150, 200, 50)
button_settings = pygame.Rect(300, 250, 200, 50)
button_quit = pygame.Rect(300, 350, 200, 50)

def draw_menu():
    """Dessine le menu principal avec les boutons."""
    screen.blit(background, (0, 0))  # Affiche le fond

    # Dessiner les boutons
    pygame.draw.rect(screen, black, button_play)
    pygame.draw.rect(screen, black, button_settings)
    pygame.draw.rect(screen, black, button_quit)

    # Ajouter le texte sur les boutons
    play_text = font.render("Jouer", True, white)
    settings_text = font.render("Paramètres", True, white)
    quit_text = font.render("Quitter", True, white)

    screen.blit(play_text, (button_play.x + 50, button_play.y + 5))
    screen.blit(settings_text, (button_settings.x + 10, button_settings.y + 5))
    screen.blit(quit_text, (button_quit.x + 50, button_quit.y + 5))

def toggle_fullscreen():
    """Permet de basculer entre plein écran et mode fenêtré."""
    global screen
    fullscreen = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
    if fullscreen:
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# Boucle principale du menu
running = True
while running:
    draw_menu()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:  # Appuyer sur 'F' pour basculer en plein écran
                toggle_fullscreen()

pygame.quit()
sys.exit()
