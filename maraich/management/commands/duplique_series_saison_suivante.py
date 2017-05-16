# -*- coding: utf-8 -*-
import csv
import datetime, os

from django.core.management.base import BaseCommand
from maraich.models import *
from maraich.settings import log, BASE_DIR
import sys
   

class Command(BaseCommand):
    """Duplication de toutes les séries d'une année N vers l'année M
    Tapper python manage.py duplique_series_saison_suivante --orig 20XX --dest 20YY"""


    def add_arguments(self, parser):
        parser.add_argument('--orig', nargs='+', type=int, help=__doc__)
        parser.add_argument('--dest', nargs='+', type=int)
              
    def handle(self, *args, **options):
        s_err = ""
        try:
            ## recup anne origine
            ## recup année à créer
            anneeOrigine = options["orig"][0]
            anneeDestination = options["dest"][0]
            dateOrig = MyTools.getDateFrom_d_m_y("1/1/%d"%anneeOrigine)
            dateDest =  MyTools.getDateFrom_d_m_y("31/12/%d"%anneeOrigine)
            decalageJours = ((anneeDestination - anneeOrigine)*365)-1
            assert dateDest > dateOrig, "Années d'origine et de destination incohérentes"
            
            for serie in Serie.objects.activesSurPeriode(dateOrig, dateDest):
                dateFabPlants = serie.dateDebutPlants()
                if dateFabPlants:
                    dureeFabPlants_j = (serie.evt_debut.date - dateFabPlants).days
                else:
                    dureeFabPlants_j = 0
    
                serieDest = creationEditionSerie({"id_serie":"0",
                                                  "intra_rang_cm":serie.intra_rang_m*100,
                                                  "nb_rangs":serie.nb_rangs,
                                                  "id_legume":serie.legume_id,
                                                  "nb_pieds":serie.nbPieds(),
                                                  "b_serre":serie.bSerre,
                                                  "date_debut":serie.evt_debut.date + datetime.timedelta(days = decalageJours),
                                                  "duree_fab_plants_j":dureeFabPlants_j,
                                                  "duree_avant_recolte_j":serie.dureeAvantRecolte_j,
                                                  "etalement_recolte_j":serie.etalementRecolte_j
                                                  })

                log.info("%s\nsérie dupliquée : %s\n\n"%(serie.__str__(), serieDest.__str__()))
        except:
            s_err = str(sys.exc_info()[1])
            log.error(s_err)

        log.info("Fin de commande")  
