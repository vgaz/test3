# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand       

from main import serveRequest, views, constant
from django.test import RequestFactory

from main.models import Serie, essaiDeplacementSeries, cloneSerie, Evenement, creationPlanche,\
    Planche,Implantation
from main.Tools import MyTools


class Command(BaseCommand):
    help = "test divers"

    def handle(self, *args, **options):
        
#         creationPlanche(10000, 100, False, "Planche Virtuelle", constant.PLANCHE_VIRTUELLE_NUM)

#         from main import planification
# 
#         delta20h = datetime.timedelta(hours=20)
<<<<<<< HEAD
        date_debut_vue = MyTools.getDateFrom_d_m_y("1/1/2016")
        date_fin_vue = MyTools.getDateFrom_d_m_y("1/8/2016")
        la_date = MyTools.getDateFrom_d_m_y("1/8/2016")
        l_implantations = Implantation.objects.filter(planche_id = 2)

    
        l_series = Serie.objects.filter(evt_debut__date__lte = la_date,
                                        evt_fin__date__gte = la_date,
                                        implantations__id__in = l_implantations).values_list("id",flat=True)
        print(l_series)
        return
=======
#         date_debut_vue = datetime.datetime.strptime("18/5/2015", constant.FORMAT_DATE)
#         date_fin_vue = datetime.datetime.strptime("24/5/2015", constant.FORMAT_DATE) + delta20h
>>>>>>> refs/remotes/remote_origin/dev
# 
#         planification.planif(date_debut_vue, date_fin_vue)
#         return
<<<<<<< HEAD
#         laPlanche = Planche.objects.get(id=11)
#         print( Serie.objects.surPlancheDansPeriode(laPlanche.id, date_debut_vue,date_fin_vue))
# 
#         laPlanche = Planche.objects.get(id=1)
#         print( Serie.objects.surPlancheDansPeriode(laPlanche.id, date_debut_vue,date_fin_vue))

        return
=======
        
>>>>>>> refs/remotes/remote_origin/dev
        id_serie = 3
#         reste  = essaiDeplacementSeries(id_plant, 3, 60, 2)
        serie = Serie.objects.get(id=id_serie)
        serie2 = cloneSerie(serie)
        print (serie2)
        return 
    
#         ## maj quantités
#         plant2.quantite = plant.quantite - reste 
#         plant2.save()
#         plant.quantite = reste
#         plant.save()

        print(help)
        
        self.factory = RequestFactory()

        # Create an instance of a POST request.
        request = self.factory.post('/chrono_planches/?num_planches=', 
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
        