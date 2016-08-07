# -*- coding: utf-8 -*-
import csv
import datetime

from django.core.management.base import BaseCommand
from main.models import Famille, Planche, Serie, Variete, Espece, Implantation

from main import constant

import sys
   
class Command(BaseCommand):
    """updateDB command"""
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
            p.save()  

        try:
            p = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS)
        except:
            p = Planche()
            p.nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS
            p.longueur_m = 10000
            p.largeur_m = 1
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
        l_fams_sup = []

        ## maj espèces et familles
        ficname = "production.csv"
        with open(ficname, "r+t", encoding="ISO-8859-1") as hF:
            reader = csv.DictReader(hF)
            for d_line in reader:
                nomEspece = d_line.get("Légume").lower().strip()
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

                    unite = d_line.get("Unité","").lower().strip()
                    if not unite:
                        print("pas d'unité pour", esp.nom)
                    if unite == "kg":
                        esp.unite_prod = constant.UNITE_PROD_KG
                    else:
                        esp.unite_prod = constant.UNITE_PROD_PIECE
                    esp.save()      
 
                    
                    
    
        ## maj espèces, variétés et séries
        ficname = "planning.csv"
        with open(ficname, "r+t", encoding="ISO-8859-1") as hF:
            reader = csv.DictReader(hF)
            for d_line in reader:
                
                s_espece = d_line.get("Légume", "").lower().strip()
                s_variet = d_line.get("Variété", "").lower().strip()
                s_dateEnTerre = d_line.get("Date en terre","")
                
                if not s_espece or not s_variet:
                    print ("Ignore", d_line)
                    continue
                
                try:
                    v = Variete.objects.get(nom = s_variet)

                except:
                    self.stdout.write("Ajout " + s_variet)
                    v = Variete()
                
                v.nom = s_variet
                espece = Espece.objects.get(nom=s_espece) 
                v.espece_id = espece.id
                v.save()
                print(v)
                
                ## maj série
                if not s_dateEnTerre:
                    print ("Ignore ligne date en terre absente", d_line)
                    continue

                try:
                    dateEnTerre = datetime.datetime.strptime(s_dateEnTerre, constant.FORMAT_DATE)
                    serie = Serie.objects.get(evt_debut__date = dateEnTerre, variete = v)
                except:
                    serie = Serie()
                    serie.variete = v
                    serie.save()
                    
                try:
                    serie.dureeAvantDebutRecolte_j = int(d_line.get("Durée avant récolte (j)", "0"))
                    serie.etalementRecolte_seriej = int(d_line.get("Étalement récolte (j)", "0"))
                    serie.save()
                    serie.fixeDates(dateEnTerre)
                    serie.nb_rangs = int(d_line.get("Nombre de rangs retenus", "0"))
                    serie.intra_rang_m = float(d_line.get("Intra rang (cm)", "0"))/100   ## renseigné en cm
                    serie.quantite = int(d_line.get("Nombre de pieds", "0"))
                    serie.save()
                                            
                    ## implantation par defaut sur planche virtuelles serre ou plein champ
                    serie.bSerre = d_line.get("lieu", "SERRE") == "SERRE"
                    implantation = Implantation()
                    if serie.bSerre:    
                        implantation.planche_id = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS).id
                    else:
                        implantation.planche_id = Planche.objects.get(nom = constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP).id
                    ## on place toute la série sur cette implantation par défaut
                    
                    implantation.surface_m2 = serie.quantite*serie.intra_rang_m/serie.nb_rangs * constant.LARGEUR_PLANCHES_VIRTUELLES
                    implantation.save()
                    print(">>>>>>>>>>>>>>>>> ajout impl de base", implantation)
                    
                    serie.implantations.add(implantation)
                    serie.save()

                except:
                    print(sys.exc_info()[1]) 
                    continue
# 
#         
#         ficname = "Legumes.csv"
#         with open(ficname, "r+t", encoding="utf-8") as hF:
#             reader = csv.DictReader(hF)
#             for d_line in reader:
#                 variet = d_line.get("variete", "").lower()
#                 try:
#                     v = Variete.objects.get(nom = variet)
#                 except:
#                     self.stdout.write("Ajout " + variet)
#                     v = Variete()
#                     v.nom = variet
# 
#                 v.date_min_plantation_pc = d_line.get("date_min_plantation_pc")
#                 v.date_max_plantation_pc = d_line.get("date_max_plantation_pc")
#                 v.duree_avant_recolte_pc_j = int(d_line.get("duree_avant_recolte_pc_j") or 0 )
#                 v.date_min_plantation_sa = d_line.get("date_min_plantation_sa")
#                 v.date_max_plantation_sa = d_line.get("date_max_plantation_sa")
#                 v.duree_avant_recolte_sa_j = int(d_line.get("duree_avant_recolte_sa_j") or 0 )
#                 v.prod_hebdo_moy_g = d_line.get("prod_hebdo_moy_g")
#                 v.prod_hebdo_moy_g = d_line.get("prod_hebdo_moy_g")
#                 v.couleur = d_line.get("couleur","green")
#                 
#                 if d_line.get("unite_prod") == 'u': 
#                     v.unite_prod = constant.UNITE_PROD_PIECE
#                 else:
#                     v.unite_prod = constant.UNITE_PROD_KG
#                      
#                 v.save()
# 
#                 try:
#                     fam = d_line.get("famille","").lower().strip()
#                     if fam and fam not in l_fams and fam not in l_fams_sup:
#                         print("ajout famille %s"%fam)
#                         hFam = Famille()
#                         hFam.nom = fam
#                         hFam.save()
#                         l_fams_sup.append(fam)
#                 
#                     if not v.famille:
#                         v.famille = Famille.objects.get(nom=fam)
#                         v.save()
#                         print("maj %s / %s"%(v.nom, v.famille.nom))
#                         
#                 except:
#                     print("pb, pas de famille accessible pour %s dans le fichier %s" %(variet, ficname))
#                 
#         ## mise à jour associations
#         l_variets = Variete.objects.all().values_list("nom", flat=True)
#         l_variets_sup = []
#         reader = csv.DictReader(open("associationsPlantes.csv", "r+t", encoding="utf-8"))
#         for d_line in reader:
#             
#             variet = d_line.get("variete").lower()
#             
#             try:
#                 s_tmp = d_line.get("avec","").lower()
#                 l_varAvec = [va.strip() for va in s_tmp.split(",") if va]
#             except:
#                 l_varAvec = []
#                 
#             try:
#                 s_tmp = d_line.get("sans","").lower()
#                 l_varSans = [va.strip() for va in s_tmp.split(",") if va]
#             except:
#                 l_varSans = []
# 
#             l_ajoutSiBesoin = []
#             l_ajoutSiBesoin.append(variet)
#             l_ajoutSiBesoin.extend(l_varAvec)
#             l_ajoutSiBesoin.extend(l_varSans)
#             
#             for _v in set(l_ajoutSiBesoin):
#                 if _v and _v not in l_variets and _v not in l_variets_sup:
#                     v = Variete()
#                     v.nom = _v
#                     v.save()
#                     l_variets_sup.append(_v)
#                     print("ajout variété" , v.nom)
# 
#             v = Variete.objects.get(nom = variet)
#             v.b_choisi = False
#             ## mise à jour des variétés qui peuvent ou pas aller avec celle-ci
#             for var in l_varAvec:
#                 v.avec.add(Variete.objects.get( nom = var ))
#             for var in l_varSans:
#                 v.sans.add(Variete.objects.get( nom = var ))
# 
#             v.save()

        print("end of command " + self.__doc__)  
        
        
    
