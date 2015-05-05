# -*- coding: utf-8 -*-
import datetime

from main.models import Planche, Prevision, Production, SeriePlants, Variete
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
                print("production crée")
                
            ## 3 déduction de tout ou partie de la quantité demandée
            reste = prod.qte - prod.qte_bloquee - prev.qte 
            print ("reste", reste)
            if reste >= 0:
                prod.qte_bloquee = reste
                break ## on a assez donc on bloque et on passe à la variété suivante
            else:
                print("création de plants supplémentaires pour répondre au besoin de production")
                var = Variete.objects.get(id = prev.variete_id)
                nb_plants_a_installer = var.plantsPourProdHebdo(abs(reste))
                print ("nb plants a installer", nb_plants_a_installer)
                seriePlants = SeriePlants(prev.variete_id, nb_plants_a_installer)
                ## on calcule la quantité de plants ou de graines nécessaires en fonction de la masse escomptée
                
                seriePlants.planche_id = 0 ## placement en planche virtuelle en attente de placement réel 
                seriePlants.save()
                
                prod.qte = prev.qte
                prod.qte_bloquee = prod.qte
                prod.save()
                
        dateSemaine += datetime.timedelta(days=7)
    
