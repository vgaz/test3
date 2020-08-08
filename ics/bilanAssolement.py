# -*- coding: utf-8 -*-
import csv
import os, sys

# from django.core.management.base import BaseCommand
# from maraich.models import *
from maraich.settings import log
import re
from maraich import constant


sys.path.insert(-1, "/home/vincent/Documents/donnees/DIVERS/DeveloppementLogiciel/python/MyPyTools")


import MyTools
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



class EvtICS(object):
    
    TYPE_LEG = 1
    TYPE_PHYTO = 2
    TYPE_AMEND = 3
    TYPE_CULTURE = 4
    TYPE_DIVERS = 5
    TYPE_DISTRIB = 6
    TYPE_MOTTES = 7
    TYPE_TERRINE = 8
    
    def __init__(self):
        self.date = None
        self.summary = ""
        self.description = """ """
        self.location = ""
        self.type = None
    
    def __str__(self):
        s_rep = "%s\n%s sur %s\n"%(self.summary, self.date, self.location)
        if self.description:
            s_rep += self.description
        return s_rep
    
    def getNomLegume(self):
        """retourne le nom du légume ou chaine vide si ce n'est pas un évènement légume"""
        if self.type != self.TYPE_LEG:
            return ""
        else:
            for d_leg in constant.L_LEGUMES:
                if self.summary.lower().startswith(d_leg["nom"]):
                    return d_leg["nom"]
            raise Exception("ERREUR : %s n'est pas dans la liste des légumes"%self.summary)
        
    def getFamille(self):
        """retourne le nom de la famille du légume ou chaine vide si ce n'est pas un evenement légume"""
        if self.type != self.TYPE_LEG:
            return ""        
        for d_leg in constant.L_LEGUMES:
            if d_leg["nom"] == self.getNomLegume():
                return d_leg["famille"]

    def traceSend(self, strIn):
        pass
      
        
def getEvents(filePath):
    """ récupère les évenements à partir du fichier ics"""
    l_evts = [] 
    
    #PATERN_PLANCHES = "([BDHS])([0-9])"
    PATERN_PLANCHE = "([BDHS])([0-9]+)(\.[0-9]+)* *(.*)"
   
    #paternPlanches = re.compile(PATERN_PLANCHES) 
    paternPlanche = re.compile(PATERN_PLANCHE) 
    
    
    #     lecture iCS
    #  recup lieu, légume
    with open(filePath, "r+t", encoding="utf-8") as hF:

        _type = None
        s_date = ""
        s_summary = ""
        s_description = ""
        l_locations = []
        s_ligneComplete = """"""
       
      
        for s_ligneCourante in hF:
                             
            if s_ligneCourante.startswith(" "):
                s_ligneComplete += s_ligneCourante[1:].rstrip('\n')
                continue
            
            if not s_ligneComplete:
                ## on garde le début de cette ligne (la premièreligne du fichier), complète ou pas
                s_ligneComplete = s_ligneCourante.rstrip('\n')
                continue
            
            ## on est au début d'une nouvelle ligne 
            ## on gère la ligne complète du dessus
            s_ligneComplete = s_ligneComplete.replace("\\n", "\n")
            s_ligneComplete = s_ligneComplete.replace("\\,", ",").replace("\\;",";")
            ## suppression du commentaire suivant //
