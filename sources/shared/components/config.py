from pygame import *

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
btn_jeu = {"rect": Rect(lrg/2-125, htr/2-100, 250, 60), "a_joue_son": False}
btn_cfg = {"rect": Rect(lrg/2-125, htr/2, 250, 60), "a_joue_son": False}
btn_fin = {"rect": Rect(lrg/2-125, htr/2+100, 250, 60), "a_joue_son": False}

# Couleurs
BLC = (255, 255, 255)
NOR = (0, 0, 0)
BLEU = (0, 100, 200)

# Police
fnt = font.Font(None, 50)
police_titre = font.Font(None, 150)
police_options = font.Font(None, 40)

# Position de la barre de volume
barre_x = 200
barre_y_general = 250
barre_y_musique = 350
barre_y_sfx = 450
barre_largeur = 400
barre_hauteur = 20
