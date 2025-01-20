
import pygame
import sys
from config import *

# Initialisation fenêtre
def init_fenetre():
    """Configure la fenêtre principale du jeu"""
    pygame.init()
    ecr = pygame.display.set_mode((LRG, HTR), pygame.RESIZABLE)
    pygame.display.set_caption("Menu Principal")
    return ecr

def dessiner_menu(ecr, fnt, fnd):
    """Affiche les éléments du menu"""
    ecr.blit(fnd, (0, 0))
    
    # Dessin boutons
    pygame.draw.rect(ecr, NOR, btn_jeu)
    pygame.draw.rect(ecr, NOR, btn_cfg)
    pygame.draw.rect(ecr, NOR, btn_fin)
    
    # Textes des boutons
    txt_jeu = fnt.render("Jouer", True, BLC)
    txt_cfg = fnt.render("Paramètres", True, BLC)
    txt_fin = fnt.render("Quitter", True, BLC)
    
    ecr.blit(txt_jeu, (btn_jeu.x + 50, btn_jeu.y + 5))
    ecr.blit(txt_cfg, (btn_cfg.x + 10, btn_cfg.y + 5))
    ecr.blit(txt_fin, (btn_fin.x + 50, btn_fin.y + 5))

def plein_ecran(ecr):
    """Bascule entre mode fenêtré et plein écran"""
    if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
        ecr = pygame.display.set_mode((LRG, HTR), pygame.RESIZABLE)
    else:
        ecr = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return ecr
