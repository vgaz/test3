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


def creationICS(csvFilePath, icsFilePath):
    """Création d'un fichier ics de la base à partir du tableau CSV"""
    l_err = []
    
    ## maj variétés, légumes et séries  encodage  "ISO-8859-1"
    with open(csvFilePath, "r+t", encoding="ISO-8859-1") as hF:
        reader = csv.DictReader(hF)

        ics_txt = ICS_HEAD
        
        for d_line in reader:
                        
            try: 
                d_serie = {}
                d_serie["espece"] = d_line.get("nom espece", "").lower().strip() 
                assert d_serie["espece"], 'Champ "nom espece" vide'         
                d_serie["variet"] = d_line.get("Variété", "").lower().strip() 
                assert d_serie["variet"], 'Champ "Variété" vide pour %s'%(d_serie["espece"])         
                nomLeg = "%s %s" % (d_serie["espece"], d_serie["variet"])
                
                d_serie["numSerie"] = d_line.get("Numéro série", "")
                assert d_serie["numSerie"], "pb de numéro de série pour %s"%(nomLeg)
                
                
                d_serie["delaiPepin_j"] = MyTools.getIntInDict(d_line, "Délai pépinière (j)", 0)

                d_serie["s_datePlants"] = d_line.get("Date plants ou semis","")

                if d_serie["delaiPepin_j"]:     ## cas des mottes à faire et semer
                    
                    d_serie["datePlants"] = MyTools.getDateFrom_d_m_y(d_serie["s_datePlants"])           
                    ## maj agenda ics pour les mottes
                    evt_nom = "mottes %s" % (nomLeg)
                    
                    d_serie["nbMottes"] = MyTools.getIntInDict(d_line, "Nombre de mottes", 0)
                    assert  d_serie["nbMottes"], "Attention : pas de nb de mottes pour %s alors qu'une date de fabrication de plants est donnée."%(nomLeg)
                    d_serie["nbTrousParPlaque"] = MyTools.getIntInDict(d_line, "Nb trous par plaque", 0)
                    assert d_serie["nbTrousParPlaque"], "mottes mais pas de nb de trous par plaque pour %s %s"%(d_serie["espece"], d_serie["variet"])
                    evt_txt = "ns:%s\\nx %d (%.02f x %d)"%(d_serie["numSerie"], d_serie["nbMottes"], float(d_serie["nbMottes"]/d_serie["nbTrousParPlaque"]), d_serie["nbTrousParPlaque"])
                    ics_txt += ICS_ITEM%( evt_nom,
                                          evt_txt, 
                                          str(d_serie["datePlants"]).split(" ")[0].replace("-","")+"T080000",
                                          str(d_serie["datePlants"]).split(" ")[0].replace("-","")+"T090000")                    
                    

                d_serie["s_dateEnTerre"] = d_line.get("Date en terre","")
                assert d_serie["s_dateEnTerre"], "'Date en terre' indéfini pour %s"%(nomLeg)
                d_serie["dateEnTerre"] = MyTools.getDateFrom_d_m_y(d_serie["s_dateEnTerre"])        
                
                ## maj agenda ics pour le semis ou le repiquage
                if d_serie["delaiPepin_j"]:
                    evt_nom = "repiquage %s" % (nomLeg)
                else:
                    evt_nom = "semis %s" % (nomLeg)

                if d_line.get("lieu") == 'SERRE':
                    s_lieu = "sous serre"
                else:
                    s_lieu = "en plein champ"
                    
                evt_txt = "ns:%s\\nNb planches : %0.2f (%d m).Tous les %d cm sur %d rangs (%s). %s" %(d_serie["numSerie"],
                                                                            MyTools.getFloatInDict(d_line, "nb planches", 0),
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
            MyTools.strToFic(icsFilePath, ics_txt)
        except:
            s_err = str(sys.exc_info()[1])
            l_err.append(s_err)
            log.error(s_err)

                    
        log.info("Fin de commande\n nombre d'erreurs = %d\n%s"%( len(l_err), "\n".join(l_err)))  


if __name__ == '__main__':

    s_annee = "2021"
    creationICS("/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/%s/csv/planning.%s.csv"%(s_annee, s_annee),
                "/home/vincent/Documents/donnees/maraichage/Armorique/lancieux/LaNouvelais/Cultures/%s/planning.%s.ics"%(s_annee, s_annee))
    