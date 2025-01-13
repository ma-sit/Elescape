encyclopédie={
    1:["Humain",[6,7,10],1,"image/humain"],
    2:["Seau d'eau",[5],0,"image/seau_d'eau"],
    3:["Graine",[5],0,"image/graine"],
    4:["Pierre",[7],1,"image/pierre"],
    5:["Plante",[6],0,"image/plante"],
    6:["Bois",[8],1,"image/bois"],
    7:["Etincelles",[8],0,"image/etincelles"],
    8:["Chaleur",[9],0,"image/chaleur"],
    9:["Metal",[10],0,"image/metal"],
    10:["Clé",[],1,"image/clé"],
    11:["Seau",[9],0,"image/seau"]
}

elements_connus=[1,2,3,4]

def combinaison(element1,element2):
    n=0
    #Vérifie que les elements sont différents, puis si ils peuvent créer qq chose
    if encyclopédie[element1][0]!=encyclopédie[element2][0]:
        for element in encyclopédie[element1][1]:
            if element in encyclopédie[element2][1]:
                n=1
                # retourne l'élément crée
                return element,element1,element2
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
