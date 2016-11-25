# -*- coding: utf-8 -*-
import csv
import datetime, os

from django.core.management.base import BaseCommand
from main.models import *
from main.settings import PROJECT_PATH
import sys
   
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
            with open(os.path.join(PROJECT_PATH, "inputs", "Planches.csv"), "r+t", encoding="ISO-8859-1") as hF:
                reader = csv.DictReader(hF)
                for d_line in reader:                
                    nomPlanche = d_line.get("nom")
                    try:
                        p = Planche.objects.get(nom = nomPlanche)
                    except:
                        p = Planche()
                        p.nom = nomPlanche
                        print(nomPlanche)
                        p.longueur_m = int(d_line.get("longueur (m)", 0))
                        p.largeur_m = float(d_line.get("largeur (m)", "0").replace(",","."))
                        p.bSerre = (p.nom[0]=="S")
                        p.save()
                        print (p)               
        except:
            print(sys.exc_info()[1]) 
              


            
    def handle(self, *args, **options):

        log = logging.getLogger('utils')
        log.setLevel(logging.INFO)
        log = logging.getLogger('updatedb')
        log.setLevel(logging.INFO)
        
        
        ## maj planches
        self.creationPlanches()

        ## maj espèces et familles
        with open(os.path.join(PROJECT_PATH, "inputs", "production.csv"), "r+t", encoding="ISO-8859-1") as hF:
            reader = csv.DictReader(hF)
            for d_line in reader:
                nomEspece = d_line.get("Espèce").lower().strip()
                if nomEspece:
                    try:
                        ## déjà presente
                        esp = Espece.objects.get(nom = nomEspece)
                    except: 
                        ## absente : création
                        self.stdout.write("Ajout " + nomEspece)
                        esp = Espece()
                        esp.nom = nomEspece
                        esp.save()
                    
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
                        esp.famille_id = famille.id

                        esp.save()
                    
                    ## recup infos
                    try: 
                        
                        s_rendement = d_line.get("Rendement (kg/m²)","").replace(",",".") 
                        assert s_rendement, "'Rendement (kg/m²)' indéfini pour %s"%(esp.nom)            
                        esp.rendementProduction_kg_m2 = float(s_rendement)

                        s_unite = d_line.get("Unité","").lower().strip()
                        assert s_unite, "Pas d'interRang défini pour %s"%(esp.nom)
                        if s_unite == "kg":
                            esp.unite_prod = constant.UNITE_PROD_KG
                        else:
                            esp.unite_prod = constant.UNITE_PROD_PIECE

                        s_stockable = d_line.get("stockable","")
                        assert s_stockable, "pas de valeur 'stockable' pour espèce : %s"%(esp.nom)
                        esp.bStockable = s_stockable == "oui"     
                        
                        s_rendementC = d_line.get("Rendement conservation","").replace(",",".") 
                        assert s_rendementC, "'Rendement conservation' indéfini pour %s"%(esp.nom)            
                        esp.rendementConservation = float(s_rendementC)                                           

                        ## maj conso
                        s_field = d_line.get("Nombre de paniers", "0")
                        assert s_field, "'Nombre de paniers' indéfini pour %s"%(esp.nom)  
                        esp.nbParts = int(s_field)
                 
                        s_field = d_line.get("Conso hebdo par pannier", "0").replace(",",".")
                        assert s_field, "'Conso hebdo par pannier' indéfini pour %s"%(esp.nom)  
                        esp.consoHebdoParPart = float(s_field)
                                                                                
                        esp.save()
                    
                    except:
                        log.error(sys.exc_info()[1])
                        continue
                    
 

        ## maj variétés et séries
        with open(os.path.join(PROJECT_PATH, "inputs", "planning.csv"), "r+t", encoding="ISO-8859-1") as hF:
            reader = csv.DictReader(hF)
            for d_line in reader:
                ## une ligne par série
                s_espece = d_line.get("Espèce", "").lower().strip()
                espece = Espece.objects.get(nom=s_espece) 

                s_variet = d_line.get("Variété", "").lower().strip()
                
                if not s_espece or not s_variet:
                    print ("Ignore", d_line)
                    continue
                
                ## mise à jour liste des variétés
                try:
                    var = Variete.objects.get(nom = s_variet)
                except:
                    logging.info("Ajout " + s_variet)
                    var = Variete()
                    var.nom = s_variet
                    var.save()
                    espece.varietes.add(var)
                    espece.save()
                    continue    
                        
                ## mise à jour liste des légumes et planning de séries
                try:
                    leg = Legume.objects.get(espece_id = espece.id, variete_id = var.id)
                except:
                    self.stdout.write("Ajout " + s_variet)
                    leg = Legume()
                    leg.espece_id = espece.id
                    leg.variete_id = var.id
                    leg.save()
            
                ## recup infos légumes
                try: 
                    s_dateEnTerre = d_line.get("Date en terre","")
                    assert s_dateEnTerre, "Pas de date en terre définie pour %s %s "%(s_espece, s_variet)

                    s_intraRang = d_line.get("Intra rang (cm)","").replace(",",".") 
                    assert s_intraRang, "Pas d'intra Rang défini pour %s"%(esp.nom)            
                    leg.intra_rang_m = float(s_intraRang)/100
                    
                    s_interRang = d_line.get("Inter rang (cm)","").replace(",",".") 
                    assert s_interRang, "Pas d'inter rang défini pour %s"%(esp.nom)
                    leg.inter_rang_m = float(s_interRang)/100
                          
                    s_poidsParPiece = d_line.get("Poids estimé par pièce (g)", "0").replace(",",".") 
                    leg.poidsParPiece_kg = float(s_poidsParPiece)/1000

                    s_nbGrainesParPied = d_line.get("Nb graines par pied", "1") 
                    leg.nbGrainesParPied = int(s_nbGrainesParPied)

                    leg.save()
                    

                    ## maj série
                    try:
                        dateEnTerre = datetime.datetime.strptime(s_dateEnTerre, constant.FORMAT_DATE)
                        serie = Serie.objects.get(evenements__type = Evenement.TYPE_DEBUT,
                                                  evenements__date = dateEnTerre,
                                                  legume_id = leg.id)
                    except:
                        ## nouvelle série
                        serie = Serie()
                        serie.legume_id = leg.id
                        serie.save()

                    ## recup infos 
                    serie.dureeAvantRecolte_j = int(d_line.get("Durée avant récolte (j)", "0"))
                    serie.etalementRecolte_j = int(d_line.get("Étalement récolte (j)", "0"))
                    serie.save()
                    serie.fixeDates(dateEnTerre)
                    serie.nb_rangs = int(float(d_line.get("Nombre de rangs retenus", "0").replace(",",".")))
                    serie.intra_rang_m = leg.intra_rang_m
                    serie.quantite = int(float(d_line.get("Nombre de pieds", "0").replace(",",".")))
                    serie.rendementGermination = float(d_line.get("Rendement germination", "1").replace(",","."))
                    delaiCroissancePlants_j = int(d_line.get("Délai croissance plants (j)", "0"))
                    if delaiCroissancePlants_j != 0:
                        ## on ajoute un évenement de fabrication des plants
                        evt = creationEvt(serie.evt_debut.date - datetime.timedelta(days=delaiCroissancePlants_j), 
                                    Evenement.TYPE_DIVERS,
                                    "fabrication plants de %s x %d"%(serie.legume.nom(), 
                                                                     serie.quantite * serie.rendementGermination),
                                    1)
                        serie.evenements.add(evt)
                    serie.save()
                                            
                    ## implantation par defaut sur planche virtuelles serre ou plein champ
                    serie.bSerre = d_line.get("lieu", "SERRE") == "SERRE"
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
                    logging.info("ajout implantation de base %s", str(implantation))

                except:
                    logging.error(sys.exc_info()[1]) 
                    continue

        print("end of command " + self.__doc__)  
        
        
    
