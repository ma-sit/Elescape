from pygame import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def dessiner_menu(ecr, fnd):
    """Affiche le menu principal"""
    ecr.blit(fnd, (0, 0))
    
    draw.rect(ecr, NOR, btn_jeu)
    draw.rect(ecr, NOR, btn_cfg)
    draw.rect(ecr, NOR, btn_fin)
    
    txt_jeu = fnt.render("Jouer", True, BLC)
    txt_cfg = fnt.render("Paramètres", True, BLC)
    txt_fin = fnt.render("Quitter", True, BLC)
    
    ecr.blit(txt_jeu, (btn_jeu.x + 75, btn_jeu.y + 10))
    ecr.blit(txt_cfg, (btn_cfg.x + 25, btn_cfg.y + 10))
    ecr.blit(txt_fin, (btn_fin.x + 60, btn_fin.y + 10))

def plein_ecran():
    """Bascule plein écran"""
    global ecr
    if display.get_surface().get_flags() & FULLSCREEN:
        ecr = display.set_mode((lrg, htr), RESIZABLE)
    else:
        ecr = display.set_mode((0, 0), FULLSCREEN)
