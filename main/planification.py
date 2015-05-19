# -*- coding: utf-8 -*-
import datetime
from main.models import Evenement, Production, Planche, Plant, TypeEvenement, Variete

#################################################

def enregistrePrevisions(request):
    if request.POST:
        for k, v in request.POST.items():
            ## gestion prévisions de récoltes
            if k.startswith("p__") and v:
                _, ds, var = k.split("__")
                try:
                    obj = Production.objects.get(variete_id=var, date_semaine = ds)
                except:
                    obj=Production()
                    obj.variete_id = var
                    obj.date_semaine = ds
                qte = int(v.split(" ")[0])
#                 if qte == 0: ## issu d'un enregistrement ayant précédement une masse différente de zéro
#                     obj.delete()
#                 else:
                obj.qte_dde = qte
                obj.save()
                    
                    
def planif(dateDebut, dateFin):
    
    ## on balaye semaine par semaine
    dateSemaine = dateDebut
    while dateSemaine <= dateFin:
        print("\nplanification semaine du %s"%dateSemaine)
        ## 1 récupération des productions demandées
        l_prods = Production.objects.filter(date_semaine = dateSemaine)
        for prod in l_prods:
            
            var = Variete.objects.get(id = prod.variete_id)
            print ("\n%s"%var.nom)
            reste = prod.qte_prod - prod.qte_dde 
            if reste >= 0:
                pass
                pass
                ## on a assez,  on passe à la variété suivante
                print ("Dde = %d; prod= %d, ok"%(prod.qte_dde,  prod.qte_prod) )
                break
            ## on rajoute des plants
            nb_plants_a_installer = var.plantsPourProdHebdo(abs(reste))
            print ("Besoin de %d nouveaux plants"%(nb_plants_a_installer))
            plants = Plant(var.id, nb_plants_a_installer)                
            plants.planche = Planche.objects.get(num = 0)           ## placement en planche virtuelle en attente de placement réel 
            plants.production_id = prod.id
            plants.hauteur_cm = var.diametre_cm                     ## on fixe arbitrairement sur une ligne
            plants.largeur_cm = var.diametre_cm * nb_plants_a_installer
            plants.save()
            print(plants)
            
            ## maj prod de cette semaine pour cette variété
            l_prodSemaine = var.prodSemaines(nb_plants_a_installer)
            print(l_prodSemaine)
            ## maj pour cette semaine
            prod.qte_prod += l_prodSemaine[0]
            print ("prod %s sem %s  %d/%d"%(prod.variete_id, dateSemaine, prod.qte_dde, prod.qte_prod))
            prod.save()
            
            ## maj éventuelle des semaines suivantes
            if len(l_prodSemaine) > 1:  
                for index, qteSem in enumerate(l_prodSemaine[1:]):
                    dateSem = dateDebut + datetime.timedelta(weeks = 1 + index)
                    prod_suite = Production.objects.get_or_create(variete_id = var.id, date_semaine = dateSem)[0]
                    print (prod_suite)
                    prod_suite.qte_prod += qteSem
                    prod_suite.save()
                    print(prod_suite)

            evt = Evenement()
            evt.type = TypeEvenement.objects.get(nom="debut")
            evt.plant_base = plants
            evt.date = dateSemaine
            evt.duree = var.duree_avant_recolte_j
            evt.nom = "plant " + var.nom
            evt.save()

        dateSemaine += datetime.timedelta(days=7)
    
