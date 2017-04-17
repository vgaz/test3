# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand       

from maraich import serveRequest
from django.test import TestCase, RequestFactory

from maraich.models import Evenement, Serie, Planche
from maraich import constant
import datetime
import MyTools

class Command(BaseCommand):
    help = "test evt"

    def handle(self, *args, **options):
        
        from maraich import planification

        delta20h = datetime.timedelta(hours=20)
        date_debut_vue = "18/5/2015")
        date_fin_vue = MyTools.getDateFrom_d_m_y("24/5/2015" + delta20h

        planification.planif(date_debut_vue, date_fin_vue)
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
#         l_objs = Serie.objects.all()
#         for evt in l_objs:
#             print (evt)         
#         
#         l_objs = Evenement.objects.filter(serie_id = int(request.POST.get("id", 0)))
#         for evt in l_objs:
#             print (evt)
        serveRequest.serveRequest(request)
        