#             s_ligneComplete = s_ligneComplete.split("//")[0]
            #########################
            ## début de gestion ligne complète
            ##print (">>>>", s_ligneComplete)   

            if s_ligneComplete.startswith("BEGIN:VEVENT"):
                _type = None
                s_date = ""
                s_summary = ""
                s_description = ""
                l_locations = []
                
             
            if s_ligneComplete.startswith("DTSTART;"):
                s_date = s_ligneComplete
                s_date += s_ligneComplete.replace(" ","")
                s_date = s_date.split(":")[1]
                s_date = s_date[0:8]

            elif s_ligneComplete.startswith("SUMMARY:"):
                s_summary = s_ligneComplete.split("SUMMARY:")[1]
                
                if s_summary.lower().startswith("plantation "):
                    s_summary = s_summary[len("plantation "):].strip()
                    _type = EvtICS.TYPE_LEG
                elif s_summary.lower().startswith("semis "):
                    s_summary = s_summary[len("semis "):].strip()
                    _type = EvtICS.TYPE_LEG
                elif s_summary.lower().startswith("mottes "):
                    s_summary = s_summary[len("mottes "):]
                    _type = EvtICS.TYPE_MOTTES
                elif s_summary.lower().startswith("terrine"):
                    _type = EvtICS.TYPE_TERRINE
                elif s_summary.lower().startswith("Réalisation plants"):
                    s_summary = s_summary[len("Réalisation plants"):]
                    _type = EvtICS.TYPE_MOTTES
                elif s_summary.lower().startswith("repiquage "):
                    s_summary = s_summary[len("repiquage "):].strip()
                    _type = EvtICS.TYPE_LEG
                elif s_summary.lower().startswith("phyto") :
                    _type = EvtICS.TYPE_PHYTO
                elif s_summary.lower().startswith("culture") or "culture." in s_description:
                    _type = EvtICS.TYPE_CULTURE
                elif s_summary.lower().startswith("distribution amap"):
                    _type = EvtICS.TYPE_DISTRIB
                else:
                    _type = EvtICS.TYPE_DIVERS

                 
            elif s_ligneComplete.startswith("LOCATION:"):
                s_location = s_ligneComplete.split("LOCATION:")[1]
                l_locations = s_location.split(",")         


                           
            elif s_ligneComplete.startswith("DESCRIPTION:"):
                s_description = s_ligneComplete.split("DESCRIPTION:")[1]
 
            elif s_ligneComplete.startswith("END:VEVENT"):
                ## création du ou des évenements ; 1 par location 
                for s_loc in l_locations:
#                         patern = paternPlanche.match(s_loc)
#                         if patern:
#                             s_locChamp = patern.group(1)
#                             s_locNumPl =  "%02d"%int(patern.group(2))
#                             s_locNumRang = patern.group(3) or "" # numero de rg
#                             if s_locNumRang : "rang " + s_locNumRang.split(".")[1]
#                             s_locDetail = patern.group(4) or "" # precision debut et fin dans la planche en m
#                             if s_locDetail : s_locDetail = " (%s)"%(s_locDetail)
#                             s_location = "%s%s%s%s"%(s_locChamp, s_locNumPl, s_locNumRang, s_locDetail)
#                         else:
#                             s_location = s_loc      
                
                    evt = EvtICS()
                    evt.type = _type
                    evt.summary = s_summary
                    evt.location = s_loc.strip()
                    evt.date = MyTools.getDateFrom_y_m_d(s_date)
                    evt.description = s_description
                    l_evts.append(evt)   
#                     print(evt)       

   
            #########################
            ## fin de gestion ligne complète
            ## reset ligne complète avec la ligne courante
            s_ligneComplete = s_ligneCourante.rstrip('\n')    
            continue ## next line in file

        return l_evts


def getTxtEvtsAssolement(l_evts):
    
    # retourne une multistring décrivant tous les évenements
    s_txtEvts = ""
    l_evts.sort(key=lambda x: x.date)

    ## tri par lieu
    s_txtEvts += "\n\n------------- Assolement par planche -------------\n\n"
    l_tmp = sorted(l_evts, key=lambda x: x.location[:3])
    for ev in l_tmp:
        if ev.type == EvtICS.TYPE_LEG:
            s_txtEvts += "%s ; %s %s\n"%(MyTools.getDMYFromDate(ev.date), ev.location, ev.summary)
    
    ## tri par légume
    s_txtEvts += "\n\n------------- Assolement par légume -------------\n\n"
    l_tmp = sorted(l_evts, key=lambda x: x.summary.split()[0])
    for ev in l_tmp:
        if ev.type == EvtICS.TYPE_LEG:
            s_txtEvts += "%s ; %s : %s\n"%(MyTools.getDMYFromDate(ev.date), ev.location, ev.summary)
    
    ## info phyto
    s_txtEvts += "\n\n------------- Traitements phytosanitaires -------------\n\n"
    for ev in l_evts:
        if ev.type == EvtICS.TYPE_PHYTO or "phyto." in ev.description :
            s_txtEvts += "%s ; %s ; %s\n%s\n\n"%(MyTools.getDMYFromDate(ev.date), ev.summary, ev.location, ev.description)

    ## info amendement
    s_txtEvts += "\n\n------------- Amendement -------------\n\n"
    for ev in l_evts:
        if "amendement" in ev.summary.lower() :
            s_txtEvts += "%s ; %s ; %s\n%s\n"%(MyTools.getDMYFromDate(ev.date), ev.summary, ev.location, ev.description)

    ## info culture
    s_txtEvts += "\n\n------------- Remarque culture -------------\n\n"
    for ev in l_evts:
        if ev.type == EvtICS.TYPE_CULTURE:
            s_txtEvts += "%s ; %s %s\n%s\n"%(MyTools.getDMYFromDate(ev.date), ev.summary, ev.location, ev.description)
            

    ## info distrib
    s_txtEvts += "\n\n------------- Distributions -------------\n\n"
    for ev in l_evts:
        if ev.type == EvtICS.TYPE_DISTRIB:
            s_txtEvts += ev.__str__()


    ## info diverses
    s_txtEvts += "\n\n------------- Remarques diverses -------------\n\n"
    for ev in l_evts:
        if ev.type == EvtICS.TYPE_DIVERS:
            s_txtEvts += "%s ; %s ; %s\n%s\n"%(MyTools.getDMYFromDate(ev.date), ev.summary,ev.location,ev.description.replace("\\n","\n"))
            
    
    return s_txtEvts

           
        

