# -*- coding: utf-8 -*-
import csv
import datetime, os

from django.core.management.base import BaseCommand
from maraich.models import Planche
from maraich.settings import log
from maraich import settings, constant



class Command(BaseCommand):
    """mise à jour des surfaces totales de planches"""
          
            
    def handle(self, *args, **options):
        l_err  = []
        totalSerre_m2 = 0
        totalChamp_m2 = 0
        
        for pl in Planche.objects.exclude(nom__in=[constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP,
                                                   constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS]):
            if pl.bSerre:
                totalSerre_m2 += pl.surface_m2()
            else:
                totalChamp_m2 += pl.surface_m2()
        
        Planche.objects.get(nom=constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP).longueur_m = totalChamp_m2 
        Planche.objects.get(nom=constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS).longueur_m = totalSerre_m2

        log.info("Fin de comande %s\n nombre d'erreurs = %d\n%s"%(self.__doc__,
                                                                len(l_err), 
                                                                "\n".join(l_err)))  
