# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand       

from main import serveRequest
from django.test import TestCase, RequestFactory

   
class Command(BaseCommand):
    """updateDB command"""
    help = "updateDB"

    def handle(self, *args, **options):
        
        self.factory = RequestFactory()

        # Create an instance of a POST request.
        request = self.factory.post('http://localhost:8000/edition_planche/?num_planche=1', data={"cde":"getEvtsPlant",
                                                                                                  "id":"36"
                                                                                                  })

      
        
        serveRequest.serveRequest(request)
        
        
       
        
        
    