def getPlanchesPossibles(l_evts, famille, prefixePlanche=""):
    """ recherche les planches disponibles pour une espece donnée
    possibilité de passer une lettre en 3 eme parametre correspondant au prefixe de la parcelle voulue 
    @todo: retenir un delai de rotation"""
    
    print("Recherche des planches disponibles pour planter une %s"%famille)
    l_planches = []
    try:
        for pl in constant.L_PLANCHES:

             
            if prefixePlanche and not pl.startswith(prefixePlanche):
                continue
             
            bFamilleDejaVue = False
            
            for evt in l_evts:
                if evt.type is not EvtICS.TYPE_LEG:
                    continue
                
                if pl == evt.location.split(" ")[0].split(".")[0] and evt.getFamille() == famille:
                    bFamilleDejaVue = True
                    ## deja eu un légume de cette famille, on passe
                    break
                
            if bFamilleDejaVue:
                continue
                
            ## récupération de la localisation de la culture :  si on passe ici, famille encore inconue 
            l_planches.append(pl)
                  
    except:
        print ("ERR", evt)

    
    return (l_planches)
            
        

def getCumul(l_evts, legume):
    """ recup des cumuls de distribution par légume"""
    cumul = 0.0
    paternPaniers = re.compile("paniers : *([0-9]+)")
    paternTotalLegume = re.compile("%s .*: *([0-9]+)"%(legume))
    
    try:
        for evt in l_evts:
            
            if evt.type is not EvtICS.TYPE_DISTRIB:
                continue
            
            bPatPaniers = False
            for s_ligne in evt.description.split("\n"):
                pat = paternTotalLegume.match(s_ligne.lower().strip()) 
                if pat:
                    cumul += float(pat.group(1).replace(",","."))                        
                    print(evt.date, s_ligne)
                    
                    
                if paternPaniers.match(s_ligne):
                    bPatPaniers = True
        
            if not bPatPaniers:
                print ("ERR def paniers le :", evt.date)      
    except:
        print ("ERR", evt, legume)

#     print("cumul", cumul)
    
    return (cumul)


