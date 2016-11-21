# -*- coding: utf-8 -*-
import csv
import datetime

from django.core.management.base import BaseCommand
from main.models import *

import sys
   
class Command(BaseCommand):
    """updatedb commande
    mise à jour des la base à partir des tableaux CSV"""
    help = "updateDB"

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
            ficname = "Planches.csv"
            with open(ficname, "r+t", encoding="ISO-8859-1") as hF:
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
        
        ## maj planches
        self.creationPlanches()
        
        ## maj base de légumes
        l_fams = Famille.objects.all().values_list("nom", flat=True)
        print ("l_fams ", l_fams)

        ## maj espèces et familles
        ficname = "production.csv"
        with open(ficname, "r+t", encoding="ISO-8859-1") as hF:
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
                        s_stockable = d_line.get("stockable","")
                        assert s_stockable, "pas de valeur 'stockable' pour espèce : %s"%(nomEspece)
                        esp.bStockable = s_stockable == "oui"
                        esp.save()
                    except:
                        logging.error(sys.exc_info()[1])
                        continue                                
 

        ## maj variétés et séries
        ficname = "planning.csv"
        with open(ficname, "r+t", encoding="ISO-8859-1") as hF:
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
                        
                ## mise à jour liste des légumes
                try:
                    leg = Legume.objects.get(espece_id = espece.id, variete_id = var.id)
                except:
                    self.stdout.write("Ajout " + s_variet)
                    leg = Legume()
                    leg.espece_id = espece.id
                    leg.variete_id = var.id
                    leg.save()
            
                ## recup infos
                try: 
                    s_dateEnTerre = d_line.get("Date en terre","")
                    assert s_dateEnTerre, "Pas de date en terre définie pour %s %s "%(s_espece, s_variet)
                    
                    s_rendement = d_line.get("Rendement (kg/m²)","")  
                    assert s_rendement, "'Rendement (kg/m²)' indéfini pour %s"%(nomEspece)            
                    leg.rendementProduction_kg_m2 = float(s_rendement)
                    
                    s_poidsParPiece = d_line.get("Poids estimé par pièce (g)", "0")
                    leg.poidsParPiece_kg = float(s_poidsParPiece)/1000
                     
                    s_intraRang = d_line.get("Intra rang (cm)","")
                    assert s_intraRang, "Pas d'intra Rang défini pour %s"%(nomEspece)            
                    leg.intra_rang_m = float(s_intraRang)/100
                    
                    s_interRang = d_line.get("Inter rang (cm)","")
                    assert s_interRang, "Pas d'interRang défini pour %s"%(nomEspece)
                    leg.inter_rang_m = float(s_interRang)/100
                    
                    s_unite = d_line.get("Unité","").lower().strip()
                    assert s_unite, "Pas d'interRang défini pour %s"%(nomEspece)
                    if s_unite == "kg":
                        leg.unite_prod = constant.UNITE_PROD_KG
                    else:
                        leg.unite_prod = constant.UNITE_PROD_PIECE

                    leg.save()
                        
                except:
                    logging.error(sys.exc_info()[1])
                    continue                    
                
                ## maj série
                try:
                    dateEnTerre = datetime.datetime.strptime(s_dateEnTerre, constant.FORMAT_DATE)
                    serie = Serie.objects.get(evenements__type = Evenement.TYPE_DEBUT,
                                              evenements__date = dateEnTerre,
                                              variete__espece_nom = s_espece,
                                              variete_nom = s_variet)
                except:
                    ## nouvelle série
                    serie = Serie()
                    serie.legume = leg
                    serie.save()
                    
                try:
                    serie.dureeAvantDebutRecolte_j = int(d_line.get("Durée avant récolte (j)", "0"))
                    serie.etalementRecolte_seriej = int(d_line.get("Étalement récolte (j)", "0"))
                    serie.save()
                    serie.fixeDates(dateEnTerre)
                    serie.nb_rangs = int(float(d_line.get("Nombre de rangs retenus", 0).replace(",",".")))
                    serie.intra_rang_m = float(d_line.get("Intra rang (cm)", "0"))/100   ## renseigné en cm
                    serie.quantite = int(d_line.get("Nombre de pieds", "0"))
                    serie.rendementGermination = float(d_line.get("Rendement germination", 1))
                    delaiCroissancePlants_j = int(d_line.get("Délai croissance plants (j)", "0"))
                    if delaiCroissancePlants_j != 0:
                        ## on ajoute un évenement de fabrication des plants
                        evt = creationEvt(serie.evt_debut.date - datetime.timedelta(days=delaiCroissancePlants_j), 
                                    Evenement.TYPE_DIVERS,
                                    "fabrication plants %s %s x %d"%(serie.variete.espece.nom, 
                                                                     serie.variete.nom,
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
                    print(sys.exc_info()[1]) 
                    continue

        print("end of command " + self.__doc__)  
        
        
    
