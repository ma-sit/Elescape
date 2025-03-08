from pygame import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import * 
from shared.components.color_config import *

def bouton(ecr, couleur, btn, texte, son_survol, son_click, radius, surbrillance=None):
    """Dessine un bouton interactif avec sons et coins arrondis"""
    rect = btn["rect"]
    survole = rect.collidepoint(mouse.get_pos())

    if survole:
        couleur = surbrillance if surbrillance else couleur
        if not btn["a_joue_son"]:  # Vérifie si le son n'a pas encore été joué
            son_survol.play()
            btn["a_joue_son"] = True
    else:
        btn["a_joue_son"] = False  # Réinitialise quand la souris quitte le bouton
    
    if btn["image"]:
        draw.rect(ecr, couleur, rect, border_radius=radius)
        ecr.blit(btn["image"], (rect.x + (rect.width - btn["image"].get_width()) // 2, rect.y + 15))
    
    else:
        draw.rect(ecr, couleur, rect, border_radius=radius)
        txt_rendu = fnt.render(texte, True, TEXTE)
        # Centre le texte horizontalement et verticalement
        text_rect = txt_rendu.get_rect(center=(rect.x + rect.width // 2, rect.y + rect.height // 2))
        ecr.blit(txt_rendu, text_rect)

    return survole


def dessiner_menu(ecr, image):
    """Affiche le menu principal"""
    
    ecr.blit(image, (0, 0))
    
    hover_jeu = bouton(ecr, MENU_BOUTON, btn_jeu, "Jouer", son_survol, son_clicmenu, r_menu, surbrillance=MENU_BOUTON_SURVOL)
    hover_cfg = bouton(ecr, MENU_BOUTON, btn_cfg, "Paramètres", son_survol, son_clicmenu, r_menu, surbrillance=MENU_BOUTON_SURVOL)
    hover_fin = bouton(ecr, MENU_BOUTON, btn_fin, "Quitter", son_survol, son_clicmenu, r_menu, surbrillance=MENU_BOUTON_SURVOL)
    
    """Titre du jeu"""
    rect_titre = Rect(0, 0, 550, 100)
    rect_titre.center = (lrg // 2, htr // 4)

    survol_titre = rect_titre.collidepoint(mouse.get_pos())
    
    titre_agrandi = False
    taille_titre = 200  # Taille normale du titre
    taille_titre_max = 250  # Taille agrandie

    # Ajustement de la taille
    if survol_titre and not titre_agrandi:
        taille_titre = min(taille_titre + 8, taille_titre_max)  # Grandit progressivement
        titre_agrandi = True
    elif not survol_titre and titre_agrandi:
        taille_titre = max(taille_titre - 8, 60)  # Revient à la taille normale
        titre_agrandi = False

    # Affichage du titre
    police_titre = font.Font(None, taille_titre)
    txt_titre = police_titre.render("Vitanox", True, NOM_JEU)
    rect_titre = txt_titre.get_rect(center=(lrg // 2, htr // 4))
    ecr.blit(txt_titre, rect_titre)
    
    

def plein_ecran():
    """Bascule plein écran"""
    global ecr
    if display.get_surface().get_flags() & FULLSCREEN:
        ecr = display.set_mode((lrg, htr), RESIZABLE)
    else:
        ecr = display.set_mode((0, 0), FULLSCREEN)