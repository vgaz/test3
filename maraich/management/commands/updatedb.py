# -*- coding: utf-8 -*-
import csv
import datetime, os

from django.core.management.base import BaseCommand
from maraich.models import *
from maraich.settings import log
from maraich import settings

def getInt(d_line, name, default="0"):
    return int(d_line.get(name, default).split(",")[0])

def getFloat(d_line, name, default="0"):
    return float(d_line.get(name, default).replace(",","."))


class Command(BaseCommand):
    """updatedb : mise à jour de la base à partir des tableaux CSV"""
    help = "Tapper python manage.py updatedb"

    def creationPlanches(self):
        """Création des planches de base et celles du fichier"""
        
        try:
            p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP)
        except:
            p = Planche()
            p.nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP
            p.longueur_m = 10000
            p.largeur_m = 1
            p.bSerre = False
            p.save()  

        try:
            p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS)
        except:
            p = Planche()
            p.nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS
            p.longueur_m = 10000
            p.largeur_m = 1
            p.bSerre = True
            p.save()  

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
        except:
            log.error(sys.exc_info()[1]) 
              


            
    def handle(self, *args, **options):

       
        l_err  = []

        ## maj planches
        self.creationPlanches()

        ## maj espèces et familles
        with open(os.path.join(settings.BASE_DIR, "inputs", "production.csv"), "r+t", encoding="ISO-8859-1") as hF:
            reader = csv.DictReader(hF)
            for d_line in reader:
                nomEspece = d_line.get("Espèce").lower().strip()
                if nomEspece:
                    try:
                        ## déjà presente
                        espece = Espece.objects.get(nom = nomEspece)
                    except: 
                        ## absente : création
                        log.info("Ajout %s"%nomEspece)
                        espece = Espece()
                        espece.nom = nomEspece
                        espece.save()
                    
                    nomFam = d_line.get("Famille","").lower().strip()
                    if nomFam:
                        try:
                            famille = Famille.objects.get(nom = nomFam)
                        except:
                            ## besoin création
                            famille = Famille()
                            famille.nom = nomFam
                            famille.save()
                        
                        ## maj famille de l'espèce
                        espece.famille_id = famille.id
                        espece.save()
                    
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

                        espece.rendementConservation = getFloat(d_line, "Rendement conservation", "0") 
                        assert espece.rendementConservation !=0, "'Rendement conservation' indéfini pour %s"%(esp.nom)            

                        ## maj conso
                        espece.nbParts = getInt(d_line, "Nombre de pieds", "0")
                        assert espece.nbParts != 0, "'Nombre de paniers' indéfini ou nul pour %s"%(espece.nom)  
                 
                        s_field = d_line.get("Conso hebdo par pannier", "").replace(",",".")
                        assert s_field, "'Conso hebdo par pannier' indéfini pour %s"%(espece.nom)  
                        espece.consoHebdoParPart = float(s_field)
                        
                        s_field = d_line.get("Délai avant retour (an)", "")
                        assert s_field, "'Délai avant retour (an)' indéfini pour %s"%(espece.nom)  
                        espece.delai_avant_retour_an = int(s_field)
                                                                 
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
                    assert s_espece, "Espèce indéfinie"   
                    
#                     assert s_espece == "laitue",'on ne garde sque les laitues pour test'
                    
                            
                    s_variet = d_line.get("Variété", "").lower().strip() 
                    assert s_variet, "Variété indéfinie pour %s"%(s_espece)
                    espece = Espece.objects.get(nom=s_espece) 
                    assert espece, "objet Espèce non trouvé pour %s"%(s_espece)
                except:
                    s_err = str(sys.exc_info()[1])
                    l_err.append(s_err)
                    continue
                
                try:
                    ## mise à jour des variétés
                    var = Variete.objects.get(nom = s_variet)
                except:
                    log.info("Ajout variété %s"%s_variet)
                    var = Variete()
                    var.nom = s_variet
                    var.save()
                    espece.varietes.add(var)
                    espece.save()
                        
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
                    val = d_line.get("Intra rang (cm)","").split(",")[0]
                    assert val, "Pas d'intra Rang défini pour %s"%(espece.nom)            
                    leg.intra_rang_m = float(val)/100
                    
                    val = d_line.get("Inter rang (cm)","").split(",")[0]
                    assert val, "Pas d'inter rang défini pour %s"%(espece.nom)
                    leg.inter_rang_m = float(val)/100
                    
                    ## pas de controle car inutile si unité  = kg    
                    s_poidsParPiece = d_line.get("Poids estimé par pièce (g)").split(",")[0] or "0" 
                    leg.poidsParPiece_kg = float(s_poidsParPiece)/1000

                    leg.rendementProduction_kg_m2 = getFloat(d_line, "Rendement (kg/m²)") 
                    assert leg.rendementProduction_kg_m2, "Champs 'Rendement (kg/m²)' indéfini pour %s"%(espece.nom)            

                    leg.save()
                    
                    ## maj série
                    s_dateEnTerre = d_line.get("Date en terre","")
                    assert s_dateEnTerre, "Champ 'Date en terre' indéfini pour %s"%(leg.nom())
                    dateEnTerre = datetime.datetime.strptime(s_dateEnTerre, constant.FORMAT_DATE)
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
                    serie.quantite = getInt(d_line, "Nombre de pieds", "0")
                    assert serie.quantite, "Champ 'Nombre de pieds' indéfini pour %s "%(leg.nom())
                    
                    serie.nb_rangs = getInt(d_line, "Nombre de rangs retenus")
                    assert serie.nb_rangs != 0, "Champ 'Nombre de rangs retenus' indéfini pour %s "%(leg.nom())
                    
                    val = d_line.get("lieu", "")
                    assert val, "Champ 'lieu' indéfini pour %s "%(leg.nom())                    
                    serie.bSerre = (val == "SERRE")
                    serie.intra_rang_m = leg.intra_rang_m
                    serie.remarque = d_line.get("Remarque", "")       
                    dureeAvantRecolte_j = getInt(d_line, "Durée avant récolte (j)")
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
                    implantation.quantite = serie.quantite
                    implantation.save()
                    serie.implantations.add(implantation)
                    serie.save()
                    log.info("Ajout %s", str(implantation))

                except:
                    s_err = str(sys.exc_info()[1])
                    if "could not convert string to float" in s_err:
                        pass
                    l_err.append(s_err)
                    continue

        log.info("Fin de comande %s\n nombre d'erreurs = %d\n%s"%(self.__doc__,
                                                                len(l_err), 
                                                                "\n".join(l_err)))  
