# -*- coding: utf-8 -*-
'''
Created on Nov 26, 2013

@author: vgazeill
'''

from django.http import HttpResponse
from main.models import *
import sys, traceback
import datetime
from django.core import serializers

def serveRequest(request):
    """Received a request and return specific response"""
    cde = request.POST.get("cde","")
    print(request.POST)
    
    if cde == "get_evts_serie": 
        ## retour des évenements d'une série)
        try:
            l_evts = Serie.objects.get(id = int(request.POST.get("id", 0))).evenements.all()
            rep = serializers.serialize("json", l_evts)      
            s_json = '{"status":true, "l_evts": %s}'%rep
            print(s_json)
        except:
            print(__name__ + ': ' + str(sys.exc_info()[1]) )
            traceback.print_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%(sys.exc_info()[1])
             
        return HttpResponse(s_json, content_type="application/json")

    ## --------------- renvoi d'un evt à partir de son identifiant
    if cde == "get_evt": 
        try:
            evt = Evenement.objects.get(id = int(request.POST.get("id", 0)))
            s_ = serializers.serialize("json", evt)       
            s_json = '{"status":true,"evt":%s}'% s_
        except:
            traceback.print_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]
             
        return HttpResponse( s_json, content_type="application/json")

    ## --------------- creation ou maj serie de plants 
    if cde =="sauve_serie":
        try:
            # gestion de la création ou édition d'une série de plants
            serie = creationEditionSerie(
                                int(request.POST.get("id_serie")),
                                ##Planche.objects.get(num=int(request.POST.get("num_planche"))).id, 
                                int(request.POST.get("id_variete")), 
                                int(request.POST.get("quantite")), 
                                request.POST.get("intra_rang_cm")/100, 
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
            planche = Planche.objects.get(id=id_pl)
            if planche.nom == constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP or planche.nom == constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS:
                raise ValueError("Refus de suppression. Une planche virtuelle ne peut être détruite")
            ## @todo: suppression des series de plants associés
            ## suppression de la production associée
            ## supression des évenements associés à une serie de plants            
            
            planche.delete()
            
            s_json = '{"status":"true","id_planche":%d}'%id_pl
        except:
            s_json = '{"status":"false","err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")

    
    ## --------------- request to update database 
    if cde == "sauve_evt": 
        try:
            e_id = int(request.POST.get("id",0))
            id_serie = int(request.POST.get("id_serie",0))
            assert(id_serie != 0, "bad id_serie in sauve_evt")
            date = MyTools.getDateFrom_d_m_y(request.POST.get("date",""))
            print (date)
            duree_j = int(request.POST.get("duree_j", 1))
            nom = request.POST.get("nom","")

            if e_id == 0:
                ## nouvel evt
                evt = Evenement()
                evt.type = Evenement.TYPE_DIVERS
            else:
                # maj d'un evt deja existant
                evt = Evenement.objects.get(id=e_id)

            evt.date = date
            evt.duree_j = duree_j
            evt.nom = nom
            evt.save()
            Serie.objects.get(id=id_serie).evenements.add(evt)
            print(evt)
                
            s_json = '{"status":true}'
        except:
            traceback.print_tb(sys.exc_info())            
            s_json = '{"status":false,"err":"%s %s"}'%(__name__, sys.exc_info()[1])
           
        return HttpResponse(s_json)

    if cde == "supprime_evt":
        try:
            evt = Evenement.objects.get(id=int(request.POST.get("id", 0)))
            print("will delete", evt)
            evt.delete()
            s_json = '{"status":true}'
        except:
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]
           
        return HttpResponse(s_json)


    if cde == "deplacement_implantation":
        ## deplacement d'une serie de plants d'une planche vers une autre
        try:
            implantation = Implantation.objects.get(id=int(request.POST.get("id_implantation")))
            serie = implantation.serie_set.all()[0]
            ##id_planche_orig = implantation.planche.id  
            
            nb_rangs = int(request.POST.get("nb_rangs", serie.nb_rangs))
            intra_rang_m = float(request.POST.get("intra_rang_cm", serie.intra_rang_m*100))/100
            planche_dest = Planche.objects.get(id=int(request.POST.get("id_planche_dest")))
            b_simu = request.POST.get("simulation") == "true"
            reste = essaiDeplacementSeries(serie.id, planche_dest, intra_rang_m, nb_rangs)
                      
            if request.POST.get("partiel", "") == "true":
                # nb de plants à déplacer
                print ("demande de déplacement partiel")
                quantite = int(request.POST.get("quantite")) ## peut etre chaine vide donc pas castable
                
            if b_simu:
                if reste == 0:
                    rep = "SIMULATION\\nTous les plants sont déplaçables sur la planche %s" % planche_dest.nom
                else:
                    rep = "SIMULATION\planche_dest\nReste %d plants non déplaçables. Déplacement incomplet."%reste            
            elif reste == 0:
                ## si on peut tout transférer sur une seule planche, la série change de planche
                ## changement de planche
                print("changement complet de planche via l'implantation")
                implantation.planche_id = planche_dest.id
                implantation.save()               
                rep = "Tous les plants ont été déplacés sur la planche %s"%planche_dest.nom
            else:
                ## sinon, on cree une nouvelle serie de plants vers la planche partiellement accueillante et on garde le reste
                ## Création nouvelle implantation de plants sur planche dest @todo
                serie2 = cloneSerie(serie) ## creation d'une nouvelle série
                ## maj quantités
                serie2.quantite = serie.quantite - reste 
                serie.quantite = reste
                serie.save()
                ## changement de planche
                serie2.planche_id = planche_dest.id
                serie2.nb_rangs = nb_rangs
                serie2.intra_rang_m = intra_rang_m
                serie2.save() 
                rep = "série %d déplacé partiellement (reste %d) sur planche %s "%(serie.id, reste, planche_dest.nom)

            s_json = '{"status":true, "msg":"%s"}'%rep
        except:
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]
           
        return HttpResponse(s_json)


    print("No action engaged for", request.POST)

    return HttpResponse("No request treated inside serveRequest")


