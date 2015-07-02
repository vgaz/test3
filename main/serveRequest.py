# -*- coding: utf-8 -*-
'''
Created on Nov 26, 2013

@author: vgazeill
'''

from django.http import HttpResponse

from main.models import Evenement, Plant, Planche, Production
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
            for evt in l_evts:
                print (evt)
            
            s_ = ','.join(['{"id":"%d","nom":"%s","date":"%s","duree_j":"%d","type":"%s"}'%( item.id, item.nom, 
                                                                                             item.date.strftime(constant.FORMAT_DATE), item.duree_j, item.type) 
                                                                                                for item in l_evts])           
            s_json = '{"status":"true","l_evts":[%s]}'% s_
        except:
            print(__name__ + ': ' + str(sys.exc_info()[1]) )
            s_json = '{"status":"false","err":"%s"}'%(sys.exc_info()[1])
             
        return HttpResponse(s_json, content_type="application/json")

    ## --------------- renvoi d'un evt
    if cde == "getEvt": 
        try:
            evt = Evenement.objects.get(id = int(request.POST.get("id", 0)))
            s_ = '{"id":"%d","nom":"%s","date":"%s","duree_j":"%s","type":"%s"}'%(evt.id, evt.nom, evt.date.strftime(constant.FORMAT_DATE), evt.duree_j, evt.type)       
            s_json = '{"status":"true","evt":%s}'% s_
        except:
            print(__name__ + ': ' + str(sys.exc_info()[1]) )
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]
             
        return HttpResponse( s_json, content_type="application/json")

    ## --------------- request to update database 
    if cde =='sauve_plant':
        try:
            id_plant = request.POST.get("id_plant")
            if '_' in id_plant:
                plant = Plant() ## un nouveau
            else:
                plant = Plant.objects.get(id=int(id_plant))
     
            plant.variete_id = request.POST.get("variete", 0)
            plant.largeur_cm = int(request.POST.get("largeur_cm",0))
            plant.hauteur_cm = int(request.POST.get("hauteur_cm",0))
            plant.coord_x_cm = int(request.POST.get("coord_x_cm",0))
            plant.coord_y_cm = int(request.POST.get("coord_y_cm",0))
            plant.planche = Planche.objects.get(num=int(request.POST.get("id_planche",0)))
            plant.production_id = 0
            plant.quatite = 1
            plant.save()
            s_json = '{"status":"true","id_plant":%d}'%plant.pk
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")

    
    ## --------------- request to update database 
    if cde == 'supprime_plant':
        try:
            id_plant = request.POST.get("id", "_")
            if '_' in id_plant:
                print("return _")
                raise(Exception, "_ in id plant")
            
            id_plant = int(id_plant)
            plant = Plant.objects.get(id=id_plant)
            
            ## suppression de la production associée
            try:
                prod = None
                prod = Production.objects.get(id = plant.production_id)
                prod.delete()##@todo: erreur il faut retrancher de la seule production de ces plants 
            except:
                pass    

            ## supression des évenements associés
            for obj in Evenement.objects.filter(plant_base_id = plant.id):
                print ("Suppression ", obj)
                obj.delete()
             
            plant.delete()                
            print ("Suppression plant", id_plant)
         
            s_json = '{"status":"true","id_plant":%d}'%id_plant
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")

    
    ## --------------- request to update database 
    if cde == "sauveEvt":
        try:
            e_id = int(request.POST.get("id",0))
            print (request.POST )
            e_type = int(request.POST.get("type", ""))
            date = datetime.datetime.strptime(request.POST.get("date",""), constant.FORMAT_DATE)
            print (date)
            duree_j = int(request.POST.get("duree_j", 1))
            plant_id = int(request.POST.get("id_plant", 0))
            nom = request.POST.get("nom","")

            if e_id == 0:
                ## svg d'un nouvel evt
                evt = Evenement()
            else:
                # maj d'un evt deja existant
                evt = Evenement.objects.get(id=e_id)
                
            evt.type = e_type
            evt.plant_base_id = plant_id
            evt.date = date
            evt.duree_j = 1
            evt.nom = nom
            
            if evt.type == Evenement.TYPE_FIN and "00:00:00" in evt.date:
                print("date +20h")
                evt.date = evt.date + datetime.datetime.timedelta(hours=20)  ## pour eviter les confusions de debut de jour à 0 h , on finit la journée à 20h 
            
            print(evt)
            evt.save()
            print(evt)
                
            s_json = '{"status":"true"}'
        except:
            s_json = '{"status":"false","err":"%s %s"}'%(__name__, sys.exc_info()[1])
           
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


