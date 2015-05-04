# -*- coding: utf-8 -*-
import datetime

from main.models import Planche, Prevision, Production, PlantBase, Variete
from main import constant

#################################################

def planif(dateDebut, dateFin):
    
    ## on balaye semaine par semaine
    print(__name__)
    dateSemaine = dateDebut
    while dateSemaine <= dateFin:
        
        ## 1 récupération des productions demandées
        for prev in Prevision.objects.filter(date_semaine = dateSemaine):
            print("planif prev", prev)
            
            ## 2 test si dispo en tout ou partie sur production actuelle
            try:
                prod = Production.objects.get(date_semaine = dateSemaine, variete_id = prev.variete_id)
            except:
                prod = Production()
                prod.variete_id = prev.variete_id
                prod.date_semaine = dateSemaine
                self.stdout.write("production crée")
                
            ## 3 déduction de tout ou partie de la quantité demandée
            reste = prod.qte - prod.qte_bloquee - prev.qte 
            self.stdout.write("reste", reste)
            if reste >= 0:
                prod.qte_bloquee = reste
                break ## on a assez donc on bloque et on passe à la variété suivante
            else:
                self.stdout.write("création de plants supplémentaires pour répondre au besoin de production")
                plant = PlantBase()
                var = Variete.objects.get(id = prev.variete_id)
                plant.variete = var
                ## on calcule la quantité de plants ou de graines nécessaires en fonction de la masse escomptée
                plant.calculeNbPlantSemis(reste)
                ## on calcule la surface nécessaire pour produire
                plant.calculeEncombrement()

                plant.planche = Planche.objects.get(num=0) ## placement en planche virtuelle en attente de placement réel 
                plant.save()
                
                prod.qte = prev.qte
                prod.qte_bloquee = prod.qte
                prod.save()
                
        dateSemaine += datetime.timedelta(days=7)
    
