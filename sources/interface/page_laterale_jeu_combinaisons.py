from pygame import *
from shared.components.config import *

def Page(ecr):
    menu_largeur = 500
    menu_x = lrg
    vitesse = 20
    menu_actif = True
    ouvert = True

    while menu_actif:
        
        # Animation d'ouverture
        if ouvert and menu_x > lrg - menu_largeur:
            menu_x -= vitesse
        elif not ouvert and menu_x < lrg:
            menu_x += vitesse
        
        # Dessine le menu latéral
        draw.rect(ecr, (50, 50, 50), (menu_x, 0, menu_largeur, htr))
        
        titre = font.Font(None, 36).render("Encyclopédie", True, BLC)
        titre_rect = titre.get_rect(center=(menu_x + menu_largeur//2, 50))
        ecr.blit(titre, titre_rect)
        
        display.flip()
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            elif evt.type == KEYDOWN and evt.key == K_ESCAPE:
                menu_actif = False
    
    return True
