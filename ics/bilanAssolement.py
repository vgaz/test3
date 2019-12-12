# -*- coding: utf-8 -*-
import csv
import datetime, os, sys

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
      
        
def getEvtsAssolement(filePath):
    """ récupère les évenements de l'assolement à partir du fichier ics"""
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
        s_location = ""
        s_finMultiligne = ""
        bInDescription = False
        bInDate = False
        bInLocation = False
        bInSummary = False
       
        for s_line in hF:
            
            #s_line = s_line.replace("\\n,", "\n").replace("\\,", ",").replace("\\;",";").rstrip('\n')
            s_line = s_line.replace("\\,", ",").replace("\\;",";").rstrip('\n')
    
                
            if s_line.startswith(" "):
                ## complement de la ligne du dessus
                s_finMultiligne += s_line[1:]
                continue
            else:
                ## on complete éventuelement la multiligne
                ## on va à la ligne
                if s_finMultiligne:
                    s_finMultiligne += "\n"                
                if bInDate:
                    s_date += s_finMultiligne.replace(" ","")
                    s_date = s_date.split(":")[1]
                    s_date = s_date[0:8]
                    bInDate = False
                elif bInLocation: 
                    s_location += s_finMultiligne
                    bInLocation = False
                elif bInDescription:
                    s_description += s_finMultiligne
                    bInDescription = False
                elif bInSummary:
                    s_summary += s_finMultiligne
                    bInSummary = False

                s_finMultiligne = ""
                 

            ## recup evt
            if s_line.startswith("BEGIN:VEVENT"):
                _type = None
                s_date = ""
                s_summary = ""
                s_description = ""
                s_location = ""
                bInDescription = False
                bInDate = False
                continue
            
            if s_line.startswith("DTSTART;"):
                s_date = s_line
                bInDate = True
                continue

            elif s_line.startswith("SUMMARY:"):
                s_summary = s_line.split(":")[1]
                continue
                
            if s_line.startswith("LOCATION:"):
                s_location = s_line.split("LOCATION:")[1]
                bInLocation =True
                continue 
                       
            elif s_line.startswith("DESCRIPTION:") and not bInDescription:
                s_description = s_line.split("DESCRIPTION:")[1]
                bInDescription = True
                continue

            
            elif s_line.startswith("END:VEVENT"):
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
         
                l_locations = s_location.split(",")         
                for s_loc in l_locations:
                    s_loc = s_loc.strip()
                    patern = paternPlanche.match(s_loc)
                    if patern:
                        s_locChamp = patern.group(1)
                        s_locNumPl =  "%02d"%int(patern.group(2))
                        s_locNumRang = patern.group(3) or "" # numero de rg
                        if s_locNumRang : "rang " + s_locNumRang.split(".")[1]
                        s_locDetail = patern.group(4) or "" # precision debut et fin dans la planche en m
                        if s_locDetail : s_locDetail = " (%s)"%(s_locDetail)
                        s_location = "%s%s%s%s"%(s_locChamp, s_locNumPl, s_locNumRang, s_locDetail)
                    else:
                        s_location = s_loc
                    
                    evt = EvtICS()
                    evt.type = _type
                    evt.summary = s_summary
                    evt.location = s_location
                    evt.date = MyTools.getDateFrom_y_m_d(s_date)
                    evt.description = s_description.replace("\\n","\n")
                    l_evts.append(evt)                
            
            continue ## next line in file
        
        ## ici, on a tous les évenements liés à l'assolement de l'année considérée
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
    """ recherche les planches dispo pour une espece donnee 
    @todo: retenir un delai de rotation"""
    
    l_planches = []
    try:
        for pl in constant.L_PLANCHES:

             
            if prefixePlanche and not pl.startswith(prefixePlanche):
                continue
             
            bFamilleDejaVue = False

            for evt in l_evts:
                            
#                 if evt.location == "S44":
#                     pass
                if evt.type is not EvtICS.TYPE_LEG:
                    continue

                if pl in evt.location and evt.getFamille() == famille:
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
    """ recup des cumul de distribution par légume"""
    cumul = 0.0
    paternPaniers = re.compile("paniers : *([0-9]+)")
    patern = re.compile("%s .*: *([0-9]+)"%(legume))
    
    try:
        for evt in l_evts:
            if evt.type is not EvtICS.TYPE_DISTRIB:
                continue
            bPatPaniers = False
            for s_ligne in evt.description.split("\n"):
                pat = patern.match(s_ligne.lower().strip()) 
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


if __name__ == '__main__':
    
    
    l_evts = []
    l_evts = getEvtsAssolement("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/2018/maraich 2018.ics")
    l_evts += ( getEvtsAssolement("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/2019/maraich 2019.ics"))
    l_evts.sort(key=lambda x: x.date)


            
#     for evt in l_evts:            
#         if evt.location == "S44":
#             print(evt)
        
        
    ## Filtrage éventuel par période
    if 1==0 :
        dateDebut = MyTools.getDateFrom_d_m_y("1/5/2019")
        dateFin =  MyTools.getDateFrom_d_m_y("30/4/2020")
        l_evts = [evt for evt in l_evts if (evt.date > dateDebut and evt.date < dateFin)]
        print ("Récoltes du", MyTools.getDMYFromDate(dateDebut), "au", MyTools.getDMYFromDate(dateFin))
    
    ## récup des cumuls de distribution par légume
    if 1==0:
        for leg in [ d_leg["nom"] for d_leg in constant.L_LEGUMES]:
            cumul = getCumul(l_evts, leg)
            print(leg, ":", cumul)
    
#     l_tmp=[]
#     for ev in l_evts:    
#         if (ev.getNomLegume() =="tomate" or ev.getNomLegume() =="pomme de terre")and "S" in ev.location:
#             print(ev)
#             l_tmp.append(ev.location)
#     print(str(l_tmp))
        
    l_planches = getPlanchesPossibles(l_evts, "solanacée","S")
    for pl in l_planches:
        print(pl)
    

    #MyTools.strToFic("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/bilan2019.txt", getTxtEvtsAssolement(l_evts))
    
    
    