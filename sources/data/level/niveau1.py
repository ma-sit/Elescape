from pygame import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.components.config import *

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
            if evt.type == KEYDOWN and evt.key == K_ESCAPE:
                act = False

    return True
