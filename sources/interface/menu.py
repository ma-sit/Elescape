from pygame import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def bouton(ecr, couleur, btn, texte, son_survol, son_click, surbrillance=None):
    """Dessine un bouton interactif avec sons et coins arrondis"""
    rect = btn["rect"]  # Récupérer le pygame.Rect
    survole = rect.collidepoint(mouse.get_pos())

    if survole:
        couleur = surbrillance if surbrillance else couleur
        if not btn["a_joue_son"]:  # Vérifie si le son n'a pas encore été joué
            son_survol.play()
            btn["a_joue_son"] = True
    else:
        btn["a_joue_son"] = False  # Réinitialise quand la souris quitte le bouton

    draw.rect(ecr, couleur, rect, border_radius=15)  # Dessiner le bouton arrondi
    txt_rendu = fnt.render(texte, True, (255, 255, 255))
    ecr.blit(txt_rendu, (rect.x + (rect.width - txt_rendu.get_width()) // 2, rect.y + 10))

    return survole
    

def dessiner_menu(ecr, fnd):
    """Affiche le menu principal"""
    ecr.blit(fnd, (0, 0))
    
    hover_jeu = bouton(ecr, NOR, btn_jeu, "Jouer", son_survol, son_clicmenu, surbrillance=(150, 150, 150))
    hover_cfg = bouton(ecr, NOR, btn_cfg, "Paramètres", son_survol, son_clicmenu, surbrillance=(150, 150, 150))
    hover_fin = bouton(ecr, NOR, btn_fin, "Quitter", son_survol, son_clicmenu, surbrillance=(150, 150, 150))
    
    """Titre du jeu"""
    y=300
    txt_titre = police_titre.render("Vitanox", True, (0, 0, 0))
    rect_titre = txt_titre.get_rect(center=(lrg // 2, y))
    ecr.blit(txt_titre, rect_titre)
    

def plein_ecran():
    """Bascule plein écran"""
    global ecr
    if display.get_surface().get_flags() & FULLSCREEN:
        ecr = display.set_mode((lrg, htr), RESIZABLE)
    else:
        ecr = display.set_mode((0, 0), FULLSCREEN)
