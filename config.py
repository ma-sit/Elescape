from pygame import *

# Initialisation écran
ecr = display.set_mode((0, 0), FULLSCREEN)
rec = ecr.get_rect()
lrg, htr = ecr.get_size()

# Dimensions boutons
btn_l = 250  # Largeur bouton
btn_h = 60   # Hauteur bouton

# Couleurs
BLC = (255, 255, 255)
NOR = (0, 0, 0)

# Police
fnt = font.Font(None, 50)

# Boutons
btn_jeu = Rect(lrg/2-btn_l/2, htr/2-100, btn_l, btn_h)
btn_cfg = Rect(lrg/2-btn_l/2, htr/2, btn_l, btn_h)
btn_fin = Rect(lrg/2-btn_l/2, htr/2+100, btn_l, btn_h)
