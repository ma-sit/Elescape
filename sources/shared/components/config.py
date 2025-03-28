#Projet : Elescape
#Auteurs : Mathis MENNESSIER ; Julien MONGENET ; Simon BILLE

from pygame import *
from shared.components.color_config import *  # Import des couleurs standardisées

# Initialisation
init()
mixer.init()

# Configuration écran
ecr = display.set_mode((0, 0), FULLSCREEN)
rec = ecr.get_rect()
lrg, htr = ecr.get_size()

# Sons
try:
    son_clic = mixer.Sound("data/sons/click_002.wav")
    mixer.music.load("data/sons/musique_test.mp3")
    son_survol = mixer.Sound("data/sons/clic1.wav")
    son_clicmenu = mixer.Sound("data/sons/clic2.wav")
    mixer.music.set_volume(0.5)
    mixer.music.play(-1)
except:
    print("Error : fichiers sons non trouvés")

# Boutons menu
btn_jeu = {"rect": Rect(lrg/2-125, htr/2-150, 250, 60), "image": None, "a_joue_son": False}
btn_cfg = {"rect": Rect(lrg/2-125, htr/2-50, 250, 60), "image": None, "a_joue_son": False}
btn_profil = {"rect": Rect(lrg/2-125, htr/2+50, 250, 60), "image": None, "a_joue_son": False}
btn_fin = {"rect": Rect(lrg/2-125, htr/2+150, 250, 60), "image": None, "a_joue_son": False}

r_menu = 15

# Boutons jeu
img_bouton = image.load("data/images/autres/book-open-text.png")
img_bouton = transform.scale(img_bouton, (70, 70))

btn_ency = {"rect": Rect(lrg/20*19-50, htr/40, 100, 100), "image": img_bouton, "a_joue_son": False}

r_jeu = 30

# Boutons fin de niveau
btn_quit = {"rect": Rect(lrg//2 - 100, 300, 200, 50), "image": None, "a_joue_son": False}

# Police
fnt = font.Font(None, 50)
police_titre = font.Font(None, 150)
police_options = font.Font(None, 40)
police_fin_niv = font.Font(None, 80)

# Position de la barre de volume
barre_x = 200
barre_y_general = 250
barre_y_musique = 350
barre_y_sfx = 450
barre_largeur = 400
barre_hauteur = 20