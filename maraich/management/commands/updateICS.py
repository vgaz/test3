# -*- coding: utf-8 -*-
import csv
import datetime, os, sys

# from django.core.management.base import BaseCommand
# from maraich.models import *
from maraich.settings import log
import re


sys.path.insert(-1, "/home/vincent/Documents/donnees/DIVERS/DeveloppementLogiciel/python/MyPyTools")
import MyTools
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



ICS_HEAD = """BEGIN:VCALENDAR
PRODID:-//Mozilla.org/NONSGML Mozilla Calendar V1.1//EN
VERSION:2.0
BEGIN:VTIMEZONE
TZID:Europe/Paris
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
END:STANDARD
END:VTIMEZONE
"""
ICS_QUEUE = "END:VCALENDAR"

ICS_ITEM = """BEGIN:VEVENT
SUMMARY:%s
DESCRIPTION:%s
DTSTART;TZID=Europe/Paris:%s
DTEND;TZID=Europe/Paris:%s
TRANSP:OPAQUE
END:VEVENT
"""

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
        self.date = "2018-00-00"
        self.summary = ""
        self.description = ""
        self.location = ""
        self.type = None
    
    def __str__(self):
        return "%s\n%s-%s\n\n"%(self.summary, self.date, self.location)  
            

    def traceSend(self, strIn):
        pass
      
        
def iCS2txtAssolement():
    """ affichage de l'assolement à partir du fichier ics"""
    l_evts = [] 
    
    PATERN_PLANCHES = "([BDHS])([0-9])"
    PATERN_PLANCHE = "([BDHS])([0-9]+)(\.[0-9]+)* *(.*)"
   
    paternPlanches = re.compile(PATERN_PLANCHES) 
    paternPlanche = re.compile(PATERN_PLANCHE) 
    #     lecture iCS
    #  recup lieu, légume
    with open("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/2018-10-28.maraich2018.ics", "r+t", encoding="utf-8") as hF:

        _type = None
        s_date = ""
        s_summary = ""
        s_description = ""
        s_location = ""
        bInDescription = False
        bInDate = False
        bInLocation = False
       
        for s_line in hF:
            
            s_line = s_line.replace("\n", "").replace("\\,", ",").replace("\\;",";")
            
            if bInDate: #la date tient tjs sur 2 lignes
                s_date += s_line.replace(" ","")
                s_date = s_date.split(":")[1]
                s_date = s_date[0:8]
                bInDate = False

            if bInLocation: # tient éventuellement sur 2 lignes max, nous sommes ici apres la 1ere
                ## si la ligne commence par un espace rajouté, c'est que c'est la suite du champ à récuperer, siono, tout tenait sur une ligne
                if s_line.startswith(" "):
                    s_location += s_line[1:] ## on ajoute la deuxieme ligne en virant l'espace
                else:
                    bInLocation = False

            if s_line.startswith("X-MOZ-GENERATION:") or s_line.startswith("LAST-MODIFIED:")\
               or s_line.startswith("TRANSP:") or s_line.startswith("X-EVOLUTION-CALDAV-HREF:") or s_line.startswith("CLASS:PUBLIC")\
               or s_line.startswith("DTEND;") :
                if bInDescription:
                    bInDescription = False
                continue

            ## recup evt
            if "BEGIN:VEVENT" in s_line:
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

            elif bInDescription:
                s_description += s_line
                continue
            
            elif bInDate:
                s_date += s_line
                continue
            
            elif s_line.startswith("END:VEVENT"):
                if s_summary.lower().startswith("plantation "):
                    s_summary = s_summary[len("plantation "):]
                    _type = EvtICS.TYPE_LEG
                elif s_summary.lower().startswith("semis "):
                    s_summary = s_summary[len("semis "):]
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
                    s_summary = s_summary[len("repiquage "):]
                    _type = EvtICS.TYPE_LEG
                elif s_summary.lower().startswith("phyto"):
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
                    evt.description = s_description
                    l_evts.append(evt)                
            
            continue ## next line in file

        ## tri par lieu
        print (30*"-", "Assolement par planche", 30*"-","\n")
        l_evts.sort(key=lambda x: x.location)
        for ev in l_evts:
            if ev.type == EvtICS.TYPE_LEG:
                print( ev.location, ":", ev.date, ev.summary)
        
        ## tri par légume
        print (30*"-", "Assolement par légume", 30*"-","\n")
        l_evts.sort(key=lambda x: x.summary)
        for ev in l_evts:
            if ev.type == EvtICS.TYPE_LEG:
                print(ev.summary, ev.date, ">>", ev.location, "\n" )
        
        ## info phyto
        print (30*"-", "Traitement phyto", 30*"-","\n")
        for ev in l_evts:
            if ev.type == EvtICS.TYPE_PHYTO:
                print(ev.summary, ev.date, ";", ev.location, "\n",  ev.description, "\n" )

        ## info culture
        print (30*"-", "Remarque culture", 30*"-","\n")
        for ev in l_evts:
            if ev.type == EvtICS.TYPE_CULTURE:
                print(ev.summary, ev.date, ";", ev.location, "\n",  ev.description.replace("\\n","\n"), "\n" )
                

        ## info distrib
        print (30*"-", "Distributions", 30*"-","\n")
        l_evts.sort(key=lambda x: x.date)
        for ev in l_evts:
            if ev.type == EvtICS.TYPE_DISTRIB:
                print(ev.date, ev.summary, ";", ev.location, "\n",  ev.description.replace("\\n","\n"), "\n" )
                

        ## info divers
        print (30*"-", "Remarque divers", 30*"-","\n")
        l_evts.sort(key=lambda x: x.date)
        for ev in l_evts:
            if ev.type == EvtICS.TYPE_DIVERS:
                print(ev.date, ev.summary, ";", ev.location, "\n",  ev.description.replace("\\n","\n"), "\n" )
                

              
            
            
        

