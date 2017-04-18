# -*- coding: utf-8 -*-
import csv
import datetime, os, sys

from django.core.management.base import BaseCommand
from maraich.models import *
from maraich.settings import log
from maraich import settings


def getInt(d_in, name, default="0"):
    """return an int value in a dictionary"""
    try:
        _i = default
        _i = int(d_in.get(name, default).split(",")[0])
        return _i
    except:
        log.warning("finding %s %s %s"%(name, str(d_in), sys.exc_info()[1])) 

def getFloat(d_in, name, default="0"):
    """return a float value in a dictionary"""
    try:
        _f = default
        _f = float(d_in.get(name, default).replace(",","."))
        return _f
    except:
        log.warning("finding %s %s %s"%(name, str(d_in), sys.exc_info()[1])) 
    


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
                        p.longueur_m = getInt(d_line, "longueur (m)")
                        p.largeur_m = getFloat(d_line, "largeur (m)")
                        p.bSerre = (p.nom[0]=="S")
                        p.save()
                        log.info (p)    
                        if p.bSerre:
                            totalSerre_m2 += p.surface_m2()
                        else:
                            totalChamp_m2 += p.surface_m2()           
        except:
            log.error(sys.exc_info()[1]) 
              
        try:
            p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP)
            p.nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP
            p.longueur_m = totalChamp_m2
            p.largeur_m = 1
            p.bSerre = False
            p.save()          
        except:
            p = creationPlanche(totalChamp_m2, 1, False, constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP)
#             p = Planche()
        log.info (p)    

        try:
            p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS)
        except:
            p = Planche()
            p.nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS
            p.longueur_m = totalSerre_m2
            p.largeur_m = 1
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

                    espece.nbGrainesParPied = getInt(d_line,"Nb graines par pied") 
                    assert espece.nbGrainesParPied, "'Nb graines par pied' indéfini pour %s"%(espece.nom)

                    espece.rendementGermination = getFloat(d_line, "Rendement germination", "0")
                    assert espece.rendementGermination != 0, "'Rendement germination' indéfini pour %s"%(espece.nom)            

                    espece.rendementPousseEtConservation = getFloat(d_line, "Rendement pousse et conservation", "0") 
                    assert espece.rendementPousseEtConservation !=0, "'Rendement pousse et conservation' indéfini pour %s"%(espece.nom)            

                    ## maj conso
                    espece.nbParts = getInt(d_line, "Nombre de panniers", "0")
                    assert espece.nbParts != 0, "'Nombre de panniers' indéfini ou nul pour %s"%(espece.nom)  
             
                    espece.consoHebdoParPart = getFloat(d_line, "Conso hebdo par pannier", "0")
                    assert espece.consoHebdoParPart, "'Conso hebdo par pannier' indéfini pour %s"%(espece.nom)
                    
                    espece.delai_avant_retour_an = getInt(d_line, "Délai avant retour (an)", "0")
                    assert espece.delai_avant_retour_an, "'Délai avant retour (an)' indéfini pour %s"%(espece.nom)
                                                             
                    espece.volume_motte_cm3 = getInt(d_line, "Volume alvéole (cm³)", "0")
                                                             
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
                       
                ## recup infos légumes
                try: 
                    leg.intra_rang_m = getFloat(d_line, "Intra rang (cm)","0")/100
                    assert leg.intra_rang_m, "'Intra rang (cm)' indéfini pour %s"%(espece.nom)            

                    leg.prodParPied_kg = getFloat(d_line, "Production par pied (kg)") 
                    assert leg.prodParPied_kg, "Production par pied (kg)' indéfini pour %s"%(espece.nom)   
                             
                    leg.poidsParPiece_kg = getFloat(d_line, "Poids par pièce (g)")/1000 
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

                    ## recup infos série
                    serie.nb_rangs = getInt(d_line, "Nombre de rangs retenus")
                    assert serie.nb_rangs != 0, "'Nombre de rangs retenus' indéfini pour %s "%(leg.nom())
                    
                    val = d_line.get("lieu", "")
                    assert val, "'lieu' indéfini pour %s "%(leg.nom())                    
                    serie.bSerre = (val == "SERRE")
                    
                    serie.intra_rang_m = getFloat(d_line, "Intra rang (cm)","0")/100
                    assert serie.intra_rang_m, "'Intra rang (cm)' indéfini pour %s"%(leg.nom)    
                    
                    serie.remarque = d_line.get("Remarque", "")       
                    dureeAvantRecolte_j = getInt(d_line, "Durée avant récolte (j)")
                    
#                     serie.prelevement_sd = d_line, "Mode de prélèvement","" == "SD"   ## calcul prelevement selon distrib
                    
                    assert dureeAvantRecolte_j!=0, "Champ 'Durée avant récolte (j)' indéfini pour %s "%(leg.nom())
                    
                    etalementRecolte_j = getInt(d_line, "Étalement récolte (j)")
                    assert etalementRecolte_j!=0, "Champ 'Étalement récolte (j)' indéfini pour %s "%(leg.nom())                    
                    delaiCroissancePlants_j = getInt(d_line, "Délai croissance plants (j)")
                    
                    serie.save() 
                    serie.fixeDates(dateEnTerre, dureeAvantRecolte_j, etalementRecolte_j, delaiCroissancePlants_j)

                    ## implantation de la série par defaut sur planche virtuelles serre ou plein champ
                    implantation = Implantation()
                    if serie.bSerre:    
                        implantation.planche_id = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS).id
                    else:
                        implantation.planche_id = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP).id

                    ## on place toute la série sur cette implantation par défaut
                    implantation.nbPieds = getInt(d_line, "Nombre de pieds", "0")
                    assert implantation.nbPieds, "'Nombre de pieds' indéfini pour %s "%(leg.nom())
                     
                    implantation.save()
                    serie.implantations.add(implantation)
#                     serie.save()
                    log.info("Ajout %s", str(implantation))

                except:
                    s_err = str(sys.exc_info()[1])
                    l_err.append(s_err)
                    continue

        log.info("Fin de comande %s\n nombre d'erreurs = %d\n%s"%(self.__doc__,
                                                                len(l_err), 
                                                                "\n".join(l_err)))  
