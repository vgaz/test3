# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand       
from django.test import RequestFactory

from maraich import serveRequest, views
import os
from maraich import settings
from maraich.models import *
import MyHttpTools


def     testViewImplantations():
        # Create an instance of a POST request.
        factory = RequestFactory()       
        request = factory.post('/suiviImplantations/',      
                                     data=        {'decalage_j':'30', 
                                                 'date_debut_vue': '01/04/2017', 
                                                 'serres': 'on', 
                                                 'date_fin_vue': '01/05/2017', 
                                                 's_filtre_legume': 'aub', 
                                                 's_filtre_planches': 'Vir', 
                                                 'periode': 'mois'}
                                     )
        views.suiviImplantations(request)

def     testdonnePeriodeVue():
        # Create an instance of a POST request.
        factory = RequestFactory()       
        request = factory.post('/suiviImplantations/',      
                                     data=        {'decalage_j':'7', 
                                                 'date_debut_vue': '01/04/2017', 
                                                 'date_fin_vue': '01/05/2017', 
                                                 'serres': 'on', 
                                                 'direction': 'recul',
                                                 's_filtre_legume': 'aub', 
                                                 's_filtre_planches': 'Vir', 
                                                 'periode': 'mois'}
                                     )
        views.donnePeriodeVue(request.POST)


class Command(BaseCommand):
    help = "test divers"

    def handle(self, *args, **options):


        testdonnePeriodeVue()
        return
    
        testViewImplantations()
        return
    

#         ser = Serie.objects.get(pk=15)
#         qt = ser.quantiteEstimee_kg_ou_piece()
#         ss = ser.quantiteEstimee_kg_ou_piece()
#         print (ser.descriptif())
#         prod =  ser.prodHebdo(MyTools.getDateFrom_d_m_y("15/10/2017"), 2)
#         print(prod)
#         return
 
#         ## Create an instance of a POST request.
#         factory = RequestFactory()       
#         request = factory.post('/suiviPlants/',      
#                                 data={"periode":"specifique",
#                                        "date_debut_vue":"08/05/2017",
#                                        "date_fin_vue":"29/05/2017", 
#                                     }
#                                 )
#         views.suiviPlants(request)
#         return
#      

        # Create an instance of a POST request.
        factory = RequestFactory()       
        request = factory.post('/evenementsPlanches/',      
                                     data={"periode":"specifique",
                                           "date_debut_vue":"20/4/2017",
                                           "date_fin_vue":"20/4/2017", 
                                           "periode":"aujourdhui"
 
                                         }
                                     )
        views.evenementsPlanches(request)
        
# 
#  
#         # Create an instance of a POST request.
#         factory = RequestFactory()       
#         request = factory.post('/recolte/',      
#                                      data={"periode":"specifique",
#                                            "date_debut_vue":"8/05/2017",
#                                            "date_fin_vue":"29/5/2017", 
#                                            "bSerres":"on",
#                                            "s_filtre_espece":"car"
#  
#                                          }
#                                      )
#         views.recolte(request)
#         
         
#         return
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


#         print(Evenement.objects.get(id=7654).__str__())
# 
#         self.factory = RequestFactory()
#         d0 = { 'b_serre': 'false', 
#                 'cde': 'sauve_serie', 
#                 'etalement_recolte_j': '9', 
#                 'date_debut': '08/05/2017', 
#                 'nb_pieds': '1234', 
#                 'intra_rang_cm': '5', 
#                 'nb_rangs': '4', 
#                 'id_legume': '16', 
#                 'duree_avant_recolte_j': '19', 
#                 'id_serie': '17'}
#          
#          
#          
#         d1 = {'duree_avant_recolte_j': '100', 
#               'etalement_recolte_j': '6', 
#               'date_debut': '3/3', 
#               'intra_rang_cm': '15', 
#               'id_serie': '0',
#               'nb_rangs': '2', 
#               'id_legume': '6', 
#               'b_serre': 'off', 
#               'cde': 'sauve_serie'
#               } 
#          
#         _d2={   'duree_j': '1', 
#                 'delta_j': '-19', 
#                 'id': '7654', 
#                 'cde': 'sauve_evt', 
#                 'date': '', 
#                 'nom': 'semi motte blette verte à carde blanche 2', 
#                 'id_serie':'8'                          
#                 }
#         # Create an instance of a POST request.   
#         request = self.factory.post('/serveRequest/', data=d0 )        
#          
#  
# 
#         serveRequest.serveRequest(request)
# 
#         return
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

#         date_debut_vue = MyTools.getDateFrom_d_m_y("1/4/2017")
#         date_fin_vue = MyTools.getDateFrom_d_m_y("11/4/2017")
#         la_date = MyTools.getDateFrom_d_m_y("14/03/2016")
#         l_implantations = Implantation.objects.filter(planche_id = 2)
#         planche = Planche.objects.get(id=1)
#         l_series = Serie.objects.activesSurPeriode(date_debut_vue, date_fin_vue)
#         for ser in l_series:
#             print (ser)
#             pr = ser.prodHebdo(date_debut_vue)
#         
#         return
    
    
    
    
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

   
        