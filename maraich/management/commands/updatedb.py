# -*- coding: utf-8 -*-
import csv
import datetime, os, sys

from django.core.management.base import BaseCommand
from maraich.models import *
from maraich.settings import log
from maraich import settings


class Command(BaseCommand):
    """updatedb : mise à jour de la base à partir des tableaux CSV"""
    help = "Tapper python manage.py updatedb"

    def creationPlanches(self):
        """Création des planches de base et celles du fichier"""
        totalSerre_m2 = 0
        totalChamp_m2 = 0
        
        try:
            with open(os.path.join(settings.BASE_DIR, "inputs", "Planches.csv"), "r+t", encoding="ISO-8859-1") as hF:
                reader = csv.DictReader(hF)
                for d_line in reader:                
                    nomPlanche = d_line.get("nom")
                    try:
                        p = Planche.objects.get(nom = nomPlanche)
                    except:
                        p = Planche()
                        p.nom = nomPlanche
                        p.longueur_m = MyTools.getIntInDict(d_line, "longueur (m)", 0, log)
                        p.largeur_m = MyTools.getFloatInDict(d_line, "largeur (m)", 0, log)
                        p.bSerre = p.nom.startswith("Serre")
                        p.save()
                        log.info(p)    
                        if p.bSerre:
                            totalSerre_m2 += p.surface_m2()
                        else:
                            totalChamp_m2 += p.surface_m2()           
        except:
            log.error(sys.exc_info()[1]) 
              
        try:
            p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP)
    
        except:
            p = creationPlanche(totalChamp_m2, 1, False, constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP)
            p.nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP
            p.longueur_m = totalChamp_m2
            p.largeur_m = 1.2
            p.bSerre = False
            p.save()      
            log.info (p)    

        try:
            p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS)
        except:
            p = Planche()
            p.nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS
            p.longueur_m = totalSerre_m2
            p.largeur_m = 1.2
            p.bSerre = True
            p.save()  
            log.info (p)    

           
            
    def handle(self, *args, **options):
        l_err  = []

        ## maj planches
        self.creationPlanches()

        ## maj espèces et familles
        with open(os.path.join(settings.BASE_DIR, "inputs", "production.csv"), "r+t", encoding="ISO-8859-1") as hF:
            reader = csv.DictReader(hF)
            for d_line in reader:
                try:
                    nomEspece = d_line.get("Espèce").lower().strip()
                    if nomEspece:                        
                        ## déjà presente
                        espece = Espece.objects.get(nom = nomEspece)
                except: 
                    ## absente : création
                    log.info("Ajout %s"%nomEspece)
                    espece = Espece()
                    espece.nom = nomEspece
                
                try:
                    nomFam = d_line.get("Famille","").lower().strip()
                    if nomFam:
                        famille = Famille.objects.get(nom = nomFam)
                except:
                    ## besoin création
                    famille = Famille()
                    famille.nom = nomFam
                    famille.save()
                    
                ## maj famille de l'espèce
                espece.famille_id = famille.id
            
                ## recup infos
                try:
                    s_unite = d_line.get("Unité","").lower().strip()
                    assert s_unite, "Pas d'interRang défini pour %s"%(espece.nom)
                    if s_unite == "kg":
                        espece.unite_prod = constant.UNITE_PROD_KG
                    else:
                        espece.unite_prod = constant.UNITE_PROD_PIECE

                    s_stockable = d_line.get("stockable","")
                    assert s_stockable, "pas de valeur 'stockable' pour espèce : %s"%(espece.nom)
                    espece.bStockable = (s_stockable == "oui")     

                    espece.nbGrainesParPied = MyTools.getIntInDict(d_line,"Nb graines à semer par trou", 0, log) 
                    assert espece.nbGrainesParPied, "'Nb graines à semer par trou' indéfini pour %s"%(espece.nom)

                    espece.rendementGermination = MyTools.getFloatInDict(d_line, "Rendement germination", "0", log)
                    assert espece.rendementGermination != 0, "'Rendement germination' indéfini pour %s"%(espece.nom)            

                    espece.rendementPousseEtConservation = MyTools.getFloatInDict(d_line, "Rendement pousse et conservation", "0", log) 
                    assert espece.rendementPousseEtConservation !=0, "'Rendement pousse et conservation' indéfini pour %s"%(espece.nom)            

                    ## maj conso
                    espece.nbParts = MyTools.getIntInDict(d_line, "Nombre de paniers", "0", log)
                    assert espece.nbParts != 0, "'Nombre de paniers' indéfini ou nul pour %s"%(espece.nom)  
             
                    espece.consoHebdoParPart = MyTools.getFloatInDict(d_line, "Conso hebdo par panier", "0", log)
                    assert espece.consoHebdoParPart, "'Conso hebdo par panier' indéfini pour %s"%(espece.nom)
                    
                    espece.delai_avant_retour_an = MyTools.getIntInDict(d_line, "Délai avant retour (an)",  "0", log)
                    assert espece.delai_avant_retour_an, "'Délai avant retour (an)' indéfini pour %s"%(espece.nom)
                                                             
                    espece.volume_motte_cm3 = MyTools.getIntInDict(d_line, "Volume alvéole (cm³)",  "0", log)
                                                             
                    s_field = d_line.get("Couleur", "brown").strip()
                    assert s_field, "'Couleur' indéfini pour %s"%(espece.nom)  
                    espece.couleur = s_field
                                                             
                    espece.save()
                
                except:
                    log.error(sys.exc_info()[1])
                    l_err.append(str(sys.exc_info()[1]))
                    continue

        ## maj variétés, légumes et séries
        with open(os.path.join(settings.BASE_DIR, "inputs", "planning.csv"), "r+t", encoding="ISO-8859-1") as hF:
            reader = csv.DictReader(hF)

            for d_line in reader:
                
                try:
                    s_espece = d_line.get("Espèce", "").lower().strip()                    
                    espece = Espece.objects.get(nom=s_espece) 
                except:
                    l_err.append("Erreur; espèce %s non trouvée. abandon"%(s_espece))
                    continue
                
                try:
                    s_variet = d_line.get("Variété", "").lower().strip() 
                    assert s_variet, "Variété indéfinie pour %s"%(s_espece)
                    ## mise à jour des variétés
                    var = Variete.objects.get(nom = s_variet)
                except:
                    log.info("Ajout variété %s"%s_variet)
                    var = Variete.objects.create_variete(s_variet)
                    espece.varietes.add(var)
                        
                ## mise à jour liste des légumes et planning de séries
                try:
                    leg = Legume.objects.get(espece_id = espece.id, variete_id = var.id)
                except:
                    leg = Legume()
                    leg.espece_id = espece.id
                    leg.variete_id = var.id
                    log.info("Ajout légume %s %s" % (espece.nom, var.nom))
                       
                try: 
                    leg.intra_rang_m = MyTools.getFloatInDict(d_line, "Intra rang (cm)","0", log)/100
                    assert leg.intra_rang_m, "'Intra rang (cm)' indéfini pour %s"%(espece.nom)            

                    leg.prodParPied_kg = MyTools.getFloatInDict(d_line, "Production théorique par trou (kg)", "0", log) 
                    assert leg.prodParPied_kg, "Production théorique par trou (kg)' indéfini pour %s"%(espece.nom)   
                             
                    leg.poidsParPiece_kg = MyTools.getFloatInDict(d_line, "Poids par pièce (g)", "0", log)/1000 
                    assert leg.poidsParPiece_kg, "Poids par pièce (g)' indéfini pour %s"%(espece.nom)            

                    leg.save()
                    
                    ## maj série
                    s_dateEnTerre = d_line.get("Date en terre","")
                    assert s_dateEnTerre, "'Date en terre' indéfini pour %s"%(leg.nom())
                    dateEnTerre = MyTools.getDateFrom_d_m_y(s_dateEnTerre)
                    try:
                        serie = Serie.objects.get(evt_debut__type = Evenement.TYPE_DEBUT,
                                                  evt_debut__date = dateEnTerre,
                                                  legume_id = leg.id)
                        continue ## dejà présente
                    
                    except:
                        ## nouvelle série
                        serie = Serie()
                        serie.legume = leg
                        
