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
UNITE_PROD_BRIN = 3
UNITE_PROD_BOUQUET = 4
D_NOM_UNITE_PROD = {UNITE_PROD_KG : "kg", 
                    UNITE_PROD_PIECE : "pièce",
                    UNITE_PROD_BRIN : "brin",
                    UNITE_PROD_BOUQUET : "bouquet"
                    }

NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP = "Virtuelle plein champ"
NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS = "Virtuelle sous abris"

PLAQUE_24_230 = (24,230)
PLAQUE_77_55 = (77,55)

DOC_CHRONOVIEW = """Voila la doc de chrono planches<br/>
Il s'agit de placer les séries sur les planches dans le temps"""

L_PLANCHES = ["B1","S10","S11","S12","S13","S14","S15","S16","S20","S21","S22","S23","S24","S25","S26","S30","S31","S32","S33","S34","S35","S36","S40","S41","S42","S43","S44","S45","S46"]


L_LEGUMES = [{"nom":"aillet",        "famille":"amaryllidacée",      "prix":14,       "unite":UNITE_PROD_KG},
            {"nom":"ail",          "famille":"amaryllidacée",      "prix":14,       "unite":UNITE_PROD_KG},
            {"nom":"artichaut",     "famille" : "asteracée",        "prix":0.2,      "unite":UNITE_PROD_PIECE},
            {"nom":"aubergine",     "famille" : "solanacée",        "prix":1.8,      "unite":UNITE_PROD_PIECE},
            {"nom":"basilic",       "famille" : "lamiacée",         "prix":0.3,      "unite":UNITE_PROD_BRIN},
            {"nom":"betterave",     "famille": "chénopodiacée",     "prix":3.5,      "unite":UNITE_PROD_KG},
            {"nom":"blette" ,       "famille": "chénopodiacée",     "prix":4,        "unite":UNITE_PROD_KG},
            {"nom":"carotte primeur","famille" : "apiacée",         "prix":3.8,      "unite":UNITE_PROD_KG},
            {"nom":"carotte",       "famille" : "apiacée",          "prix":3,        "unite":UNITE_PROD_KG},
            {"nom":"céleri branche","famille" : "apiacée",          "prix":3.2,      "unite":UNITE_PROD_KG},
            {"nom":"céleri rave",   "famille" : "apiacée",          "prix":3.5,      "unite":UNITE_PROD_KG},
            {"nom":"chicorée" , "famille": "asteracée",  "prix":1.2,     "unite":UNITE_PROD_PIECE},
            {"nom":"chou de bruxelles","famille": "brassicacée",    "prix":6,        "unite":UNITE_PROD_KG},
            {"nom":"chou de milan" ,    "famille": "brassicacée",       "prix":3.2,      "unite":UNITE_PROD_KG},
            {"nom":"chou blanc",    "famille": "brassicacée",       "prix":3.2,        "unite":UNITE_PROD_KG},
            {"nom":"chou rouge" ,   "famille": "brassicacée",       "prix":3.2,      "unite":UNITE_PROD_KG},
            {"nom":"chou frisé" ,    "famille": "brassicacée",       "prix":3.2,      "unite":UNITE_PROD_KG},
            {"nom":"chou brocoli" , "famille": "brassicacée",       "prix":5,        "unite":UNITE_PROD_KG},
            {"nom":"chou chinois" , "famille": "brassicacée",       "prix":3,        "unite":UNITE_PROD_PIECE},
            {"nom":"chou rutabaga", "famille": "brassicacée",       "prix":2.5,      "unite":UNITE_PROD_KG},
            {"nom":"chou romanesco","famille": "brassicacée",       "prix":3.5,      "unite":UNITE_PROD_KG},
            {"nom":"chou fleur" ,   "famille": "brassicacée",       "prix":4.5,      "unite":UNITE_PROD_PIECE},
            {"nom":"chou rave" ,    "famille": "brassicacée",       "prix":1.8,      "unite":UNITE_PROD_PIECE},
            {"nom":"chou" ,    "famille": "brassicacée",       "prix":1.8,      "unite":UNITE_PROD_PIECE},
            {"nom":"ciboulette",    "famille" : "amaryllidacée",    "prix":1,        "unite":UNITE_PROD_BOUQUET},
            {"nom":"ciboule",       "famille" : "amaryllidacée",    "prix":0.25,     "unite":UNITE_PROD_PIECE},
            {"nom":"claytone de cuba", "famille": "portulacacée",   "prix":12,       "unite":UNITE_PROD_KG},
            {"nom":"concombre" ,    "famille": "cucurbitacée",      "prix":1.3,      "unite":UNITE_PROD_PIECE},
            {"nom":"coriandre",     "famille" : "apiacée",          "prix":1,        "unite":UNITE_PROD_BOUQUET},
            {"nom":"courgette",     "famille" : "cucurbitacée",     "prix":1,        "unite":UNITE_PROD_PIECE},
            {"nom":"courge" ,       "famille": "cucurbitacée",      "prix":3.5,      "unite":UNITE_PROD_KG},
            {"nom":"cresson" ,      "famille": "brassicacée",       "prix":3.2,      "unite":UNITE_PROD_KG},
            {"nom":"échalote",      "famille" : "amaryllidacée",    "prix":5,        "unite":UNITE_PROD_KG},
            {"nom":"épinard" ,      "famille": "chénopodiacée",     "prix":5.5,      "unite":UNITE_PROD_KG},
            {"nom":"fenouil" ,      "famille": "apiacée",           "prix":3,        "unite":UNITE_PROD_KG},
            {"nom":"fève",          "famille" : "fabacée",          "prix":5.5,      "unite":UNITE_PROD_KG},
            {"nom":"fraise",        "famille" : "rosacée",          "prix":4,        "unite":UNITE_PROD_KG},
            {"nom":"haricot",  "famille" : "fabacée",          "prix":8,        "unite":UNITE_PROD_KG},
            {"nom":"laitue" , "famille": "asteracée",  "prix":1.2,     "unite":UNITE_PROD_PIECE},
            {"nom":"mâche" ,        "famille": "valérianacée",      "prix":12,       "unite":UNITE_PROD_KG},
            {"nom":"maïs doux",     "famille" : "poacée",           "prix":1.5,      "unite":UNITE_PROD_PIECE},
            {"nom":"melon",         "famille" : "cucurbitacée",     "prix":2.25,     "unite":UNITE_PROD_PIECE},
            {"nom":"menthe",        "famille" : "lamiacée",         "prix":1,        "unite":UNITE_PROD_BOUQUET},
            {"nom":"mizuna",        "famille" : "brassicacée",      "prix":12,       "unite":UNITE_PROD_KG},
            {"nom":"moutarde",      "famille" : "brassicacée",      "prix":4,        "unite":UNITE_PROD_KG},
            {"nom":"navet" ,        "famille": "brassicacée",       "prix":3,        "unite":UNITE_PROD_KG},
            {"nom":"navet botte" ,  "famille": "brassicacée",        "prix":5,        "unite":UNITE_PROD_KG},
            {"nom":"navet rose" ,   "famille": "brassicacée",        "prix":5,        "unite":UNITE_PROD_KG},
            {"nom":"oignon" ,       "famille": "amaryllidacée",     "prix":3.3,        "unite":UNITE_PROD_KG},
            {"nom":"oignon jaune" , "famille": "amaryllidacée",     "prix":3.3,        "unite":UNITE_PROD_KG},
            {"nom":"oignon rose" ,  "famille": "amaryllidacée",      "prix":3.3,        "unite":UNITE_PROD_KG},
            {"nom":"oignon rouge" , "famille": "amaryllidacée",     "prix":3.3,        "unite":UNITE_PROD_KG},
            {"nom":"oignon blanc" , "famille": "amaryllidacée",     "prix":3.3,        "unite":UNITE_PROD_KG},
            {"nom":"panais" ,       "famille": "apiacée",       "prix":3.5,         "unite":UNITE_PROD_KG},
            {"nom":"persil" ,       "famille": "apiacée",             "prix":1,           "unite":UNITE_PROD_BOUQUET},
            {"nom":"piment" , "famille": "solanacée","prix":0.4,         "unite":UNITE_PROD_PIECE},
            {"nom":"poireau" , "famille": "amaryllidacée",      "prix":0.9,         "unite":UNITE_PROD_PIECE},
            {"nom":"pois" , "famille":"fabacée",                "prix":8,           "unite":UNITE_PROD_KG},
            {"nom":"pois gourmand" , "famille":"fabacée",       "prix":11,          "unite":UNITE_PROD_KG},
            {"nom":"poivron", "famille" : "solanacée",          "prix":0.6,     "unite":UNITE_PROD_PIECE},
            {"nom":"pomme de terre primeur", "famille" : "solanacée",   "prix":4.5,        "unite":UNITE_PROD_KG},
            {"nom":"pomme de terre", "famille" : "solanacée",   "prix":2.8,        "unite":UNITE_PROD_KG},
            {"nom":"phacélie","famille" : "hydrophyllacée",     "prix":3.2,        "unite":UNITE_PROD_KG},
            {"nom":"pourpier doré" , "famille": "portulacacée", "prix":3.2,     "unite":UNITE_PROD_KG},
            {"nom":"radis glaçon", "famille" : "brassicacée",   "prix":4.5,     "unite":UNITE_PROD_KG},
            {"nom":"radis noir", "famille" : "brassicacée",     "prix":4.5,     "unite":UNITE_PROD_KG},
            {"nom":"radis rose", "famille" : "brassicacée",     "prix":5,     "unite":UNITE_PROD_KG},
            {"nom":"radis violet", "famille" : "brassicacée",   "prix":4.5,     "unite":UNITE_PROD_KG},
            {"nom":"rhubarbe" , "famille": "polygonacées",      "prix":6.5,     "unite":UNITE_PROD_KG},
            {"nom":"roquette" , "famille": "brassicacée",       "prix":12,     "unite":UNITE_PROD_KG},
            {"nom":"salade" , "famille": "asteracée",  "prix":1.2,     "unite":UNITE_PROD_PIECE},
            {"nom":"sauge" , "famille": "lamiacée",             "prix":1.2,     "unite":UNITE_PROD_PIECE},
            {"nom":"tagette" , "famille": "portulacacée",       "prix":3.2,     "unite":UNITE_PROD_KG},
            {"nom":"tanaisie" , "famille": "asteracée" ,        "prix":3.2,     "unite":UNITE_PROD_KG},
            {"nom":"tétragone" , "famille": "aizoacée",         "prix":3.2,     "unite":UNITE_PROD_KG},
            {"nom":"thym" , "famille": "lamiacée",              "prix":1.5,     "unite":UNITE_PROD_BOUQUET},
            {"nom":"tomate", "famille" : "solanacée",           "prix":4.9,      "unite":UNITE_PROD_KG}
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
