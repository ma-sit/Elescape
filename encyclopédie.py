import csv
from random import *
encyclopédie = []
with open('encyclopédie.csv', newline='') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=';')
    for row in spamreader:
        encyclopédie.append(dict(row))

elements_connus=[1,2,3,4]

def combinaison(element1,element2):
    n=0
    #Vérifie que les elements sont différents, puis si ils peuvent créer qq chose
    if encyclopédie[element1]["Nom"]!=encyclopédie[element2]["Nom"]:
        for element in encyclopédie[element1]["Créations"]:
            if element in encyclopédie[element2]["Créations"]:
                n=1
                e=int(element)
                # retourne l'élément crée
                return e,element1,element2
    # return false si objets non fusionnable
    else:
        return False
    if n==0:
        return False


def nouvel_element(element):
    if element in elements_connus:
        None
    else:
        # retourne l'element si pas encore découvert pour l'afficher en grand
        elements_connus.append(element)
        return element
    




