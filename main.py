import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Dimensions initiales de l'écran
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)  # Fenêtre redimensionnable
pygame.display.set_caption("Menu Principal")

# Chargement du fond d'écran
background = pygame.image.load("background/bg_menu.png").convert()
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

def game_page():
    """Affiche la page de jeu."""
    running_game = True
    while running_game:
        screen.fill((100, 100, 100))  # Fond gris pour la page de jeu
        game_text = font.render("Page de Jeu - Appuyez sur Echap pour revenir", True, white)
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
        screen.fill((150, 150, 150))  # Fond gris clair pour la page des paramètres
        settings_text = font.render("Page des Paramètres - Appuyez sur Echap pour revenir", True, white)
        screen.blit(settings_text, (50, screen_height // 2 - 25))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_settings = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_settings = False

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

        # Gestion des clics sur les boutons avec la souris
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Clic gauche
            if button_play.collidepoint(event.pos):
                game_page()  # Aller à la page de jeu
            elif button_settings.collidepoint(event.pos):
                settings_page()  # Aller à la page des paramètres
            elif button_quit.collidepoint(event.pos):
                running = False

        # Gestion des touches du clavier pour accéder aux pages ou activer le plein écran
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:   # Touche F pour basculer en plein écran
                toggle_fullscreen()
            elif event.key == pygame.K_p: # Touche P pour aller à la page de jeu (Play)
                game_page()
            elif event.key == pygame.K_s: # Touche S pour aller aux paramètres (Settings)
                settings_page()
            elif event.key == pygame.K_q: # Touche Q pour quitter (Quit)
                running = False

pygame.quit()
sys.exit()
