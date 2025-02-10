from pygame import *
from shared.components.config import *

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

    # Position des boutons du menu
    bouton_largeur = 150
    bouton_hauteur = 40
    bouton_y = 150
    espacement = 20

    # Position des barres de volume
    barre_y_general = 250
    barre_y_musique = 350
    barre_y_sfx = 450

    while act:
        ecr.fill(NOR)
        afficher_texte("Paramètres", lrg // 2, 100, police_titre, BLC)

        # Affichage des boutons du menu
        positions_boutons = [
            ("Audio", lrg // 2 - bouton_largeur - espacement),
            ("Interface", lrg // 2),
            ("Touches", lrg // 2 + bouton_largeur + espacement)
        ]

        # Dessiner les boutons du menu
        for texte, x in positions_boutons:
            couleur = BLEU if texte == section_active else BLC
            rect_bouton = Rect(x - bouton_largeur // 2, bouton_y, bouton_largeur, bouton_hauteur)
            draw.rect(ecr, couleur, rect_bouton)
            afficher_texte(texte, x, bouton_y + bouton_hauteur // 2, police_options, NOR)

        if section_active == "Audio":
            # Afficher les textes des volumes
            afficher_texte(f"Volume général : {int(volume_general * 100)}%", barre_x, barre_y_general - 30, police_options, BLEU, "left")
            afficher_texte(f"Volume musique : {int(volume_musique * 100)}%", barre_x, barre_y_musique - 30, police_options, BLEU, "left")
            afficher_texte(f"Volume interface : {int(volume_sfx * 100)}%", barre_x, barre_y_sfx - 30, police_options, BLEU, "left")

            # Affichage des barres de volume
            for volume, y_pos in [(volume_general, barre_y_general),
                                  (volume_musique, barre_y_musique),
                                  (volume_sfx, barre_y_sfx)]:
                rect_barre = Rect(barre_x, y_pos, barre_largeur, barre_hauteur)
                draw.rect(ecr, BLC, rect_barre)
                if volume > 0:
                    rect_rempli = Rect(barre_x, y_pos, int(barre_largeur * volume), barre_hauteur)
                    draw.rect(ecr, BLEU, rect_rempli)

        afficher_texte("Retour (Appuie sur Échap)", lrg // 2, 550, police_options, BLEU)

        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    act = False
            if evt.type == MOUSEBUTTONDOWN:
                x, y = evt.pos
                # Gestion des clics sur les boutons du menu
                if bouton_y <= y <= bouton_y + bouton_hauteur:
                    for texte, pos_x in positions_boutons:
                        if pos_x - bouton_largeur // 2 <= x <= pos_x + bouton_largeur // 2:
                            section_active = texte

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
                x, y = evt.pos
                nouveau_volume = max(0.0, min(1.0, (x - barre_x) / barre_largeur))
                if barre_active == "general":
                    volume_general = nouveau_volume
                elif barre_active == "musique":
                    volume_musique = nouveau_volume
                elif barre_active == "sfx":
                    volume_sfx = nouveau_volume

        # Application du volume général comme multiplicateur des volumes individuels
        volume_musique_final = volume_musique * volume_general
        volume_sfx_final = volume_sfx * volume_general

        mixer.music.set_volume(volume_musique_final)
        son_clic.set_volume(volume_sfx_final)  # Exemple pour un effet sonore spécifique

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