#                         ## maj agenda ics
#                         evt_txt = ""
#                         evt_nom = "Plantation %s %s" % (espece.nom, var.nom)
#                         evt_date = dateEnTerre
#                         ics_txt += constant.ICS_ITEM%(evt_nom,
#                                                       evt_txt, 
#                                                       str(evt_date).split(" ")[0].replace("-","")+"T080000",
#                                                       str(evt_date).split(" ")[0].replace("-","")+"T090000")
                        
                    ## recup infos série
                    serie.nb_rangs = MyTools.getIntInDict(d_line, "Nombre de rangs retenus", "0", log)
                    assert serie.nb_rangs != 0, "'Nombre de rangs retenus' indéfini pour %s "%(leg.nom())
                    
                    val = d_line.get("lieu", "")
                    assert val, "'lieu' indéfini pour %s "%(leg.nom())                    
                    serie.bSerre = (val == "SERRE")
                    
                    serie.intra_rang_m = MyTools.getFloatInDict(d_line, "Intra rang (cm)", "0", log)/100
                    assert serie.intra_rang_m, "'Intra rang (cm)' indéfini pour %s"%(leg.nom)    
                    
                    serie.remarque = d_line.get("Remarque", "")       
                    dureeAvantRecolte_j = MyTools.getIntInDict(d_line, "Durée avant récolte (j)")
                                        
                    assert dureeAvantRecolte_j!=0, "Champ 'Durée avant récolte (j)' indéfini pour %s "%(leg.nom())
                    
                    etalementRecolte_j = MyTools.getIntInDict(d_line, "Étalement récolte (j)", "0", log)
                    assert etalementRecolte_j!=0, "Champ 'Étalement récolte (j)' indéfini pour %s "%(leg.nom())                    
                    delaiCroissancePlants_j = MyTools.getIntInDict(d_line, "Délai croissance plants (j)", "0", log)
                    
                    serie.save() 
                    serie.fixeDates(dateEnTerre, dureeAvantRecolte_j, etalementRecolte_j, delaiCroissancePlants_j)

                    ## implantation de la série par defaut sur planche virtuelles serre ou plein champ
                    implantation = Implantation()
                    if serie.bSerre:    
                        implantation.planche_id = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS).id
                    else:
                        implantation.planche_id = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP).id

                    ## on place toute la série sur cette implantation par défaut
                    implantation.nbPieds = MyTools.getIntInDict(d_line, "Nombre de pieds", "0", log)
                    assert implantation.nbPieds, "'Nombre de pieds' indéfini pour %s "%(leg.nom())
                     
                    implantation.save()
                    serie.implantations.add(implantation)
                    log.info("Ajout %s", str(implantation))

                except:
                    s_err = str(sys.exc_info()[1])
                    l_err.append(s_err)
                    continue
        
#         try:
#             ics_txt += constant.ICS_QUEUE
#             MyTools.strToFic(os.path.join(settings.BASE_DIR, "cultures.ics"), ics_txt)
#         except:
#             s_err = str(sys.exc_info()[1])
#             l_err.append(s_err)
#             log.error(s_err)

                    
        log.info("Fin de comande %s\n nombre d'erreurs = %d\n%s"%(self.__doc__,
                                                                len(l_err), 
                                                                "\n".join(l_err)))  
