from pygame import *
from shared.components.config import *
import json

def page_parametres():
    """Page des paramètres"""
    act = True
    volume_general = mixer.music.get_volume()
    volume_musique = mixer.music.get_volume()
    volume_sfx = mixer.music.get_volume()
    clic_souris = False
    barre_active = None
    horloge = time.Clock()
    section_active = "Audio"
    
    # Chargement des touches
    try:
        with open("data/touches.json", "r") as f:
            touches = json.load(f)
    except:
        touches = {
            'Déplacement': BUTTON_RIGHT,
            'Action': K_SPACE,
            'Retour': K_ESCAPE,
            'Plein écran': K_f,
            'Paramètres': K_s,
            'Jouer': K_p,
            'Quitter': K_q
        }
    touche_active = None

    while act:
        ecr.fill(NOR)
        
        # Titre
        afficher_texte("Paramètres", lrg // 2, 100, police_titre, BLC)

        # Position des boutons du menu
        positions_boutons = [
            ("Audio", lrg // 2 - 170),
            ("Interface", lrg // 2),
            ("Touches", lrg // 2 + 170)
        ]

        # Dessiner les boutons du menu
        for texte, x in positions_boutons:
            couleur = BLEU if texte == section_active else BLC
            rect_bouton = Rect(x - 75, 150, 150, 40)
            draw.rect(ecr, couleur, rect_bouton)
            afficher_texte(texte, x, 170, police_options, NOR)

        # Section Audio
        if section_active == "Audio":
            # Afficher les textes des volumes
            afficher_texte(f"Volume général : {int(volume_general * 100)}%", 
                         barre_x, barre_y_general - 30, police_options, BLEU, "left")
            afficher_texte(f"Volume musique : {int(volume_musique * 100)}%", 
                         barre_x, barre_y_musique - 30, police_options, BLEU, "left")
            afficher_texte(f"Volume interface : {int(volume_sfx * 100)}%", 
                         barre_x, barre_y_sfx - 30, police_options, BLEU, "left")

            # Barres de volume
            for volume, y_pos in [(volume_general, barre_y_general),
                                (volume_musique, barre_y_musique),
                                (volume_sfx, barre_y_sfx)]:
                rect_barre = Rect(barre_x, y_pos, barre_largeur, barre_hauteur)
                draw.rect(ecr, BLC, rect_barre)
                if volume > 0:
                    rect_rempli = Rect(barre_x, y_pos, int(barre_largeur * volume), barre_hauteur)
                    draw.rect(ecr, BLEU, rect_rempli)

        # Section Touches
        elif section_active == "Touches":
            y_pos = 250
            espacement = 80
            
            for nom, code in touches.items():
                rect_touche = Rect(lrg//2 - 200, y_pos, 400, 60)
                couleur = BLEU if touche_active == nom else BLC
                draw.rect(ecr, NOR, rect_touche)
                draw.rect(ecr, couleur, rect_touche, 2)
                
                if nom == "Déplacement":
                    nom_touche = "Clic droit" if code == BUTTON_RIGHT else "Clic gauche"
                else:
                    nom_touche = key.name(code).upper()
                    
                afficher_texte(f"{nom} : {nom_touche}", 
                             lrg//2, y_pos + 30, police_options, couleur)
                y_pos += espacement

            if touche_active:
                afficher_texte("Appuyez sur une touche...", 
                             lrg // 2, htr - 100 + y_pos + espacement , police_options,BLC)  
