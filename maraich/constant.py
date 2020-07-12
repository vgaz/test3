# -*- coding: utf-8 -*-
'''
Created on 15 févr. 2015

@author: vincent
'''

APP_NAME = "MARAICH"


# A faire
# 
# placement sur plusieusr planches consécutives 
# 
#  filtrage planches dans chrono planches avec set sans *<br/>
#  
#  
 
APP_VERSION = "1.3"

UNITE_PROD_KG = 1
UNITE_PROD_PIECE = 2
D_NOM_UNITE_PROD = { UNITE_PROD_KG:"Kg", UNITE_PROD_PIECE:"Pièce"}

NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP = "Virtuelle plein champ"
NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS = "Virtuelle sous abris"

PLAQUE_24_230 = (24,230)
PLAQUE_77_55 = (77,55)

DOC_CHRONOVIEW = """Voila la doc de chrono planches<br/>
Il s'agit de placer les séries sur les planches dans le temps"""

L_PLANCHES = ["B1","S10","S11","S12","S13","S14","S15","S16","S20","S21","S22","S23","S24","S25","S26","S30","S31","S32","S33","S34","S35","S36","S40","S41","S42","S43","S44","S45","S46"]

L_LEGUMES = [{"nom":"ail",          "famille":"amaryllidacée",     "prix":3.2},
            {"nom":"aillet",          "famille":"amaryllidacée",     "prix":3.2},
            {"nom":"artichaut",     "famille" : "asteracée",       "prix":3.2},
            {"nom":"aubergine",     "famille" : "solanacée",       "prix":3.2},
            {"nom":"basilic",       "famille" : "lamiacée",        "prix":3.2},
            {"nom":"betterave",     "famille": "chénopodiacée",    "prix":3.2},
            {"nom":"blette" ,       "famille": "chénopodiacée",    "prix":3.2},
            {"nom":"carotte primeur",       "famille" : "apiacée",         "prix":3.2},
            {"nom":"carotte",       "famille" : "apiacée",         "prix":3.2},
            {"nom":"céleri",        "famille" : "apiacée",         "prix":3.2},
            {"nom":"chicorée",      "famille": "asteracée",          "prix":3.2},
            {"nom":"chou" ,         "famille": "brassicacée",      "prix":3.2},
            {"nom":"chou rave" ,         "famille": "brassicacée",      "prix":3.2},
            {"nom":"ciboule",       "famille" : "amaryllidacée",      "prix":3.2},
            {"nom":"ciboulette",    "famille" : "amaryllidacée",   "prix":3.2},
            {"nom":"claytone de cuba", "famille": "portulacacée", "prix":3.2},
            {"nom":"concombre" , "famille": "cucurbitacée",     "prix":3.2},
            {"nom":"coriandre",  "famille" : "apiacée",         "prix":3.2},
            {"nom":"courge" ,    "famille": "cucurbitacée",     "prix":3.2},
            {"nom":"courgette",  "famille" : "cucurbitacée",    "prix":3.2},
            {"nom":"cresson" ,      "famille": "brassicacée",   "prix":3.2},
            {"nom":"échalote",   "famille" : "amaryllidacée",   "prix":3.2},
            {"nom":"épinard" , "famille": "chénopodiacée",      "prix":3.2},
            {"nom":"fenouil" , "famille": "apiacée",            "prix":3.3},
            {"nom":"fève", "famille" : "fabacée",               "prix":3.2},
            {"nom":"fraise", "famille" : "rosacée",             "prix":3.2},
            {"nom":"haricot vert", "famille" : "fabacée",       "prix":3.2},
            {"nom":"laitue" , "famille": "asteracée",           "prix":3.2},
            {"nom":"mâche" , "famille": "valérianacée",         "prix":3.2},
            {"nom":"maïs", "famille" : "poacée",                "prix":3.2},
            {"nom":"melon", "famille" : "cucurbitacée",         "prix":3.2},
            {"nom":"menthe", "famille" : "lamiacée",         "prix":3},
            {"nom":"mizuna", "famille" : "brassicacée",         "prix":3.2},
            {"nom":"moutarde", "famille" : "brassicacée",       "prix":3.2},
            {"nom":"navet" , "famille": "brassicacée",          "prix":3.2},
            {"nom":"navet rose" , "famille": "brassicacée",          "prix":3.2},
            {"nom":"oignon" , "famille": "amaryllidacée",       "prix":3.2},
            {"nom":"oignon jaune" , "famille": "amaryllidacée",       "prix":3.2},
            {"nom":"oignon rose" , "famille": "amaryllidacée",       "prix":3.2},
            {"nom":"oignon blanc" , "famille": "amaryllidacée",       "prix":3.2},
            {"nom":"oignon botte" , "famille": "amaryllidacée",       "prix":3.2},
            {"nom":"panais" , "famille": "apiacée",             "prix":3.2},
            {"nom":"pomme de terre", "famille" : "solanacée",   "prix":3.2},
            {"nom":"pomme de terre primeur", "famille" : "solanacée",   "prix":3.2},
            {"nom":"persil" , "famille": "apiacée",             "prix":3.2},
            {"nom":"phacélie","famille" : "hydrophyllacée",     "prix":3.2},
            {"nom":"poireau" , "famille": "amaryllidacée",      "prix":3.2},
            {"nom":"pois" , "famille":"fabacée",                "prix":3.2},
            {"nom":"pois gourmand" , "famille":"fabacée",                "prix":3.2},
            {"nom":"poivron", "famille" : "solanacée",          "prix":3.2},
            {"nom":"pourpier doré" , "famille": "portulacacée", "prix":3.2},
            {"nom":"radis glaçon", "famille" : "brassicacée",   "prix":3.2},
            {"nom":"radis noir", "famille" : "brassicacée",     "prix":3.2},
            {"nom":"radis rose", "famille" : "brassicacée",     "prix":3.2},
            {"nom":"radis violet", "famille" : "brassicacée",   "prix":3.2},
            {"nom":"rhubarbe" , "famille": "polygonacées",      "prix":3.2},
            {"nom":"roquette" , "famille": "brassicacée",       "prix":3.2},
            {"nom":"salade laitue" , "famille": "asteracée",           "prix":3.2},
            {"nom":"sauge" , "famille": "lamiacée",             "prix":3.2},
            {"nom":"tagette" , "famille": "portulacacée",       "prix":3.2},
            {"nom":"tanaisie" , "famille": "asteracée" ,        "prix":3.2},
            {"nom":"tétragone" , "famille": "aizoacée",         "prix":3.2},
            {"nom":"thym" , "famille": "lamiacée",              "prix":3.2},
            {"nom":"tomate", "famille" : "solanacée",           "prix":5.5}
             ]

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
