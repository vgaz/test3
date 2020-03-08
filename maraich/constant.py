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

L_LEGUMES = [{"nom":"ail",       "famille":"amaryllidacée"},
            {"nom":"artichaut",  "famille" : "asteracée"},
            {"nom":"aubergine",  "famille" : "solanacée"},
            {"nom":"basilic",    "famille" : "lamiacée"},
            {"nom":"betterave",  "famille": "chénopodiacée"},
            {"nom":"blette" ,    "famille": "chénopodiacée"},
            {"nom":"carotte",    "famille" : "apiacée"},
            {"nom":"céleri",     "famille" : "apiacée"},
            {"nom":"chicorée" , "famille": "asteracée"},
            {"nom":"chou" ,      "famille": "brassicacée"},
            {"nom":"ciboule", "famille" : "amaryllidacée"},
            {"nom":"ciboulette", "famille" : "amaryllidacée"},
            {"nom":"claytone de cuba" , "famille": "portulacacée"},
            {"nom":"concombre" , "famille": "cucurbitacée"},
            {"nom":"coriandre",  "famille" : "apiacée"},
            {"nom":"courge" ,    "famille": "cucurbitacée"},
            {"nom":"courgette",  "famille" : "cucurbitacée"},
            {"nom":"cresson" ,      "famille": "brassicacée"},
            {"nom":"échalote",   "famille" : "amaryllidacée"},
            {"nom":"épinard" , "famille": "chénopodiacée"},
            {"nom":"fenouil" , "famille": "apiacée"},
            {"nom":"fève", "famille" : "fabacée"},
            {"nom":"fraise", "famille" : "rosacée"},
            {"nom":"haricot", "famille" : "fabacée"},
            {"nom":"laitue" , "famille": "asteracée"},
            {"nom":"mâche" , "famille": "valérianacée"},
            {"nom":"maïs", "famille" : "poacée"},
            {"nom":"melon", "famille" : "cucurbitacée"},
            {"nom":"mizuna", "famille" : "brassicacée"},
            {"nom":"moutarde", "famille" : "brassicacée"},
            {"nom":"navet" , "famille": "brassicacée"},
            {"nom":"oignon" , "famille": "amaryllidacée"},
            {"nom":"panais" , "famille": "apiacée"},
            {"nom":"pomme de terre", "famille" : "solanacée"},
            {"nom":"persil" , "famille": "apiacée"},
            {"nom":"phacélie","famille" : "hydrophyllacée"},
            {"nom":"poireau" , "famille": "amaryllidacée"},
            {"nom":"pois" , "famille":"fabacée"},
            {"nom":"poivron", "famille" : "solanacée"},
            {"nom":"pourpier doré" , "famille": "portulacacée"},
            {"nom":"radis glaçon", "famille" : "brassicacée"},
            {"nom":"radis noir", "famille" : "brassicacée"},
            {"nom":"radis rose", "famille" : "brassicacée"},
            {"nom":"radis violet", "famille" : "brassicacée"},
            {"nom":"rhubarbe" , "famille": "polygonacées"},
            {"nom":"roquette" , "famille": "brassicacée"},
            {"nom":"sauge" , "famille": "lamiacée"},
            {"nom":"tagette" , "famille": "portulacacée"},
            {"nom":"tanaisie" , "famille": "asteracée"},
            {"nom":"tétragone" , "famille": "aizoacée"},
            {"nom":"thym" , "famille": "lamiacée"},
            {"nom":"tomate", "famille" : "solanacée"}
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
