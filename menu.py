from pygame import *
from config import *

def dessiner_menu(ecr, fnd):
    """Dessine le menu principal avec les boutons"""
    ecr.blit(fnd, (0, 0))  # Affiche le fond

    # Dessiner les boutons
    draw.rect(ecr, NOR, btn_jeu)
    draw.rect(ecr, NOR, btn_cfg)
    draw.rect(ecr, NOR, btn_fin)

    # Ajouter le texte sur les boutons
    txt_jeu = fnt.render("Jouer", True, BLC)
    txt_cfg = fnt.render("Paramètres", True, BLC)
    txt_fin = fnt.render("Quitter", True, BLC)

    ecr.blit(txt_jeu, (btn_jeu.x + 75, btn_jeu.y + btn_h/5))
    ecr.blit(txt_cfg, (btn_cfg.x + 25, btn_cfg.y + btn_h/5))
    ecr.blit(txt_fin, (btn_fin.x + 60, btn_fin.y + btn_h/5))

def plein_ecran():
    """Bascule plein écran"""
    global ecr
    if display.get_surface().get_flags() & FULLSCREEN:
        ecr = display.set_mode((lrg, htr), RESIZABLE)
    else:
        ecr = display.set_mode((0, 0), FULLSCREEN)
