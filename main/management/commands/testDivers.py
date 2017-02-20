# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand       

from main import serveRequest, views, constant
from django.test import RequestFactory

from main.models import *


class Command(BaseCommand):
    help = "test divers"

    def handle(self, *args, **options):
        
        date_debut = MyTools.getDateFrom_d_m_y("05/09/2016")

#         b1 = respecteRotation(date_debut, 1, 1)
        
        serie = Serie.objects.get(id=79)
        print (serie.descriptif())
        print (serie.prodHebdo(date_debut))
#         date_debut_sem = MyTools.getDateFrom_d_m_y("2/10/2016")
# 
#         serie.prodHebdo(date_debut_sem)
#         
        return
        
#         impl = Implantation.objects.get(id=13)
#         s = impl.surface_m2()
#         print (s)
#         return
#
#         S = 140
#         q = quantitePourSurface(1, S, 3, 0.2)
#         print(q)
#         s = surfacePourQuantite(1, q, 3, 0.2)
#         print (s)
#         return 0
#         
#         self.factory = RequestFactory()
#         
# 
        # Create an instance of a POST request.
        
    
        request = self.factory.post('/chrono_planches/?nom_planches=', 
                                    data={  "cde":"sauve_serie",
                                            "id_serie":0,
                                            "id_variete":1,
                                            "quantite":5,
                                            "nb_rangs":3,
                                            "intra_rang_cm":30,
                                            "simulation":""                            
                                        }
                                    )        
        serveRequest.serveRequest(request)
         
         
         
        return

        date_debut_vue = MyTools.getDateFrom_d_m_y("1/7/2016")
        date_fin_vue = MyTools.getDateFrom_d_m_y("31/7/2016")
        la_date = MyTools.getDateFrom_d_m_y("14/03/2016")
#         l_implantations = Implantation.objects.filter(planche_id = 2)
        planche = Planche.objects.get(id=1)
        l_series = Serie.objects.activesSurPeriode(date_debut_vue, date_fin_vue, planche)
        print(len(l_series))
        for pl in l_series:
            print (pl)
        
        return
        l_series = Serie.objects.activesEnDateDu(la_date, planche)
        print("séries actives en date du", la_date, l_series.values_list("id",flat=True))
        
        return 
    
        print(l_series.values_list("id",flat=True))
        
        
        return
#         date_debut_vue = datetime.datetime.strptime("18/5/2015", constant.FORMAT_DATE)
#         date_fin_vue = datetime.datetime.strptime("24/5/2015", constant.FORMAT_DATE) + delta20h
# 
#         planification.planif(date_debut_vue, date_fin_vue)
#         return
#         laPlanche = Planche.objects.get(id=11)
#         print( Serie.objects.surPlancheDansPeriode(laPlanche.id, date_debut_vue,date_fin_vue))
# 
#         laPlanche = Planche.objects.get(id=1)
#         print( Serie.objects.surPlancheDansPeriode(laPlanche.id, date_debut_vue,date_fin_vue))

        return

        
#         id_serie = 3
# #         reste  = essaiDeplacementSeries(id_plant, 3, 60, 2)
#         serie = Serie.objects.get(id=id_serie)
#         serie2 = cloneSerie(serie)
#         print (serie2)
#         return 
#     
#         ## maj quantités
#         plant2.quantite = plant.quantite - reste 
#         plant2.save()
#         plant.quantite = reste
#         plant.save()

        print(help)
        
        self.factory = RequestFactory()

        # Create an instance of a POST request.
        request = self.factory.post('/suivi_implantations/', 
                                    data={"editSerie_id":"0",
                                          "editSerie_num_planche":"12",
                                          "editSerie_id_variete":"6", 
                                          "editSerie_quantite":"343", 
                                          "editSerie_intra_rang_cm":"20", 
                                          "editSerie_nb_rangs":"5", 
                                          "editSerie_date_debut":"3/2/2016", 
                                          "editSerie_date_fin":"12/6/2016"
                                         
                                        }
                                    )
        views.chronoPlanches(request)
#         serveRequest.serveRequest(request)

   
        