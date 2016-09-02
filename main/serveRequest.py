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

logging.disable(logging.DEBUG)

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
            serie = Serie.objects.get(id=int(request.POST.get("id")))
            ##print("Demande de suppression série %s"%serie.__str__())
            ## supression des évenements associés
            for obj in serie.evenements.all():
                print ("Suppression ", obj)
                obj.delete()
            ## supression des implantations
            for obj in serie.implantations.all():
                print ("Suppression ", obj)
                obj.delete()
             
            print ("Série supprimée")
            serie.delete()                
         
            s_json = '{"status":true}'
        except:
            traceback.print_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]

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
            e_id = int(request.POST.get("id", 0))
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
        ## déplacement d'une serie de plants d'une planche vers une autre
        try:
            implantation = Implantation.objects.get(id=int(request.POST.get("id_implantation")))
            planche_dest = Planche.objects.get(id=int(request.POST.get("id_planche_dest")))
            serie = implantation.serie()
            quantite = int(request.POST.get("quantite"))
            assert quantite <= implantation.quantite, "quantité saisie à déplacer plus importante que la quantité de l'implantation"
            if  implantation.quantite != quantite:
                aConserverSurPlace = implantation.quantite - quantite
            else:
                aConserverSurPlace=0
            
            nb_rangs = int(request.POST.get("nb_rangs", serie.nb_rangs))
            intra_rang_m = float(request.POST.get("intra_rang_cm", serie.intra_rang_m*100))/100
            b_simu = request.POST.get("simulation") == "true"

            dispoApresPlacement_m2 = surfaceLibreSurPeriode(planche_dest, serie.evt_debut.date, serie.evt_fin.date) - surfacePourQuantite(planche_dest.largeur_m, quantite, nb_rangs, intra_rang_m)
            if dispoApresPlacement_m2 >= 0: ##  assez de place
                quantiteNonDeplacable = 0
                quantiteDeplacable = quantite
            else:
                quantiteNonDeplacable = quantitePourSurface(planche_dest.largeur_m, abs(dispoApresPlacement_m2), nb_rangs, intra_rang_m)
                quantiteDeplacable = quantite - quantiteNonDeplacable

            if b_simu:
                if dispoApresPlacement_m2 >= 0 : ## toute la quantité demandée est déplaçable
                    rep = "Résultat de simulation : tous les plants (%d) sont déplaçable sur la planche %s" % (quantiteDeplacable, planche_dest.nom)
                else:
                    rep = "Résultat de simulation : pas assez de surface pour un déplacement total, seulement %d pieds possibles sur la planche %s"%(quantiteDeplacable, planche_dest.nom)

            else:
                if dispoApresPlacement_m2 >= 0 and aConserverSurPlace == 0 :
                    ## si on peut tout transférer sur une seule planche, l'implantation change de planche
                    implantation.planche_id = planche_dest.id
                    implantation.save()
                    rep = "Tous les plants ont été déplacés sur la planche %s"%planche_dest.nom

                else:
                    ## sinon, on crée une nouvelle implantation sur la planche de destination  => quantite
                    nelleImpl = Implantation()
                    nelleImpl.planche_id = planche_dest.id
                    nelleImpl.quantite = quantiteDeplacable
                    nelleImpl.save()
                    serie.implantations.add(nelleImpl)
                    serie.save() 
                    ## mise à jour implantation d'origine
                    implantation.quantite = quantiteNonDeplacable + aConserverSurPlace
                    implantation.save()
                    rep = "Implantation déplacée partiellement sur planche %s (reste %d pieds sur implantation initiale)"%(planche_dest.nom, 
                                                                                                                           implantation.quantite)

            s_json = '{"status":true, "msg":"%s"}'%rep
        except:
            s_err = "Erreur : " + str(sys.exc_info()[1])
            print (s_err)
            s_json = '{"status":false,"err":"%s"}'%s_err
           
        return HttpResponse(s_json)


    print("No action engaged for", request.POST)

    return HttpResponse("No request treated inside serveRequest")


