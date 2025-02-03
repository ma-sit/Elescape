def niveau1():
    """Premier niveau du jeu"""
    act = True
    
    # Fond niveau 1
    fnd_niv1 = image.load("data/images/bg_level1.jpg").convert()
    fnd_niv1 = transform.scale(fnd_niv1, (lrg, htr))
    
    while act:
        ecr.blit(fnd_niv1, (0, 0))
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:
                    # Afficher le menu paramètres
                    resultat = menu_parametres()
                    if not resultat:
                        return False
        
    return True
