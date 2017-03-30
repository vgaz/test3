# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand       
from django.test import TestCase, RequestFactory

from maraich import serveRequest, views, constant
import os
from maraich import settings
from maraich.models import *

from UnitTests import testU_Series, testU_ProdSemaine

class Command(BaseCommand):
    help = "test divers"

    def handle(self, *args, **options):

        self.factory = RequestFactory()

        # Create an instance of a POST request.
        request = self.factory.post('/recolte/', 
                                    
                                    data={"periode":"specifique",
                                          "date_debut_vue":"29/5/2017",
                                          "date_fin_vue":"5/6/2017", 
                                          "bSerres":"on"
                    
                                         
                                        }
                                    )
        views.recolte(request)    
        
#         
#         testU_ProdSemaine.testU_ProdSemaine()
#         
#         leg = Legume.objects.get(id=10)
#         testU_Series.testU_sauveSerie()
#         
#         return

#         

        
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

#         self.factory = RequestFactory()
#         
#         # Create an instance of a POST request.   
#         request = self.factory.post('/utilisation_planches/', 
#                                         data={  "periode":"specifique",
#                                                 "date_debut_vue":"22/01/2017",
#                                                 "date_fin_vue":"3/4/2017",
#                                                 "bSerres":"on"                           
#                                                 }
#                                     )        
#         views.utilisationPlanches(request)
#         
#         return
# 
#         
#         serveRequest.serveRequest(request)
    

        date_debut_vue = MyTools.getDateFrom_d_m_y("1/4/2017")
        date_fin_vue = MyTools.getDateFrom_d_m_y("31/7/2017")
#         la_date = MyTools.getDateFrom_d_m_y("14/03/2016")
#         l_implantations = Implantation.objects.filter(planche_id = 2)
#         planche = Planche.objects.get(id=1)
        l_series = Serie.objects.activesSurPeriode(date_debut_vue, date_fin_vue)
        for ser in l_series:
            print (ser)
            pr = ser.prodHebdo(date_debut_vue)
        
        return
    
    
    
    
#     
#         l_series = Serie.objects.activesEnDateDu(la_date, planche)
#         print("séries actives en date du", la_date, l_series.values_list("id",flat=True))
#         print(l_series.values_list("id",flat=True))
#         
#         return 
    
    


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

#         print(help)
        
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

   
        