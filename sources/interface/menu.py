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

def get_active_profile_name():
    """
    Récupère le nom du profil actif depuis le fichier profiles.json.
    """
    try:
        profile_file = os.path.join("data", "profiles.json")
        if not os.path.exists(profile_file):
            return None
            
        with open(profile_file, "r") as f:
            profiles = json.load(f)
            
        active_id = profiles.get("active_profile")
        if not active_id:
            return None
            
        for profile in profiles.get("profiles", []):
            if profile["id"] == active_id:
                return profile.get("name")
                
        return None
    except:
        return None

def dessiner_menu(ecr, image):
    """Affiche le menu principal"""
    
    ecr.blit(image, (0, 0))
    
    hover_jeu = bouton(ecr, MENU_BOUTON, btn_jeu, "Jouer", son_survol, son_clicmenu, r_menu, surbrillance=MENU_BOUTON_SURVOL)
    hover_cfg = bouton(ecr, MENU_BOUTON, btn_cfg, "Paramètres", son_survol, son_clicmenu, r_menu, surbrillance=MENU_BOUTON_SURVOL)
    hover_profil = bouton(ecr, MENU_BOUTON, btn_profil, "Profil", son_survol, son_clicmenu, r_menu, surbrillance=MENU_BOUTON_SURVOL)
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
    txt_titre = police_titre.render("Elescape", True, NOM_JEU)
    rect_titre = txt_titre.get_rect(center=(lrg // 2, htr // 4))
    ecr.blit(txt_titre, rect_titre)
    
    # Afficher le profil actuellement actif
    profile_name = get_active_profile_name()
    if profile_name:
        user_font = font.Font(None, 30)
        user_text = user_font.render(f"Profil actif : {profile_name}", True, TEXTE_INTERACTIF)
        user_rect = user_text.get_rect(topleft=(20, 20))
        ecr.blit(user_text, user_rect)
    
    # Description du jeu sous les boutons dans un rectangle semi-transparent
    description = [
        "Bienvenue dans Elescape, un jeu de découverte et de création !",
        "Combinez des éléments, explorez des environnements divers et variés,",
        "et découvrez plus de 30 objets uniques dans plusieurs niveaux captivants."
    ]
    
    police_description = font.Font(None, 30)
    espacement = 30  # Espacement entre les lignes
    
    # Calculer la hauteur totale nécessaire pour le texte
    hauteur_texte = len(description) * espacement + 40  # 40px de padding (20px en haut et en bas)
    largeur_rectangle = 800  # Largeur du rectangle
    
    # Créer le rectangle de fond
    rect_fond = Rect(
        (lrg - largeur_rectangle) // 2,  # Centré horizontalement
        htr // 2 + 220,                  # Position Y sous les boutons
        largeur_rectangle,
        hauteur_texte
    )
    
    # Dessiner le rectangle semi-transparent avec coins arrondis
    fond_description = Surface((largeur_rectangle, hauteur_texte), SRCALPHA)
    fond_description.fill((30, 30, 40, 180))  # Couleur sombre semi-transparente
    
    # Appliquer des coins arrondis au rectangle
    draw.rect(fond_description, (30, 30, 40, 180), Rect(0, 0, largeur_rectangle, hauteur_texte), border_radius=30)
    
    # Ajouter une bordure subtile
    draw.rect(fond_description, (50, 50, 60, 200), Rect(0, 0, largeur_rectangle, hauteur_texte), width=2, border_radius=30)
    
    # Afficher le rectangle de fond
    ecr.blit(fond_description, rect_fond)
    
    # Dessiner le texte
    y_position = rect_fond.y + 20  # 20px de marge en haut
    
    for ligne in description:
        texte_description = police_description.render(ligne, True, TEXTE)
        rect_description = texte_description.get_rect(center=(lrg // 2, y_position + police_description.get_height() // 2))
        ecr.blit(texte_description, rect_description)
        y_position += espacement  # Déplace la position Y pour la ligne suivante
    

def plein_ecran():
    """Bascule plein écran"""
    global ecr
    if display.get_surface().get_flags() & FULLSCREEN:
        ecr = display.set_mode((lrg, htr), RESIZABLE)
    else:
        ecr = display.set_mode((0, 0), FULLSCREEN)