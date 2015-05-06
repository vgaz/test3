# -*- coding: utf-8 -*-
import datetime

from main.models import Evenement, Prevision, Production, Plant, TypeEvenement, Variete

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
                print("Nelle production")
                
            ## 3 déduction de tout ou partie de la quantité demandée
            reste = prod.qte - prev.qte 
            print ("reste", reste)
            if reste >= 0:
                ## on a assez ,  on passe à la variété suivante
                break 
            else:
                print("création de plants supplémentaires pour répondre au besoin de production")
                var = Variete.objects.get(id = prev.variete_id)
                nb_plants_a_installer = var.plantsPourProdHebdo(abs(reste))
                print ("Nb plants à installer", nb_plants_a_installer)

                ## on ajoute la qté nouvelle à la production
                prod.qte += abs(reste)  
                prod.save()
                      
                print(prod)          
                plants = Plant(prev.variete_id, nb_plants_a_installer)                
                plants.planche_id = 0 ## placement en planche virtuelle en attente de placement réel 
                plants.productionHebdo_id = prod.id
                print(plants.planche_id)
                print(plants.productionHebdo_id)
                print(plants.variete_id)
                print(plants.quantite)
                plants.save()
                print(plants)
                
                evt = Evenement()
                evt.type = TypeEvenement.objects.get(nom="debut")
                evt.plant_base = plants
                evt.date = dateSemaine
                evt.duree = var.duree_avant_recolte_j
                evt.nom = "plant " + var.nom

        dateSemaine += datetime.timedelta(days=7)
    
