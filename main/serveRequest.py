# -*- coding: utf-8 -*-
'''
Created on Nov 26, 2013

@author: vgazeill
'''

from django.http import HttpResponse

from main.models import Evenement, Plant, Planche, Production
from main.models import creationPlanche, creationSerie, essai_deplacement_plants, clonePlant
import sys, traceback
import datetime
from main import constant

def serveRequest(request):
    """Received a request and return specific response"""
    rep = ""
    ## --------------- renvoi de tous les evenements d'un plant
    cde = request.POST.get("cde","")
    print(request.POST)#
    
    if cde == "getEvtsPlant": 
        ## retour des évenements des plants (sauf debut et fin déjà affichés spécifiquement)
        try:
            l_evts = Evenement.objects.filter(plant_base_id = int(request.POST.get("id", 0)),
                                              type = Evenement.TYPE_DIVERS)       
            s_ = ','.join(['{"id":"%d","nom":"%s","date":"%s","duree_j":"%d","type":"%s"}'%( item.id, item.nom, 
                                                                                             item.date.strftime(constant.FORMAT_DATE), item.duree_j, item.type) 
                                                                                                for item in l_evts])           
            s_json = '{"status":"true","l_evts":[%s]}'% s_
        except:
            print(__name__ + ': ' + str(sys.exc_info()[1]) )
            traceback.print_tb(sys.exc_info())
            s_json = '{"status":"false","err":"%s"}'%(sys.exc_info()[1])
             
        return HttpResponse(s_json, content_type="application/json")

    ## --------------- renvoi d'un evt à partir de son identifiant
    if cde == "getEvt": 
        try:
            evt = Evenement.objects.get(id = int(request.POST.get("id", 0)))
            s_ = '{"id":"%d","nom":"%s","date":"%s","duree_j":"%s","type":"%s"}'%(evt.id, evt.nom, evt.date.strftime(constant.FORMAT_DATE), evt.duree_j, evt.type)       
            s_json = '{"status":"true","evt":%s}'% s_
        except:
            traceback.print_tb(sys.exc_info())
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]
             
        return HttpResponse( s_json, content_type="application/json")

    ## --------------- creation ou maj serie de plants 
    if cde =='sauve_plant':
        try:
            print (request.POST)
            id_plant = request.POST.get("id_pl#ant")
            if '_' in id_plant:
                plant = Plant() ## un nouveau
            else:
                plant = Plant.objects.get(id=int(id_plant)) ## un déjà créé
     
            plant.variete_id = request.POST.get("variete", 0)
            plant.quantite = int(request.POST.get("quantite", 0))
            plant.largeur_cm = int(request.POST.get("largeur_cm",0))
            plant.hauteur_cm = int(request.POST.get("hauteur_cm",0))
            plant.intra_rang_cm = int(request.POST.get("intra_rang_cm",0))
            plant.nb_rangs = int(request.POST.get("nb_rangs", 0))
            plant.planche = Planche.objects.get(num=int(request.POST.get("id_planche",0)))
            plant.production_id = 0
            plant.quatite = 1
            plant.save()
            plant.fixeDates(MyTools.getDateFrom_d_m_y(request.POST.get("date_debut")), 
                            None or request.POST.get("date_fin", ""))
            print(plant)
            s_json = '{"status":"true","id_plant":%d}'%plant.pk
        except:#
            ex_type, ex, tb = sys.exc_info()
            print (ex_type, ex)
            traceback.print_tb(tb)
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")

    
    if cde == 'supprime_serie':
        try:
            id_plant = int(request.POST.get("id", 0))
            if id_plant == 0:
                print("return _")
                raise(Exception, "série non supprimable")
            
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

    if cde == 'supprime_planche':
        try:
            id_pl = int(request.POST.get("id"))
            if id_pl == 1:
                raise ValueError("Refus de suppression. La planche virtuelle ne peut être détruite")
            
            planche = Planche.objects.get(id=id_pl)
            planche.delete()

            ## suppression des series de plants associés
                ## suppression de la production associée
                ## supression des évenements associés à une serie de plants

            s_json = '{"status":"true","id_planche":%d}'%id_pl
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
            evt.save()
            print(evt)
                
            s_json = '{"status":"true"}'
        except:
            traceback.print_tb(sys.exc_info())            
            s_json = '{"status":"false","err":"%s %s"}'%(__name__, sys.exc_info()[1])
           
        return HttpResponse(s_json)

    if cde == "supprime_evenement":
        try:
            evt = Evenement.objects.get(id=int(request.POST.get("id", 0)))
            print("will delete", evt)
            evt.delete()
            s_json = '{"status":"true"}'
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]
           
        return HttpResponse(s_json)

    if cde == "deplacement_plant":
        ## deplacement de plants d'une planche vers une autre
        try:
            plant = Plant.objects.get(id=int(request.POST.get("id_plant")))
            b_deplacementPartiel = request.POST.get("deplacement_partiel") == "true"
            if b_deplacementPartiel:
                # nb de plants à déplacer
                nb_plants = request.POST.get("nb_plants") ## peut etre chaine vide donc pas castable
                if nb_plants:
                    nb_plants = int(nb_plants)
                else:
                    raise Exception("demande de deplacement partiel mais nb_plants non défini")                
            
            nb_rangs = int(request.POST.get("nb_rangs"))
            intra_rang_cm = int(request.POST.get("intra_rang_cm"))
            planche_dest = Planche.objects.get(num=int(request.POST.get("num_planche_dest")))
            b_simu = request.POST.get("simu") == "true"
            reste = essai_deplacement_plants(plant.id, planche_dest.num, intra_rang_cm, nb_rangs)
            
            if b_simu:
                if reste == 0:
                    rep = "SIMULATION\\nTous les plants sont déplaçables sur la planche %s" % planche_dest.num
                else:
                    rep = "SIMULATION\\nReste %d plants non déplaçables. Déplacement incomplet."%reste            
            elif reste == 0:
                ## si on peut tout transférer sur une seule planche, le plant chage de planche
                ## sinon, on cree une nouvelle serie de plants vers la planche partiellement accueillante et on garde le reste
                ## changement de planche
                plant.planche_id = planche_dest.id
                plant.nb_rangs = nb_rangs
                plant.intra_rang_cm = intra_rang_cm
                plant.save()
                rep ="Tous les plants ont été déplacés"
            else:
                ## Création nouvelle série de #plants sur planche dest
                plant2 = clonePlant(plant) ## creation d'un nouveau plant
                ## maj quantités
                plant2.quantite = plant.quantite - reste 
                plant.quantite = reste
                plant.save()
                ## changement de planche
                plant2.planche_id = planche_dest.id
                plant2.nb_rangs = nb_rangs
                plant2.intra_rang_cm = intra_rang_cm
                plant2.save() 
                rep = "plant %d déplacé partiellement (reste %d) sur planche %d "%(plant.id, reste, planche_dest.num)

            s_json = '{"status":"true", "msg":"%s"}'%rep
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]
           
        return HttpResponse(s_json)


    print("No action engaged for", request.POST)

    return HttpResponse("No request treated inside serveRequest")


