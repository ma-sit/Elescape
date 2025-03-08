from pygame import *
import sys
import json
from shared.components.config import *
from interface.menu import bouton, dessiner_menu, plein_ecran
from interface.selection_niveau import selection_niveau
from interface.parametres import page_parametres, page_parametres_superpose, TOUCHES_DEFAUT
from interface.loading_screen import loading_screen  # Import de l'écran de chargement

# Initialisation
try:
    init()
except Exception as e:
    print(f"Erreur lors de l'initialisation de pygame: {e}")
    sys.exit(1)

# Chargement des touches
try:
    with open("data/touches.json", "r") as f:
        touches = json.load(f)
    
    # Vérification que toutes les touches requises sont présentes
    for key in TOUCHES_DEFAUT:
        if key not in touches:
            touches[key] = TOUCHES_DEFAUT[key]
            print(f"Touche '{key}' manquante, utilisation de la valeur par défaut")
except Exception as e:
    print(f"Erreur lors du chargement des touches: {e}")
    touches = TOUCHES_DEFAUT.copy()
    # Sauvegarde du fichier par défaut
    try:
        with open("data/touches.json", "w") as f:
            json.dump(touches, f)
    except:
        print("Impossible de sauvegarder le fichier touches.json par défaut")

# Affichage de l'écran de chargement
if not loading_screen():
    sys.exit(0)

# Chargement fond menu
try:
    img_menu = image.load("data/images/bg/image_menu.png").convert()
    img_menu = transform.scale(img_menu, (rec.right, rec.bottom))
except Exception as e:
    print(f"Erreur lors du chargement de l'image de fond du menu: {e}")
    img_menu = Surface((rec.right, rec.bottom))
    img_menu.fill((50, 50, 70))  # Fond de secours

# Boucle principale avec gestion des erreurs
act = True
while act:
    try:
        dessiner_menu(ecr, img_menu)
        
        for evt in event.get():
            if evt.type == QUIT:
                act = False
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                if btn_jeu["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    try:
                        act = selection_niveau()
                    except Exception as e:
                        print(f"Erreur lors de l'accès à la sélection de niveau: {e}")
                elif btn_cfg["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    try:
                        # Capture l'écran actuel pour l'utiliser comme arrière-plan
                        current_screen = ecr.copy()
                        # Utilise la version superposée des paramètres en passant l'écran actuel
                        param_result = page_parametres_superpose(current_screen)
                        # Si page_parametres_superpose() retourne False, on quitte l'application
                        if not param_result:
                            act = False
                    except Exception as e:
                        print(f"Erreur lors de l'accès aux paramètres: {e}")
                elif btn_fin["rect"].collidepoint(evt.pos):
                    son_clicmenu.play()
                    act = False
            if evt.type == KEYDOWN:
                # Vérifier si la touche est dans notre configuration
                for action, key_code in touches.items():
                    if evt.key == key_code:
                        if action == 'Plein écran':
                            try:
                                plein_ecran()
                            except Exception as e:
                                print(f"Erreur lors du changement de mode d'écran: {e}")
                        elif action == 'Jouer':
                            try:
                                act = selection_niveau()
                            except Exception as e:
                                print(f"Erreur lors de l'accès à la sélection de niveau: {e}")
                        elif action == 'Paramètres':
                            try:
                                # Capture l'écran actuel pour l'utiliser comme arrière-plan
                                current_screen = ecr.copy()
                                # Utilise la version superposée des paramètres en passant l'écran actuel
                                param_result = page_parametres_superpose(current_screen)
                                # Si page_parametres_superpose() retourne False, on quitte l'application
                                if not param_result:
                                    act = False
                            except Exception as e:
                                print(f"Erreur lors de l'accès aux paramètres: {e}")
                        elif action == 'Quitter':
                            act = False
        display.flip()
        time.delay(30)
    except Exception as e:
        print(f"Erreur dans la boucle principale: {e}")
        # Continue la boucle au lieu de planter

# Quitter proprement
try:
    quit()
except:
    pass
    
sys.exit()