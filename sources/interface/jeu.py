from pygame import *
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

def page_jeu():
    """Menu du jeu avec déplacement du personnage"""
    # Chargement des touches
    try:
        with open("data/touches.json", "r") as f:
            touches = json.load(f)
    except:
        touches = {
            'Déplacement': BUTTON_RIGHT,
            'Action': K_SPACE,
            'Retour': K_ESCAPE
        }
    
    walk_images = [image.load(f"data/images/perso/i{i}.jpg") for i in range(1, 7)]
    x, y = lrg // 2, htr // 2
    speed = 5
    current_image = 0
    target_x, target_y = x, y
    moving = False
    clock = time.Clock()
    act = True
    
    while act:
        ecr.fill(BLC)
        
        for evt in event.get():
            if evt.type == QUIT:
                return False
            elif evt.type == KEYDOWN and evt.key == touches['Retour']:
                act = False
            elif evt.type == MOUSEBUTTONDOWN and evt.button == touches['Déplacement']:
                target_x, target_y = mouse.get_pos()
                moving = True
        
        if moving:
            dx = target_x - x
            dy = target_y - y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > speed:
                x += (dx / distance) * speed
                y += (dy / distance) * speed
                current_image = (current_image + 1) % len(walk_images)
            else:
                x, y = target_x, target_y
                moving = False
                current_image = 0
        
        ecr.blit(walk_images[current_image], (x - walk_images[current_image].get_width() // 2, 
                                            y - walk_images[current_image].get_height() // 2))
        display.flip()
        clock.tick(30)
        
    return True
