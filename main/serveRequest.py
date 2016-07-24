# -*- coding: utf-8 -*-
'''
Created on Nov 26, 2013

@author: vgazeill
'''

from django.http import HttpResponse

from main.models import Evenement, Serie, Planche, Production
from main.models import creationPlanche, creationEditionSerie, essaiDeplacementSeries, cloneSerie
import sys, traceback
import datetime
from main import constant

def serveRequest(request):
    """Received a request and return specific response"""
    rep = ""
    cde = request.POST.get("cde","")
    print(request.POST)
    
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
    if cde =='sauve_serie':
        try:
            # gestion de la création ou édition d'une série de plants
            serie = creationEditionSerie(
                                int(request.POST.get("id_serie")),
                                Planche.objects.get(num=int(request.POST.get("num_planche"))).id, 
                                int(request.POST.get("id_variete")), 
                                int(request.POST.get("quantite")), 
                                int(request.POST.get("intra_rang_cm")), 
                                int(request.POST.get("nb_rangs")), 
                                request.POST.get("date_debut"), 
                                request.POST.get("date_fin"))
            print(serie)
            s_json = '{"status":"true","msg":"%s"}'%serie
        except:
            ex_type, ex, tb = sys.exc_info()
            print (ex_type, ex)
            traceback.print_tb(tb)
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")

    
    if cde == 'supprime_serie':
        try:
            id_serie = int(request.POST.get("id", 0))
            if id_serie == 0:
                print("return _")
                raise(Exception, "série non supprimable")
            
            id_serie = int(id_serie)
            serie = Serie.objects.get(id=id_serie)
            
            ## suppression de la production associée
            try:
                prod = None
                prod = Production.objects.get(id = serie.production_id)
                prod.delete()##@todo: erreur il faut retrancher de la seule production de ces series 
            except:
                pass    

            ## supression des évenements associés
            for obj in Evenement.objects.filter(serie_base_id = serie.id):
                print ("Suppression ", obj)
                obj.delete()
             
            serie.delete()                
            print ("Supprime série", id_serie)
         
            s_json = '{"status":"true","id_serie":%d}'%id_serie
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")


    if cde == 'supprime_planche':
        try:
            id_pl = int(request.POST.get("id"))
            if id_pl == 1: raise ValueError("Refus de suppression. La planche virtuelle ne peut être détruite")
            ## @afaire suppression des series de plants associés
            ## suppression de la production associée
            ## supression des évenements associés à une serie de plants            
            planche = Planche.objects.get(id=id_pl)
            planche.delete()
            
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


    if cde == "deplacement_serie":
        ## deplacement d'une serie de plants d'une planche vers une autre
        try:
            serie = Serie.objects.get(id=int(request.POST.get("id_serie")))
            b_deplacementPartiel = request.POST.get("partiel") == "true"
            if b_deplacementPartiel:
                # nb de plants à déplacer
                nb_plants = request.POST.get("nb_plants") ## peut etre chaine vide donc pas castable
                if nb_plants:
                    nb_plants = int(nb_plants)
                else:
                    raise Exception("demande de déplacement partiel mais quantité non définie")                
            
            nb_rangs = int(request.POST.get("nb_rangs"))
            intra_rang_cm = int(request.POST.get("intra_rang_cm"))
            planche_dest = Planche.objects.get(id=int(request.POST.get("id_planche_dest")))
            b_simu = request.POST.get("simulation") == "true"
            reste = essaiDeplacementSeries(serie.id, planche_dest.num, intra_rang_cm, nb_rangs)
            
            if b_simu:
                if reste == 0:
                    rep = "SIMULATION\\nTous les plants sont déplaçables sur la planche %s" % planche_dest.num
                else:
                    rep = "SIMULATION\\nReste %d plants non déplaçables. Déplacement incomplet."%reste            
            elif reste == 0:
                ## si on peut tout transférer sur une seule planche, la série change de planche
                ## sinon, on cree une nouvelle serie de plants vers la planche partiellement accueillante et on garde le reste
                ## changement de planche
                print("changt complet de planche")
                serie.planche_id = planche_dest.id
                serie.nb_rangs = nb_rangs
                serie.intra_rang_cm = intra_rang_cm
                serie.save()
                rep ="Touts les plants ont été déplacés"
            else:
                ## Création nouvelle série de plants sur planche dest
                serie2 = cloneSerie(serie) ## creation d'une nouvelle série
                ## maj quantités
                serie2.quantite = serie.quantite - reste 
                serie.quantite = reste
                serie.save()
                ## changement de planche
                serie2.planche_id = planche_dest.id
                serie2.nb_rangs = nb_rangs
                serie2.intra_rang_cm = intra_rang_cm
                serie2.save() 
                rep = "Série %d déplacée partiellement (reste %d) sur planche %d "%(serie.id, reste, planche_dest.num)

            s_json = '{"status":"true", "msg":"%s"}'%rep
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]
           
        return HttpResponse(s_json)


    print("No action engaged for", request.POST)

    return HttpResponse("No request treated inside serveRequest")


