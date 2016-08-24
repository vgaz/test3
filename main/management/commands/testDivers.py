# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand       

from main import serveRequest, views, constant
from django.test import RequestFactory

from main.models import *
from main.Tools import MyTools


class Command(BaseCommand):
    help = "test divers"

    def handle(self, *args, **options):
        
        self.factory = RequestFactory()

        # Create an instance of a POST request.
        request = self.factory.post('/chrono_planches/?nom_planches=', 
                                    data={"id":"12",
                                          "cde":"get_evts_serie"
                                        }
                                    )        
        serveRequest.serveRequest(request)
        return
    
    
        for e in  Evenement.objects.all():
            print (e)
        return
        date_debut_vue = MyTools.getDateFrom_d_m_y("1/1/2016")
        date_fin_vue = MyTools.getDateFrom_d_m_y("1/9/2016")
        la_date = MyTools.getDateFrom_d_m_y("14/03/2016")
#         l_implantations = Implantation.objects.filter(planche_id = 2)
        planche = Planche.objects.get(id=1)
        
        l_series = Serie.objects.activesEnDateDu(la_date, planche)
        print("séries actives en date du", la_date, l_series.values_list("id",flat=True))
        
        return 
    
        l_series = Serie.objects.activesSurPeriode(date_debut_vue, date_fin_vue, planche)
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
        request = self.factory.post('/chrono_planches/?nom_planches=', 
                                    data={"editSerie_id":"0",
                                          "editSerie_num_planche":"12",
                                          "editSerie_id_variete":"6", 
                                          "editSerie_quantite":"343", 
                                          "editSerie_intra_rang_cm":"20", 
                                          "editSerie_nb_rangs":"5", 
                                          "editSerie_date_debut":"3/2/2016", 
                                          "editSerie_date_fin":"12/6/2016",
                                          "evt_date[]":"12/4/2016",
                                          "evt_type[]":Evenement.TYPE_DIVERS,
                                          "evt_nom[]":"taille",
                                          "evt_date[]":"15/4/2016",
                                          "evt_type[]":Evenement.TYPE_DIVERS,
                                          "evt_nom[]":"action2"
                                        }
                                    )
        views.chronoPlanches(request)
#         serveRequest.serveRequest(request)

    