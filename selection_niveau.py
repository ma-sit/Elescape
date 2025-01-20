from pygame import *
from config import *

class NiveauInfo:
    """Informations sur chaque niveau"""
    def __init__(self, num, img_path, debloque=False):
        self.numero = num
        self.image = image.load(img_path).convert()
        self.debloque = debloque

def afficher_niveaux():
    """Menu de sélection des niveaux"""
    # Configuration
    act = True
    niv_par_page = 5
    decalage = 0
    
    # Liste des niveaux (à compléter avec vos images)
    niveaux = [
        NiveauInfo(1, "background/niveau1_bg.png", True),  # Premier niveau débloqué
        NiveauInfo(2, "background/niveau2_bg.png", False),
        NiveauInfo(3, "background/niveau3_bg.png", False),
        NiveauInfo(4, "background/niveau4_bg.png", False),
        NiveauInfo(5, "background/niveau5_bg.png", False)
    ]

    while act:
        ecr.fill((50, 50, 50))  # Fond sombre
        
        # Affichage des miniatures
        for i in range(niv_par_page):
            idx = i + decalage
            if idx >= len(niveaux):
                break
                
            # Position de la miniature
            x = i * (lrg//5)
            y = htr//3
            larg_min = lrg//6
            haut_min = htr//3
            
            # Redimensionnement et affichage
            min_img = transform.scale(niveaux[idx].image, (larg_min, haut_min))
            
            # Griser si niveau non débloqué
            if not niveaux[idx].debloque:
                surf_gris = Surface((larg_min, haut_min))
                surf_gris.fill((128, 128, 128))
                surf_gris.set_alpha(128)
                min_img.blit(surf_gris, (0, 0))
            
            ecr.blit(min_img, (x + larg_min//2, y))
            
            # Numéro du niveau
            txt = fnt.render(f"Niveau {niveaux[idx].numero}", True, BLC)
            ecr.blit(txt, (x + larg_min//2, y + haut_min + 10))

        display.flip()

        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == KEYDOWN:
                if evt.key == K_ESCAPE:  # Retour au menu
                    act = False
                elif evt.key == K_RIGHT and decalage + niv_par_page < len(niveaux):
                    decalage += niv_par_page  # Page suivante
                elif evt.key == K_LEFT and decalage > 0:
                    decalage -= niv_par_page  # Page précédente
            
            # Clic sur un niveau
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                for i in range(niv_par_page):
                    idx = i + decalage
                    if idx >= len(niveaux):
                        break
                    # Vérifier si clic sur la miniature
                    rect_niv = Rect(i * (lrg//5) + lrg//12, htr//3, lrg//6, htr//3)
                    if rect_niv.collidepoint(evt.pos) and niveaux[idx].debloque:
                        return idx + 1  # Retourne le numéro du niveau sélectionné
    
    return True