def createCSVDistrib(l_evts):
    """ recup des distribution et création d'un tableau csv de chaque légume par date et taille de panier
    """
    paternParts = re.compile("([0-9]+) ([0-9]+) ([0-9]+) *")
    paternPaniers = re.compile("paniers : ([0-9]+) ([0-9]+) ([0-9]+)")
    paternTotalLegume = re.compile("(.*) *: *([0-9,]+) *(\w+)?")
    s_txt = ""
    
    try:
        s_txt += ('Jour;Date;Taille;Légume;Quantité;Unité;Equivalent poids;Qté Totale en poids;Prix U;Unité_théorique;Montant; Commentaire\n')

        for evt in [ev for ev in l_evts if ev.type == EvtICS.TYPE_DISTRIB]:
            
            legCourant = ""
            uniteCourante = ""
            s_completeComment = ""
            if str(evt.date)=="2020-06-11":
                pass
            
            for s_ligne in evt.description.split("\n"):
                
                s_comment = ""
                if "//" in s_ligne:
                    (s_ligne, s_comment) = s_ligne.split("//")
                s_ligne = s_ligne.strip().lower()  
                              
                if paternPaniers.match(s_ligne):
                    ## que fait on du nb de paniers ?
                    continue

                if legCourant:
          
                    ## recup des valeurs par panier
                    patParts = paternParts.match(s_ligne) 
                    if patParts:
                        partPetits = float(patParts.group(1))
                        partMoyens = float(patParts.group(2))
                        partGrands = float(patParts.group(3))
                        if uniteCourante.lower() == "kg":
                            partPetits = partPetits/1000
                            partMoyens = partMoyens/1000
                            partGrands = partGrands/1000
                            
                        s_jour = MyTools.getWeekDayFromDate(evt.date)
                        s_completeComment += s_comment               
                        
                        
                        prixU=0
                        
                        for d_leg in [ d_legume for d_legume in constant.L_LEGUMES]:
                            if d_leg["nom"].startswith(legCourant):
                                prixU = ("%.2f"%(d_leg["prix"])).replace(".",",")
                                unite_th = constant.D_NOM_UNITE_PROD[d_leg["unite"]]
                                break

                        assert prixU, "pas de prix pour " + legCourant
                        
                        assert uniteCourante , "pas d'unité courante"
                        
                        if unite_th.lower() != uniteCourante.lower():
                            print("ERREUR !!! Pb unité discordante %s le %s"%(legCourant, evt.date))
                            s_completeComment += " !!! Pb unité discordante "


                        
                        s_txt += '"%s";"%s";"petit";"%s";%s;"%s";"";"";%s;"%s";"";"%s"\n'%(s_jour, evt.date, legCourant, (("%.03f")%partPetits).replace(".",","), uniteCourante, prixU, unite_th, s_completeComment)
                        s_txt += '"%s";"%s";"moyen";"%s";%s;"%s";"";"";%s;"%s";"";"%s"\n'%(s_jour, evt.date, legCourant, (("%.03f")%partMoyens).replace(".",","), uniteCourante, prixU, unite_th, s_completeComment)
                        s_txt += '"%s";"%s";"grand";"%s";%s;"%s";"";"";%s;"%s";"";"%s"\n'%(s_jour, evt.date, legCourant, (("%.03f")%partGrands).replace(".",","), uniteCourante, prixU, unite_th, s_completeComment)
                
                patLegume = paternTotalLegume.match(s_ligne)
                if patLegume:
                    
                    legCourant = patLegume.group(1).strip()

                    if patLegume.group(3):
                        uniteCourante = patLegume.group(3)
                    else:
                        uniteCourante = "pièce"
                        
                    s_completeComment += s_comment               
                    continue
                else:
                    legCourant = ""
                    s_completeComment = ""  
 
             
    except:
        print (evt, str(sys.exc_info()[1]))

    MyTools.strToFic("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/AMAP/distribs.csv", 
                     s_txt,
                     coding="ISO-8859-1")
    

if __name__ == '__main__':
    
    dateDebut = MyTools.getDateFrom_d_m_y("1/7/2017")
    dateFin =  MyTools.getDateTimeToday()
    
    ## Création de la liste de tous les évènements
    l_evts = []
#     l_evts += getEvents("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/2018/maraich 2018.ics")
#     l_evts +=  getEvents("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/2019/maraich 2019.ics")
    l_evts +=  getEvents("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/2020/maraich 2020.ics")
    l_evts.sort(key=lambda x: x.date)
        
    ## Filtrage éventuel par période    
    if True :
        dateDebut = MyTools.getDateFrom_d_m_y("1/04/2020")
        dateFin =  MyTools.getDateFrom_d_m_y("31/07/2020")
        l_evts = [evt for evt in l_evts if (evt.date > dateDebut and evt.date < dateFin)]
    print ("Récupération des évènements du %s au %s"%(MyTools.getDMYFromDate(dateDebut),MyTools.getDMYFromDate(dateFin)))
    
    ## Création synthèse des évenements par planche, par légume, par distrib...
    if False:
        MyTools.strToFic("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/historiqueCultures.txt", 
                         getTxtEvtsAssolement(l_evts))
        exit(0)
    
    
    ## récup des cumuls de distribution par légume
    if False:
        for leg in [ d_leg["nom"] for d_leg in constant.L_LEGUMES]:
            cumul = getCumul(l_evts, leg)
            print(leg, ":", cumul)
        exit(0)
    
    if True:
        createCSVDistrib(l_evts)
        
    ## Recherche des planches dispo pour telle ou telle famille de légume
    if False:   
        l_planches = getPlanchesPossibles(l_evts, "solanacée","S")  #  fabacée, amaryllidacée, solanacée, cucurbitacée
        print(l_planches, "\n")
        
        l_planches = getPlanchesPossibles(l_evts, "cucurbitacée","S")  #  fabacée, amaryllidacée, solanacée, cucurbitacée
        print(l_planches, "\n")
        

    
    
    