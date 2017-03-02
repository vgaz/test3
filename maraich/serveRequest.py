# -*- coding: utf-8 -*-
'''
Created on Nov 26, 2013

@author: vgazeill
'''

from django.http import HttpResponse
from maraich.models import *
import sys, traceback
import datetime
from django.core import serializers
from maraich.settings import log


def serveRequest(request):
    """Received a request and return specific response"""
    cde = request.POST.get("cde","")
    log.info("CDE..........." + cde)
    log.info(str(request.POST))

    if cde == "enregistre_recolte": 
        try:
            qte = int(request.POST.get("qte"))
            dateSem = MyTools.getDateFrom_y_m_d(request.POST.get("date_sem"))
            idLeg = int(request.POST.get("id_leg"))
            try:
                prod = Production.objects.get(dateDebutSemaine=dateSem, legume_id=idLeg)
            except:
                prod = Production(dateDebutSemaine=dateSem, legume_id=idLeg)
            prod.qte = qte
            prod.save()
            s_json = '{"status":true}'
            log.info(s_json)
        except:
            log.error(__name__ + ': ' + str(sys.exc_info()[1]) )
            traceback.log.info_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%(sys.exc_info()[1])
              
        return HttpResponse(s_json, content_type="application/json")

    
    elif cde == "get_evts_serie": 
        ## retour des évenements d'une série)
        try:
            l_evts = Serie.objects.get(id = int(request.POST.get("id", 0))).evenements.all()
            rep = serializers.serialize("json", l_evts)      
            s_json = '{"status":true, "l_evts": %s}'%rep
            log.info(s_json)
        except:
            log.info(__name__ + ': ' + str(sys.exc_info()[1]) )
            traceback.log.info_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%(sys.exc_info()[1])
             
        return HttpResponse(s_json, content_type="application/json")

    
    elif cde == "get_impls_serie": 
        ## retour des implantations d'une série)
        try:
            l_impls = Serie.objects.get(id = int(request.POST.get("id", 0))).implantations.all()
            rep = serializers.serialize("json", l_impls)      
            s_json = '{"status":true, "l_impls": %s}'%rep
            log.info(s_json)
        except:
            log.info(__name__ + ': ' + str(sys.exc_info()[1]) )
            traceback.log.info_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%(sys.exc_info()[1])
             
        return HttpResponse(s_json, content_type="application/json")
    
    elif cde == "sauve_qte_impantation":
        ## sauvegarde suite à modif de qté
        try:
            impl = Implantation.objects.get(id = int(request.POST.get("id")))
            impl.quantite = int(request.POST.get("qte"))
            impl.save()                            
            s_json = '{"status":true}'
        except:
            log.info(__name__ + ': ' + str(sys.exc_info()[1]) )
            traceback.log.info_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%(sys.exc_info()[1])
             
        return HttpResponse(s_json, content_type="application/json")
            
        
        
    ## --------------- renvoi d'un evt à partir de son identifiant
    elif cde == "get_evt": 
        try:
            evt = Evenement.objects.get(id = int(request.POST.get("id", 0)))
            s_ = serializers.serialize("json", evt)       
            s_json = '{"status":true,"evt":%s}'% s_
        except:
            traceback.log.info_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]
             
        return HttpResponse( s_json, content_type="application/json")

    ## --------------- creation ou maj serie de plants 
    elif cde =="sauve_serie":
        try:
            # gestion de la création ou édition d'une série de plants
            intra_rang_cm = request.POST.get("intra_rang_cm","")
            if not intra_rang_cm: intra_rang_m = 0
            else:  intra_rang_m = float(intra_rang_cm)/100
            nb_rangs = request.POST.get("nb_rangs","")
            if not nb_rangs: nb_rangs = 0
            else: nb_rangs = int(nb_rangs) 

            serie = creationEditionSerie(
                                        int(request.POST.get("id_serie","0")),
                                        int(request.POST.get("id_legume")), 
                                        request.POST.get("b_serre","off")=="on",
                                        intra_rang_m, 
                                        nb_rangs,
                                        request.POST.get("date_debut"), 
                                        int(request.POST.get("duree_fab_plants_j","0")),
                                        int(request.POST.get("duree_avant_recolte_j","0")),
                                        int(request.POST.get("etalement_recolte_j", "0")))
            log.info("Nouvelle série créée" + serie.__str__())
            s_json = '{"status":true,"msg":"%s"}'%serie
        except:
            ex_type, ex, tb = sys.exc_info()
            log.error (str(ex_type) + str(ex))
            traceback.log.info_tb(tb)
            s_json = '{"status":false,"msg":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")
    
    elif cde == 'supprime_serie':
        try:
            models.supprimeSerie(int(request.POST.get("id")))
            s_json = '{"status":true}'
        except:
            traceback.log.info_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")


    elif cde == 'supprime_planche':
        try:
            id_pl = int(request.POST.get("id"))
            planche = Planche.objects.get(id=id_pl)
            if planche.nom == constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP or planche.nom == constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS:
                raise ValueError("Refus de suppression. Une planche virtuelle ne peut être détruite")
            ## @todo: suppression des series de plants associés
            ## suppression de la production associée
            ## supression des évenements associés à une serie de plants            
            planche.delete()
            s_json = '{"status":true,"id_planche":%d}'%id_pl
        except:
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")


    elif cde == "sauve_impl": 
        try:
            impl = Implantation.objects.get(id=int(request.POST.get("id")))                
            impl.quantite = int(request.POST.get("quantite"))
            impl.save()
            s_json = '{"status":true}'
        except:
            traceback.log.info_tb(sys.exc_info())            
            s_json = '{"status":false,"err":"%s %s"}'%(__name__, sys.exc_info()[1])
           
        return HttpResponse(s_json)
    
    elif cde == 'supprime_impl':
        try:
            Implantation.objects.get(id=int(request.POST.get("id"))).delete()
            s_json = '{"status":true}'
        except:
            traceback.log.info_tb(sys.exc_info())
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]

        return HttpResponse( s_json, content_type="application/json")
        
    
    ## --------------- request to update database 
    elif cde == "sauve_evt": 
        try:
            e_id = int(request.POST.get("id", 0))
            id_serie = int(request.POST.get("id_serie",0))
            assert id_serie != 0, "bad id_serie in sauve_evt"
            date = MyTools.getDateFrom_d_m_y(request.POST.get("date",""))
            log.info (date)
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
            
            if e_id == 0:
                Serie.objects.get(id=id_serie).evenements.add(evt)
            
            log.info(evt)
                
            s_json = '{"status":true}'
        except:
            traceback.log.info_tb(sys.exc_info())            
            s_json = '{"status":false,"err":"%s %s"}'%(__name__, sys.exc_info()[1])
           
        return HttpResponse(s_json)

    elif cde == "supprime_evt":
        try:
            evt = Evenement.objects.get(id=int(request.POST.get("id", 0)))
            log.info("destruction de", evt)
            evt.delete()
            s_json = '{"status":true}'
        except:
            s_json = '{"status":false,"err":"%s"}'%sys.exc_info()[1]
           
        return HttpResponse(s_json)


    elif cde == "deplacement_implantation":
        ## déplacement d'une serie de plants d'une planche vers une autre
        try:
            implantation = Implantation.objects.get(id=int(request.POST.get("id_implantation")))
            id_planche_dest = int(request.POST.get("id_planche_dest"))
            planche_dest = Planche.objects.get(id=id_planche_dest)
            serie = implantation.serie()
            assert planche_dest.bSerre == serie.bSerre, "Attention, incompatibilité plein champ /sous serre entre série déplacée et planche de destination"
            ## vérification que la planche de destination ne contient pas déjà une implantation de cette série
            ## dans ce cas, absorbsion dans l'implantation dejà en place
            l_implantationDejaLa = serie.implantations.filter(planche_id = id_planche_dest)
            assert len(l_implantationDejaLa) <= 1, "plus d'une implantation deja en place sur la planche %s !!! "%planche_dest.nom
            if len(l_implantationDejaLa) == 1:
                implantationDejaLa = l_implantationDejaLa[0]
            else:
                implantationDejaLa = None
            
            
            quantite = int(request.POST.get("quantite"))
            assert quantite <= implantation.quantite, "Demande de quantité à déplacer (%d) plus importante que la quantité de l'implantation(%d)"%(quantite, implantation.quantite)
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
                    rep = "Les %d plants sont tous déplaçables sur la planche %s" % (quantiteDeplacable, planche_dest.nom)
                else:
                    rep = "Il n'y a pas assez de place pour un déplacement total, seulement %d plants sur %d sont déplaçables sur la planche %s"%(quantiteDeplacable, 
                                                                                                                                                   quantite,
                                                                                                                                                   planche_dest.nom)

            else:
                if dispoApresPlacement_m2 >= 0 and aConserverSurPlace == 0 :
                    ## si on peut et veut tout transférer sur une seule planche,
                    if implantationDejaLa:
                        ## l'implantation initiale dejà là absorbe l'arrivante
                        implantationDejaLa.quantite += quantiteDeplacable
                        implantationDejaLa.save()
                        ## puis l'arrivante est détruite 
                        rep = "Implantation %d totalement déplacée et absorbée par la %d sur planche %s"%(implantation.id,
                                                                                                          implantationDejaLa.id,
                                                                                                          planche_dest.nom   )
                        implantation.delete()
                        
                    else:
                        ##  l'implantation arrivante change de planche
                        implantation.planche_id = planche_dest.id
                        implantation.save()
                        rep = "Tous les plants ont été déplacés sur la planche %s"%planche_dest.nom

                else:   ## déplacement partiel subi ou choisi
                    if implantationDejaLa:
                        ## l'implantation initiale dejà là absorbe l'arrivante sans suppression de cette dernière
                        implantationDejaLa.quantite += quantiteDeplacable
                        implantationDejaLa.save()
                        implantation.quantite -= quantiteDeplacable
                        implantation.save()
                        rep = "Implantation %d (x%d) partiellement déplacée et absorbée par la %d (x%d) sur planche %s"%(implantation.id,
                                                                                                                         implantation.quantite,
                                                                                                                         implantationDejaLa.id,
                                                                                                                         implantationDejaLa.quantite,
                                                                                                                         planche_dest.nom )
                                    
                    else:
                        ## Création d'une nouvelle implantation sur la planche de destination  => quantite
                        nelleImpl = Implantation()
                        nelleImpl.planche_id = planche_dest.id
                        nelleImpl.quantite = quantiteDeplacable
                        nelleImpl.save()
                        serie.implantations.add(nelleImpl)
                        serie.save() 
                        ## mise à jour implantation d'origine
                        implantation.quantite = quantiteNonDeplacable + aConserverSurPlace
                        implantation.save()
                        rep = "Implantation déplacée partiellement sur planche %s (reste %d pieds sur l'implantation initiale)"%(planche_dest.nom, 
                                                                                                                               implantation.quantite)

            s_json = '{"status":true, "msg":"%s"}'%rep
        except:
            s_err = "Erreur : " + str(sys.exc_info()[1])
            log.error (s_err)
            s_json = '{"status":false,"msg":"%s"}'%s_err
           
        return HttpResponse(s_json)


    log.info("No action engaged for", request.POST)

    return HttpResponse("No request treated inside serveRequest")

