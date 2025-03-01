from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *
from interface.menu import bouton

def affichage_victoire(niveau, temps_ecoule, nb_fusions, son_fin):
    
    init()
    
    ecr.fill((0, 0, 0))
    surface_temp = ecr.copy()
    clock = time.Clock()
    
    temps_ecoule_s = temps_ecoule / 1000
    minutes = temps_ecoule_s // 60
    secondes = temps_ecoule_s % 60
    
    couleur_bouton = (50, 50, 50)
    surbrillance = (100, 100, 100)
    act = True
    
    temps_debut = time.get_ticks()
    etape = 0
    
    while act:

        if etape == 0:
            texte_victoire = police_fin_niv.render("Victoire !", True, (255, 255, 255))
            ecr.blit(texte_victoire, (lrg // 2 - texte_victoire.get_width() // 2, 50))
        
        temps_ecoule_ms = time.get_ticks() - temps_debut
        
        if etape == 0 and temps_ecoule_ms >= 500:
            etape = 1
            temps_debut = time.get_ticks()  # Redémarre le compteur de temps
        
        elif etape == 1 and temps_ecoule_ms >= 1000:
            txt_temps = police_options.render(f"Temps écoulé : {minutes} minutes et {secondes} secondes", True, (255, 255, 255))
            ecr.blit(txt_temps, (lrg // 2 - txt_temps.get_width() // 2, 150))
            etape = 2
            temps_debut = time.get_ticks()
        
        elif etape == 2 and temps_ecoule_ms >= 1000:
            txt_fusions = police_options.render(f"Nombre de fusions : {nb_fusions}", True, (255, 255, 255))
            ecr.blit(txt_fusions, (lrg // 2 - txt_fusions.get_width() // 2, 200))
            etape = 3
            temps_debut = time.get_ticks()
        
        elif etape == 3 and temps_ecoule_ms >= 1000:
            bouton(ecr, couleur_bouton, btn_quit, "Quitter", son_survol, son_clicmenu, 10, surbrillance)
            etape = 4
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if btn_quit["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    act = False
        
        display.flip()
        clock.tick(60)
