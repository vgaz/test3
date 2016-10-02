# -*- coding: utf-8 -*-
import datetime
from main.models import Production, Planche, Serie, Variete
import main.Tools.MyTools as MyTools
from main import models

#################################################

def enregistrePrevisions(request):
    if not request.POST:
        return
    
    for k, v in request.POST.items():
        ## gestion prévisions de récoltes
        if not k.startswith("p__") or not v:
            continue
        try:
            _, s_ds, var = k.split("__")
            ds = MyTools.getDateFrom_y_m_d(s_ds)
            obj = Production.objects.get(variete_id=var, date_semaine = ds)
        except:
            obj=Production()
            obj.variete_id = var
            obj.date_semaine = ds

        obj.qte_dde = int(v.split(" ")[0])
        if obj.qte_dde == 0 and obj.qte_prod == 0: ## issu d'un enregistrement ayant précédement une masse différente de zéro mais sans engagement de production
            obj.delete()
        else:
            obj.save()
            print("ds3", obj.date_semaine)


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
                ## on a assez, on passe à la variété suivante
                print ("Dde = %d; prod = %d, ok"%(prod.qte_dde,  prod.qte_prod) )
                continue
            
            ## on rajoute une série de plants
            nb_plants_a_installer = var.plantsPourProdHebdo(abs(reste))
            print ("Besoin de %d nouveaux plants"%(nb_plants_a_installer))
            serie = models.creationEditionSerie(  0,
                                                  var.id,
                                                  None,
                                                  nb_plants_a_installer, 
                                                  var.intra_rang_m, 
                                                  1, 
                                                  dateSemaine)

            serie.production_id = prod.id
            serie.save()
            
            ## maj prod de cette semaine pour cette variété
            l_prodSemaine = var.prodSemaines(nb_plants_a_installer)

            ##print(l_prodSemaine)
            ## maj pour cette semaine
            prod.qte_prod += l_prodSemaine[0]
            print ("prod %s sem %s  %d/%d"%(prod.variete_id, dateSemaine, prod.qte_dde, prod.qte_prod))
            prod.save()
            
            ## maj éventuelle des semaines suivantes
#             if len(l_prodSemaine) > 1:  
            for index, qteSem in enumerate(l_prodSemaine[1:]):
                dateSem = dateSemaine + datetime.timedelta(weeks = 1 + index)
                prod_suite = Production.objects.get_or_create(variete_id = var.id, date_semaine = dateSem)[0]
                print (prod_suite)
                prod_suite.qte_prod += qteSem
                prod_suite.save()
                print(prod_suite)


        dateSemaine += datetime.timedelta(days=7)
    
