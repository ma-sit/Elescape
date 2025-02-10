def page_parametres():
    """Page des paramètres"""
    act = True
    volume_general = mixer.music.get_volume()
    volume_musique = mixer.music.get_volume()
    volume_sfx = mixer.music.get_volume()
    clic_souris = False
    barre_active = None
    horloge = time.Clock()
    
    # Position des barres
    barre_y_general = 200
    barre_y_musique = 300
    barre_y_sfx = 400
    
    while act:
        ecr.fill(NOR)
        afficher_texte("Paramètres", lrg // 2, 100, police_titre, BLC)
        
        # Textes des volumes (alignés à gauche au-dessus des barres)
        afficher_texte(f"Volume général : {int(volume_general * 100)}%", 
                      barre_x, barre_y_general - 30, 
                      police_options, BLEU, "left")
        afficher_texte(f"Volume musique : {int(volume_musique * 100)}%", 
                      barre_x, barre_y_musique - 30, 
                      police_options, BLEU, "left")
        afficher_texte(f"Volume interface : {int(volume_sfx * 100)}%", 
                      barre_x, barre_y_sfx - 30, 
                      police_options, BLEU, "left")
        
        afficher_texte("Retour (Appuie sur Échap)", lrg // 2, 500, police_options, BLEU)
        
        # Barre volume général
        draw.rect(ecr, BLC, (barre_x, barre_y_general, barre_largeur, barre_hauteur), 
                 border_radius=10)
        dessiner_barre_remplie(volume_general, barre_y_general)
        
        # Barre volume musique
        draw.rect(ecr, BLC, (barre_x, barre_y_musique, barre_largeur, barre_hauteur), 
                 border_radius=10)
        dessiner_barre_remplie(volume_musique, barre_y_musique)
        
        # Barre volume SFX
        draw.rect(ecr, BLC, (barre_x, barre_y_sfx, barre_largeur, barre_hauteur), 
                 border_radius=10)
        dessiner_barre_remplie(volume_sfx, barre_y_sfx)
        
        # Gestion des événements
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    act = False
            if evt.type == MOUSEBUTTONDOWN:
                x, y = evt.pos
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

            if evt.type == MOUSEMOTION and clic_souris:
                x, y = evt.pos
                nouveau_volume = max(0.0, min(1.0, (x - barre_x) / barre_largeur))
                if barre_active == "general":
                    volume_general = nouveau_volume
                elif barre_active == "musique":
                    volume_musique = nouveau_volume
                elif barre_active == "sfx":
                    volume_sfx = nouveau_volume
        
        mixer.music.set_volume(volume_musique)
        display.flip()
        horloge.tick(30)

    return True

def dessiner_barre_remplie(volume, y_pos):
    """Fonction utilitaire pour dessiner la partie remplie d'une barre"""
    largeur_remplie = int(barre_largeur * volume)
    if largeur_remplie > 0:
        if volume == 1.0:
            draw.rect(ecr, BLEU, 
                     (barre_x, y_pos, largeur_remplie, barre_hauteur),
                     border_radius=10)
        else:
            draw.rect(ecr, BLEU, 
                     (barre_x, y_pos, largeur_remplie, barre_hauteur),
                     border_top_left_radius=10, border_bottom_left_radius=10)
