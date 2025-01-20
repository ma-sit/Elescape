from pygame import *

# Initialisation
init()

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

# Police
fnt = font.Font(None, 50)
