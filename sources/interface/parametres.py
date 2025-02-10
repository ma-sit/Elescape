def page_parametres():
    """Page des paramètres"""
    act = True
    volume_general = mixer.music.get_volume()
    volume_musique = mixer.music.get_volume()
    volume_sfx = mixer.music.get_volume()
    clic_souris = False
    barre_active = None
    horloge = time.Clock()
    section_active = "Audio"  # Section par défaut
    
    # Position des boutons du menu
    bouton_largeur = 150
    bouton_hauteur = 40
    bouton_y = 150
    espacement = 20
    
    # Position des barres
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
        
        for texte, x in positions_boutons:
            couleur = BLEU if texte == section_active else BLC
            draw.rect(ecr, couleur, (x - bouton_largeur//2, bouton_y, bouton_largeur, bouton_hauteur), 
                     border_radius=10)
            afficher_texte(texte, x, bouton_y + bouton_hauteur//2, police_options, NOR)
        
        # Affichage du contenu selon la section active
        if section_active == "Audio":
            # Textes des volumes
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
                draw.rect(ecr, BLC, (barre_x, y_pos, barre_largeur, barre_hauteur), 
                         border_radius=10)
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
        
        afficher_texte("Retour (Appuie sur Échap)", lrg // 2, 500, police_options, BLEU)
        
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
                        if pos_x - bouton_largeur//2 <= x <= pos_x + bouton_largeur//2:
                            section_active = texte
                
                # Gestion des barres de volume si dans la section Audio
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
                    volume_musique = volume_general
                    volume_sfx = volume_general
                elif barre_active == "musique":
                    volume_musique = nouveau_volume
                elif barre_active == "sfx":
                    volume_sfx = nouveau_volume
        
        # Mise à jour des volumes
        volume_musique_final = volume_musique * volume_general
        volume_sfx_final = volume_sfx * volume_general
        mixer.music.set_volume(volume_musique_final)
        
        display.flip()
        horloge.tick(30)

    return True
