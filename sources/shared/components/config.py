from pygame import *

# Initialisation
init()
mixer.init()
# Configuration écran
ecr = display.set_mode((0, 0), FULLSCREEN)
rec = ecr.get_rect()
lrg, htr = ecr.get_size()

# Boutons menu
btn_jeu = Rect(lrg/2-125, htr/2-100, 250, 60)
btn_cfg = Rect(lrg/2-125, htr/2, 250, 60)
btn_fin = Rect(lrg/2-125, htr/2+100, 250, 60)

# Couleurs
BLC = (255, 255, 255)
NOR = (0, 0, 0)
BLEU = (0, 100, 200)

# Police
fnt = font.Font(None, 50)
police_titre = font.Font(None, 80)
police_options = font.Font(None, 40)

# Son
mixer.music.load("data/sons/musique_test.mp3")
mixer.music.set_volume(0.5)
mixer.music.play(-1)

# Position de la barre de volume
barre_x = 200
barre_y = 300
barre_largeur = 400
barre_hauteur = 20

# Police
fnt = font.Font(None, 50)
