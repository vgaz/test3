# -*- coding: utf-8 -*-
'''
Created on 26 févr. 2015

@author: vincent
'''
from django.core.management.base import BaseCommand
from main.models import Evenement
import datetime

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        self.stdout.write(args)

        l_EvtsRecents = Evenement.objects.filter(bFinie=False, date__gt = datetime.date.today())
        
        for evt in l_EvtsRecents:
            msg = "%s" % evt.nom
            self.stdout.write(msg)
            
            
        self.stdout.write(" termine")  
