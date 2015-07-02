# -*- coding: utf-8 -*-
import datetime
from main.models import Evenement, Production, Planche, Plant, Variete

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
<<<<<<< HEAD
#                 if qte == 0: ## issu d'un enregistrement ayant précédement une masse différente de zéro
#                     obj.delete()
#                 else:
                obj.qte_dde = qte
                obj.save()
                    
                    
=======
                if qte == 0 and obj.qte_prod == 0: ## issu d'un enregistrement ayant précédement une masse différente de zéro mais sans engagement de production
                    obj.delete()
                else:
                    obj.qte_dde = qte
                    obj.save()

>>>>>>> refs/remotes/github_test3/dev
def planif(dateDebut, dateFin):
    
    ## on balaye semaine par semaine
    dateSemaine = dateDebut
    while dateSemaine <= dateFin:
        print("\nplanification semaine du %s"%dateSemaine)
        ## 1 récupération des productions demandées
        l_prods = Production.objects.filter(date_semaine = dateSemaine)
        for prod in l_prods:
            ## recup de la variete pour cette semaine
            var = Variete.objects.get(id = prod.variete_id)
            print("\n%s"%var.nom)
            reste = prod.qte_prod - prod.qte_dde 
            if reste >= 0:
                ## on a assez,  on passe à la variété suivante
                print ("Dde = %d; prod = %d, ok"%(prod.qte_dde,  prod.qte_prod) )
                continue
            
            ## on rajoute des plants
            nb_plants_a_installer = var.plantsPourProdHebdo(abs(reste))
            print ("Besoin de %d nouveaux plants"%(nb_plants_a_installer))
            plants = Plant()
            plants.variete_id = var.id
            plants.quantite = nb_plants_a_installer                
            plants.planche = Planche.objects.get(num = 0)           ## placement en planche virtuelle en attente de placement réel 
            plants.production_id = prod.id
            plants.hauteur_cm = var.diametre_cm                     ## on fixe arbitrairement sur une ligne
            plants.largeur_cm = var.diametre_cm * nb_plants_a_installer
            plants.save()
            print( "nouvelle serie " + str(plants))
            
            print ("crea evt : ", Evenement.TYPE_DEBUT, dateSemaine, var.duree_avant_recolte_j, plants.id, "début plant " + var.nom)
            e = Evenement()
            e.type = Evenement.TYPE_DEBUT
            e.date = dateSemaine
            e.plant_base_id = plants.id
            e.nom = "début plant " + var.nom
            e.save()
            
            e = Evenement()
            e.type = Evenement.TYPE_FIN
            e.date = dateSemaine + datetime.timedelta(days = var.duree_avant_recolte_j)
            e.plant_base_id = plants.id
            e.nom = "fin plant " + var.nom
            e.save()

            ## maj prod de cette semaine pour cette variété
            l_prodSemaine = var.prodSemaines(nb_plants_a_installer)
<<<<<<< HEAD
            print(l_prodSemaine)
=======
            ##print(l_prodSemaine)
>>>>>>> refs/remotes/github_test3/dev
            ## maj pour cette semaine
            prod.qte_prod += l_prodSemaine[0]
            print ("prod %s sem %s  %d/%d"%(prod.variete_id, dateSemaine, prod.qte_dde, prod.qte_prod))
            prod.save()
            
            ## maj éventuelle des semaines suivantes
            if len(l_prodSemaine) > 1:  
                for index, qteSem in enumerate(l_prodSemaine[1:]):
<<<<<<< HEAD
                    dateSem = dateDebut + datetime.timedelta(weeks = 1 + index)
=======
                    dateSem = dateSemaine + datetime.timedelta(weeks = 1 + index)
>>>>>>> refs/remotes/github_test3/dev
                    prod_suite = Production.objects.get_or_create(variete_id = var.id, date_semaine = dateSem)[0]
                    print (prod_suite)
                    prod_suite.qte_prod += qteSem
                    prod_suite.save()
                    print(prod_suite)


        dateSemaine += datetime.timedelta(days=7)
    
