# -*- coding: utf-8 -*-
import csv
import datetime, os

from django.core.management.base import BaseCommand
from main.models import *
from main.settings import PROJECT_PATH
from main.settings import log
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
                        p.longueur_m = int(d_line.get("longueur (m)", "0"))
                        p.largeur_m = float(d_line.get("largeur (m)", "0").replace(",","."))
                        p.bSerre = (p.nom[0]=="S")
                        p.save()
                        print (p)               
        except:
            print(sys.exc_info()[1]) 
              


            
    def handle(self, *args, **options):

       
        l_err  = []

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
                        s_unite = d_line.get("Unité","").lower().strip()
                        assert s_unite, "Pas d'interRang défini pour %s"%(esp.nom)
                        if s_unite == "kg":
                            esp.unite_prod = constant.UNITE_PROD_KG
                        else:
                            esp.unite_prod = constant.UNITE_PROD_PIECE

                        s_stockable = d_line.get("stockable","")
                        assert s_stockable, "pas de valeur 'stockable' pour espèce : %s"%(esp.nom)
                        esp.bStockable = (s_stockable == "oui")     
                        
                        val = d_line.get("Rendement germination", "").replace(",",".")
                        assert val, "'Rendement germination' indéfini pour %s"%(esp.nom)            
                        esp.rendementGermination = float(val)                                           

                        val = d_line.get("Rendement conservation","").replace(",",".") 
                        assert val, "'Rendement conservation' indéfini pour %s"%(esp.nom)            
                        esp.rendementConservation = float(val)                                           

                        ## maj conso
                        s_field = d_line.get("Nombre de paniers", "")
                        assert s_field, "'Nombre de paniers' indéfini pour %s"%(esp.nom)  
                        esp.nbParts = int(s_field)
                 
                        s_field = d_line.get("Conso hebdo par pannier", "").replace(",",".")
                        assert s_field, "'Conso hebdo par pannier' indéfini pour %s"%(esp.nom)  
                        esp.consoHebdoParPart = float(s_field)
                        
                        s_field = d_line.get("Délai avant retour (an)", "")
                        assert s_field, "'Délai avant retour (an)' indéfini pour %s"%(esp.nom)  
                        esp.delai_avant_retour_an = int(s_field)
                                                                 
                        s_field = d_line.get("Couleur", "brown").strip()
                        assert s_field, "'Couleur' indéfini pour %s"%(esp.nom)  
                        esp.couleur = s_field
                                                                 
                        esp.save()
                    
                    except:
                        log.error(sys.exc_info()[1])
                        l_err.append(str(sys.exc_info()[1]))
                        continue

        ## maj variétés, légumes et séries
        with open(os.path.join(PROJECT_PATH, "inputs", "planning.csv"), "r+t", encoding="ISO-8859-1") as hF:
            reader = csv.DictReader(hF)
            for d_line in reader:
                
                try:
                    s_espece = d_line.get("Espèce", "").lower().strip()
                    assert s_espece, "Espèce indéfinie"           
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
                    log.info("Ajout " + s_variet)
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
                    val = d_line.get("Intra rang (cm)","").replace(",",".") 
                    assert val, "Pas d'intra Rang défini pour %s"%(esp.nom)            
                    leg.intra_rang_m = float(val)/100
                    
                    val = d_line.get("Inter rang (cm)","").replace(",",".") 
                    assert val, "Pas d'inter rang défini pour %s"%(esp.nom)
                    leg.inter_rang_m = float(val)/100
                      
                    ## pas de controle car inutile si unité  = kg    
                    s_poidsParPiece = d_line.get("Poids estimé par pièce (g)").replace(",",".") or "0" 
                    leg.poidsParPiece_kg = float(s_poidsParPiece)/1000

                    s_nbGrainesParPied = d_line.get("Nb graines par pied", "1") 
                    assert s_nbGrainesParPied, "'Nb graines par pied' indéfini pour %s"%(esp.nom)
                    leg.nbGrainesParPied = int(s_nbGrainesParPied)

                    s_rendement = d_line.get("Rendement (kg/m²)","").replace(",",".") 
                    assert s_rendement, "Champs 'Rendement (kg/m²)' indéfini pour %s"%(esp.nom)            
                    leg.rendementProduction_kg_m2 = float(s_rendement)

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
                    
                    val = int(float(d_line.get("Nombre de pieds", "0").replace(",",".")))
                    assert val, "Champ 'Nombre de pieds' indéfini pour %s "%(leg.nom())
                    serie.quantite = val
                    
                    val = int(float(d_line.get("Nombre de rangs retenus", "0").replace(",",".")))
                    assert val, "Champ 'Nombre de rangs retenus' indéfini pour %s "%(leg.nom())
                    serie.nb_rangs = val
                    
                    val = d_line.get("lieu", "")
                    assert val, "Champ 'lieu' indéfini pour %s "%(leg.nom())                    
                    serie.bSerre = (val == "SERRE")
                    serie.intra_rang_m = leg.intra_rang_m
                    serie.save()
                    dureeAvantRecolte_j = int(d_line.get("Durée avant récolte (j)", "0"))
                    assert dureeAvantRecolte_j, "Champ 'Durée avant récolte (j)' indéfini pour %s "%(leg.nom())                        
                    etalementRecolte_j = int(d_line.get("Étalement récolte (j)", "0"))
                    assert etalementRecolte_j, "Champ 'Étalement récolte (j)' indéfini pour %s "%(leg.nom())                    
                    delaiCroissancePlants_j = int(d_line.get("Délai croissance plants (j)", "0"))
                    print("aa")
                    serie.fixeDates(dateEnTerre, dureeAvantRecolte_j, etalementRecolte_j, delaiCroissancePlants_j)
                    print ("bb")

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
                    log.info("Ajout implantation de base %s", str(implantation))

                except:
                    s_err = str(sys.exc_info()[1])
                    l_err.append(s_err)
                    continue

        log.info("Fin de comande %s\n nombre d'erreurs = %d\n%s"%(self.__doc__,
                                                                len(l_err), 
                                                                "\n".join(l_err)))  
