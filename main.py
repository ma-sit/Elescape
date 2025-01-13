import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu Principal")

# Couleurs
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)

# Police
font = pygame.font.Font(None, 50)

# Boutons
button_play = pygame.Rect(300, 150, 200, 50)
button_settings = pygame.Rect(300, 250, 200, 50)
button_quit = pygame.Rect(300, 350, 200, 50)

def draw_menu():
    """Dessine le menu principal."""
    screen.fill(white)

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

def game_page():
    """Affiche la page de jeu."""
    running_game = True
    while running_game:
        screen.fill(gray)
        game_text = font.render("Page de Jeu - Appuyez sur Echap pour revenir", True, black)
        screen.blit(game_text, (50, screen_height // 2 - 25))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_game = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_game = False

def settings_page():
    """Affiche la page des paramètres."""
    running_settings = True
    while running_settings:
        screen.fill(gray)
        settings_text = font.render("Page des Paramètres - Appuyez sur Echap pour revenir", True, black)
        screen.blit(settings_text, (50, screen_height // 2 - 25))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_settings = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_settings = False

# Boucle principale
running = True
while running:
    draw_menu()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Clic gauche
            if button_play.collidepoint(event.pos):
                game_page()
            elif button_settings.collidepoint(event.pos):
                settings_page()
            elif button_quit.collidepoint(event.pos):
                running = False

pygame.quit()
sys.exit()
