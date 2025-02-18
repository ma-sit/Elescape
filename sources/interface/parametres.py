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
                             lrg // 2, 550, police_options, BLEU)
            else:
                afficher_texte("Cliquez sur une touche à modifier", 
                             lrg // 2, 550, police_options, BLEU)

        afficher_texte("Retour (Échap)", lrg // 2, 550, police_options, BLEU)

        for evt in event.get():
            if evt.type == QUIT:
                with open("data/touches.json", "w") as f:
                    json.dump(touches, f)
                return False

            if evt.type == KEYDOWN:
                if touche_active:
                    if touche_active != "Déplacement":
                        touches[touche_active] = evt.key
                        with open("data/touches.json", "w") as f:
                            json.dump(touches, f)
                        touche_active = None
                elif evt.key == K_ESCAPE:
                    with open("data/touches.json", "w") as f:
                        json.dump(touches, f)
                    act = False

            if evt.type == MOUSEBUTTONDOWN:
                x, y = evt.pos
                
                # Gestion des clics sur les boutons du menu
                if 150 <= y <= 190:
                    for texte, pos_x in positions_boutons:
                        if pos_x - 75 <= x <= pos_x + 75:
                            section_active = texte
                
                # Gestion des touches
                if section_active == "Touches":
                    y_pos = 250
                    for nom in touches:
                        rect_touche = Rect(lrg//2 - 200, y_pos, 400, 60)
                        if rect_touche.collidepoint(x, y):
                            touche_active = nom
                            if nom == "Déplacement":
                                touches[nom] = evt.button
                                with open("data/touches.json", "w") as f:
                                    json.dump(touches, f)
                                touche_active = None
                        y_pos += espacement

                # Gestion des barres de volume
                if section_active == "Audio":
                    if barre_x <= x <= barre_x + barre_largeur:
                        if barre_y_general <= y <= barre_y_general + barre_hauteur:
                            barre_active = "general"
                            clic_souris = True
                        elif barre_y_musique <= y <= barre_y_musique + barre_hauteur:
                            barre_active = "musique"
                            clic_souris = True
                        elif barre_y_sfx <= y <= barre_y_sfx + barre_hauteur:
                            barre_active = "sfx"
                            clic_souris = True

            if evt.type == MOUSEBUTTONUP:
                clic_souris = False
                barre_active = None

            if evt.type == MOUSEMOTION and clic_souris and section_active == "Audio":
                x = evt.pos[0]
                nouveau_volume = max(0.0, min(1.0, (x - barre_x) / barre_largeur))
                if barre_active == "general":
                    volume_general = nouveau_volume
                elif barre_active == "musique":
                    volume_musique = nouveau_volume
                elif barre_active == "sfx":
                    volume_sfx = nouveau_volume

                volume_musique_final = volume_musique * volume_general
                volume_sfx_final = volume_sfx * volume_general
                mixer.music.set_volume(volume_musique_final)
                son_clic.set_volume(volume_sfx_final)

        display.flip()
        horloge.tick(30)
        
    return True

def afficher_texte(texte, x, y, plc, couleur, align="center"):
    surface_texte = plc.render(texte, True, couleur)
    rect_texte = surface_texte.get_rect()
    if align == "center":
        rect_texte.center = (x, y)
    elif align == "right":
        rect_texte.midright = (x, y)
    elif align == "left":
        rect_texte.midleft = (x, y)
    ecr.blit(surface_texte, rect_texte)
