# -*- coding: utf-8 -*-
'''
Created on Nov 26, 2013

@author: vgazeill
'''

from django.http import HttpResponse

from main.models import Evenement, Plant, Planche, TypeEvenement, Variete
import sys
import datetime
from main import constant

def serveRequest(request):
    """Received a request and return specific response"""

    ## --------------- renvoi de tous les evenements d'un plant
    cde = request.POST.get("cde","")
    print("cde =", cde)
    if cde == "getEvtsPlant": 
        try:
            l_evts = Evenement.objects.filter(plant_base_id = int(request.POST.get("id", 0)))
            s_ = ','.join(['{"id":"%d","nom":"%s","date":"%s","duree":"%d","type":"%s"}'%(   item.id, item.nom, 
                                                                                             item.date.strftime(constant.FORMAT_DATE), item.duree,
                                                                                             item.type) for item in l_evts])           
            s_json = '{"status":"true","l_evts":[%s]}'% s_
        except:
            print(__name__ + ': ' + str(sys.exc_info()[1]) )
            s_json = '{"status":"false","err":%s}'%sys.exc_info()[1]
             
        return HttpResponse( s_json, content_type="application/json")

    ## --------------- renvoi d'un evt
    cde = request.POST.get("cde","")
    print("cde =", cde)
    if cde == "getEvt": 
        try:
            evt = Evenement.objects.get(id = int(request.POST.get("id", 0)))
            s_ = '{"id":"%d","nom":"%s","date":"%s","type":"%s"}'%(evt.id, evt.nom, evt.date.strftime(constant.FORMAT_DATE), evt.type)       
            s_json = '{"status":"true","evt":%s}'% s_
        except:
            print(__name__ + ': ' + str(sys.exc_info()[1]) )
            s_json = '{"status":"false","err":%s}'%sys.exc_info()[1]
             
        return HttpResponse( s_json, content_type="application/json")

    ## --------------- request to update database 
    if cde =='sauve_plant':
        print( __name__, "sauve_plant", request.POST)

        try:
            id_plant = request.POST.get("id_plant")
            if '_' in id_plant:
                plant = Plant() ## un nouveau
            else:
                plant = Plant.objects.get(id=int(id_plant))
     
            plant.variete = Variete.objects.get(id = request.POST.get("variete",""))
            plant.nb_graines = int(request.POST.get("nb_graines",0))
            plant.largeur_cm = int(request.POST.get("largeur_cm",0))
            plant.hauteur_cm = int(request.POST.get("hauteur_cm",0))
            plant.coord_x_cm = int(request.POST.get("coord_x_cm",0))
            plant.coord_y_cm = int(request.POST.get("coord_y_cm",0))
            plant.planche = Planche.objects.get(num=int(request.POST.get("id_planche",0)))
            plant.save()
            s_json = '{"status":"true","id_plant":%d}'%plant.pk
        except:
            s_json = '{"status":"false","err":%s}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")

    
    ## --------------- request to update database 
    if cde == "sauveEvt":
        try:
            id = int(request.POST.get("id",0))
            if id != 0:
                # svg d'un evt deja existant
                evt = Evenement.objects.get(id=id)
            else:
                ## svg d'un nouvel evt
                evt = Evenement()
            evt.nom = request.POST.get("nom","")
            evt.date = datetime.datetime.strptime(request.POST.get("date",""), constant.FORMAT_DATE)
            evt.type = TypeEvenement.objects.get(nom=request.POST.get("type", ""))
            if evt.type == TypeEvenement.objects.get(nom="fin"):
                evt.date = evt.date + datetime.timedelta(hours=20)  ## pour eviter les confusions de debut de jour à 0 h , on finit la journée à 20h 
            evt.plant_base = Plant.objects.get(id=int(request.POST.get("id_plan", 0)))
            evt.date_creation = datetime.datetime.now()
            evt.save()
            print(evt)
                
            s_json = '{"status":"true"}'
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]
           
        return HttpResponse(s_json)

    ## --------------- request to update database 
    if cde == "supprime_evenement":
        try:
            evt = Evenement.objects.get(id=int(request.POST.get("id", 0)))
            print("will delete", evt)
            evt.delete()
            s_json = '{"status":"true"}'
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]
           
        return HttpResponse(s_json)


    print("No action engaged for", request.POST)

    return HttpResponse("No request treated inside serveRequest")