def creationICS():
    """updatedb : mise à jour de la base à partir des tableaux CSV"""
    l_err = []      

    ## maj variétés, légumes et séries
    with open(os.path.abspath(os.path.join(BASE_DIR, "..", "..","inputs", "planning.csv")), "r+t", encoding="ISO-8859-1") as hF:
        reader = csv.DictReader(hF)

        ics_txt = ICS_HEAD

        for d_line in reader:
        
            try: 
                d_serie = {}
                d_serie["espece"] = d_line.get("Espèce", "").lower().strip()                    
                d_serie["variet"] = d_line.get("Variété", "").lower().strip() 
#                 if "vit" not in d_serie["variet"]:
#                     continue
                
                nomLeg = "%s %s" % (d_serie["espece"], d_serie["variet"])

                d_serie["s_datePlants"] = d_line.get("Date réalisation plants","")
                if d_serie["s_datePlants"]:
                    d_serie["datePlants"] = MyTools.getDateFrom_d_m_y(d_serie["s_datePlants"])           
                    ## maj agenda ics
                    evt_nom = "Réalisation plants %s" % (nomLeg)
                    
                    d_serie["nbMottes"] = MyTools.getIntInDict(d_line, "Nombre de mottes", 0)
                    assert  d_serie["nbMottes"], "pas de nb de mottes pour %s"%(nomLeg)
                    d_serie["typePlaque"] = MyTools.getIntInDict(d_line, "Nb trous par plaque", 0)
                                        
                    evt_txt = "%d mottes, plateaux de %d trous"%(d_serie["nbMottes"], d_serie["typePlaque"])
                    ics_txt += ICS_ITEM%( evt_nom,
                                          evt_txt, 
                                          str(d_serie["datePlants"]).split(" ")[0].replace("-","")+"T080000",
                                          str(d_serie["datePlants"]).split(" ")[0].replace("-","")+"T090000")                    
                    

                    

                
                d_serie["s_dateEnTerre"] = d_line.get("Date en terre","")
                assert d_serie["s_dateEnTerre"], "'Date en terre' indéfini pour %s"%(nomLeg)
                d_serie["dateEnTerre"] = MyTools.getDateFrom_d_m_y(d_serie["s_dateEnTerre"])        
                ## maj agenda ics
                evt_nom = "Plantation %s" % (nomLeg)
                if d_line.get("lieu") == 'SERRE':
                    s_lieu = "sous serre"
                else:
                    s_lieu = "en plein champ"
                    
                evt_txt = "Nb planches : %0.2f (%d m).Tous les %d cm sur %d rangs (%s). Rem : %s" %(MyTools.getFloatInDict(d_line, "nb planches", 0),
                                                            MyTools.getIntInDict(d_line, "Longueur de rang de cette série (m)", 0),                            
                                                            MyTools.getIntInDict(d_line, "Intra rang (cm)", 0),
                                                            MyTools.getIntInDict(d_line, "Nombre de rangs retenus", 0),
                                                            s_lieu,
                                                            d_line.get("Remarque", ""))
                evt_date = d_serie["dateEnTerre"]
                ics_txt += ICS_ITEM%( evt_nom,
                                      evt_txt, 
                                      str(evt_date).split(" ")[0].replace("-","")+"T080000",
                                      str(evt_date).split(" ")[0].replace("-","")+"T090000")            
            except:
                s_err = str(sys.exc_info()[1])
                l_err.append(s_err)
                continue

        try:
            ics_txt += ICS_QUEUE
            MyTools.strToFic(os.path.join(BASE_DIR, "PlanningCultures.ics"), ics_txt)
        except:
            s_err = str(sys.exc_info()[1])
            l_err.append(s_err)
            log.error(s_err)

                    
        log.info("Fin de commande\n nombre d'erreurs = %d\n%s"%( len(l_err), "\n".join(l_err)))  



if __name__ == '__main__':
    
    iCS2txtAssolement()
    
    #creationICS()
      