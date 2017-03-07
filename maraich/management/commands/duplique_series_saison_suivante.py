# -*- coding: utf-8 -*-
import csv
import datetime, os

from django.core.management.base import BaseCommand
from maraich.models import *
from maraich.settings import log, BASE_DIR
import sys
   

class Command(BaseCommand):
    """Duplication de toutes les séries d'une année N vers l'année N+1"""
    help = "Tapper python manage.py duplique_series_saison_suivante"
# 
#     def creationPlanches(self):
#         """Création des planches de base et celles du fichier"""
#         
#         try:
#             p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP)
#         except:
#             p = Planche()
#             p.nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP
#             p.longueur_m = 10000
#             p.largeur_m = 1
#             p.bSerre = False
#             p.save()  
# 
#         try:
#             p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS)
#         except:
#             p = Planche()
#             p.nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS
#             p.longueur_m = 10000
#             p.largeur_m = 1
#             p.bSerre = True
#             p.save()  
# 
#         try:
#             with open(os.path.join(BASE_DIR, "inputs", "Planches.csv"), "r+t", encoding="ISO-8859-1") as hF:
#                 reader = csv.DictReader(hF)
#                 for d_line in reader:                
#                     nomPlanche = d_line.get("nom")
#                     try:
#                         p = Planche.objects.get(nom = nomPlanche)
#                     except:
#                         p = Planche()
#                         p.nom = nomPlanche
#                         print(nomPlanche)
#                         p.longueur_m = int(d_line.get("longueur (m)", "0"))
#                         p.largeur_m = float(d_line.get("largeur (m)", "0").replace(",","."))
#                         p.bSerre = (p.nom[0]=="S")
#                         p.save()
#                         print (p)               
#         except:
#             print(sys.exc_info()[1]) 
#               

    def handle(self, *args, **options):
        """Duplique toutes les séries lancées telle année vers telle autre année"""
        s_err = ""
        try:
            anneeOrigine = 2017
            anneeDestination = 2018
            dateOrig = MyTools.getDateFrom_d_m_y("1/1/%d"%anneeOrigine)
            dateDest =  MyTools.getDateFrom_d_m_y("31/12/%d"%anneeDestination)
            assert dateDest > dateOrig, "Années d'origine et de destination incohérentes"
            
            for serie in Serie.objects.activesSurPeriode(dateOrig, dateDest):
                serieDest = cloneSerie(serie)
                ## changement des dates des évèmenents + 365j
                for evt in serieDest.evenements.all():
                    evt.date += datetime.timedelta(days = 365) 
                    evt.save()

                serieDest.save()
        except:
            s_err = str(sys.exc_info()[1])

        log.info("Fin de comande %s\n%s"%(self.__doc__, s_err))  
