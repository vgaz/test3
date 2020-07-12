'''
Created on 12 janv. 2020

@author: vincent
'''
import sys, csv

from maraich.settings import log
import MyTools

l_err = []


class Legume():
        
    def init(self):
        self.codeEspece = ""
        self.nom = ""
        self.famille = ""
        self.s_unite = ""
        self.poidsUnite_g = 0
        self.prix_kg = 0.0
            
    def __str__(self):
        s_rep = "%s (%s), %s, %dg, %.02f€/kg"%(self.nom, 
                              self.s_unite, 
                              self.famille, 
                              self.poidsUnite_g,
                              self.prix_kg)
        return s_rep
        
    def getInfoFromCSVLine(self, d_line):
        ## recup des infos de production.csv pour les infos de base de chaque légume
        self.nom = d_line.get("nom complet","").lower().strip()
        self.famille = d_line.get("Famille","").lower().strip()
        self.s_unite = d_line.get("Unité","").lower().strip()
        self.poidsUnite_g = int(d_line.get("Poids par pièce (g)","").lower().strip())
        self.prix_kg = MyTools.getFloatInDict(d_line, "prix/kg (euro)")                        
            
        
class   legumesManager():
    
    def __init__(self):
        self.l_legumes = []

    def getBaseLegumes(self, filePath):

        ## maj espèces et familles
        with open((filePath), "r+t", encoding="ISO-8859-1") as hF:
            
            reader = csv.DictReader(hF)
            for d_line in reader:
                try:
                    lg = Legume()
                    lg.getInfoFromCSVLine(d_line)
                        
                except:
                    log.error(sys.exc_info()[1])
                    l_err.append(str(sys.exc_info()[1]))
                    print ("Aie, planté")
                    continue
    
                self.l_legumes.append(lg)
                assert lg.prix_kg, "attention !!!!!!!! prix non renseigné"
                print(lg)
    
    def getPrixKg(self, nomLeg):
        
        for leg in self.l_legumes:
            if leg.nom == nomLeg:
                return leg.prix_kg

if __name__ == '__main__':
    
    legsManager = legumesManager()
    legsManager.getBaseLegumes("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/2020/csv/production.2020.csv")
    prix = legsManager.getPrixKg("tomate")
    pass