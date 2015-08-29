# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand       

from main import serveRequest
from django.test import RequestFactory

from main.models import Plant, essai_deplacement_plants, clonePlant


class Command(BaseCommand):
    help = "test divers"

    def handle(self, *args, **options):
        
#         from main import planification
# 
#         delta20h = datetime.timedelta(hours=20)
#         date_debut_vue = datetime.datetime.strptime("18/5/2015", constant.FORMAT_DATE)
#         date_fin_vue = datetime.datetime.strptime("24/5/2015", constant.FORMAT_DATE) + delta20h
# 
#         planification.planif(date_debut_vue, date_fin_vue)
#         return
        
        id_plant = 1
        reste  = essai_deplacement_plants(id_plant, 3, 60, 2)
        plant = Plant.objects.get(id=id_plant)
        plant2 = clonePlant(plant)
        ## maj quantités
        plant2.quantite = plant.quantite - reste 
        plant2.save()
        plant.quantite = reste
        plant.save()
        return
        self.factory = RequestFactory()

        # Create an instance of a POST request.
        request = self.factory.post('http://localhost:8000/edition_planche/?num_planche=1', data={"cde":"getEvtsPlant", "id":"36"
                                                                                                  })
#         
#         evt =  Evenement(2, datetime.datetime.strptime("24/4/2015", constant.FORMAT_DATE), 5, 36)
# 
#         l_objs = Planche.objects.all()
#        
#         l_objs = Plant.objects.all()
#         for evt in l_objs:
#             print (evt)         
#         
#         l_objs = Evenement.objects.filter(plant_base_id = int(request.POST.get("id", 0)))
#         for evt in l_objs:
#             print (evt)
        serveRequest.serveRequest(request)
        