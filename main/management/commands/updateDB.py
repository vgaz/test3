# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand       
from main.models import Famille, Variete, TypeEvenement
from main.constant import d_TitresTypeEvt
from main import constant
       
class Command(BaseCommand):
    """updateDB command"""
    help = "updateDB"

    def handle(self, *args, **options):
        
        ## maj type d'évenement
        l_typeEvt = TypeEvenement.objects.all().values_list("nom", flat=True)
        for n in d_TitresTypeEvt.keys():    
            if n in l_typeEvt: continue 
            hTE = TypeEvenement()
            hTE.nom = n
            hTE.save()
        
        ## maj base de légumes
        l_fams = Famille.objects.all().values_list("nom", flat=True)
        print ("l_fams ", l_fams)
        l_fams_sup = []
        ficname = "Legumes.csv"
        with open(ficname, "r+t", encoding="utf-8") as hF:
            reader = csv.DictReader(hF)
            for d_line in reader:
                variet = d_line.get("variete").lower()
                try:
                    v = Variete.objects.get(nom = variet)
                except:
                    self.stdout.write("Ajout " + variet)
                    v = Variete()
                    v.nom = variet

                v.date_min_plantation = d_line.get("date_min_plantation")
                v.date_max_plantation = d_line.get("date_max_plantation")
                v.duree_avant_recolte_j = int(d_line.get("duree_avant_recolte_j") or 0 )
                v.prod_hebdo_moy_g = d_line.get("prod_hebdo_moy_g")
                v.diametre_cm = int(d_line.get("diametre_cm") or 0)
                
                if d_line.get("unite_prod") == 'u': 
                    v.unite_prod = constant.UNITE_PROD_PIECE
                else:
                    v.unite_prod = constant.UNITE_PROD_KG
                     
                v.save()

                try:
                    fam = d_line.get("famille","").lower().strip()
                    print ("fam ", fam)
                    if fam and fam not in l_fams and fam not in l_fams_sup:
                        print("ajout famille %s"%fam)
                        hFam = Famille()
                        hFam.nom = fam
                        hFam.save()
                        l_fams_sup.append(fam)
                
                    if not v.famille:
                        v.famille = Famille.objects.get(nom=fam)
                        v.save()
                        print("maj %s / %s"%(v.nom, v.famille.nom))
                        
                except:
                    print("pb, pas de famille accessible pour %s dans le fichier %s" %(variet, ficname))
                
        ## mise à jour associations
        l_variets = Variete.objects.all().values_list("nom", flat=True)
        l_variets_sup = []
        reader = csv.DictReader(open("associationsPlantes.csv", "r+t", encoding="utf-8"))
        for d_line in reader:
            
            variet = d_line.get("variete").lower()
            
            try:
                s_tmp = d_line.get("avec","").lower()
                l_varAvec = [va.strip() for va in s_tmp.split(",") if va]
            except:
                l_varAvec = []
                
            try:
                s_tmp = d_line.get("sans","").lower()
                l_varSans = [va.strip() for va in s_tmp.split(",") if va]
            except:
                l_varSans = []

            l_ajoutSiBesoin = []
            l_ajoutSiBesoin.append(variet)
            l_ajoutSiBesoin.extend(l_varAvec)
            l_ajoutSiBesoin.extend(l_varSans)
                        
            for _v in set(l_ajoutSiBesoin):
                if _v and _v not in l_variets and _v not in l_variets_sup:
                    v = Variete()
                    v.nom = _v
                    v.save()
                    l_variets_sup.append(_v)
                    print("ajout variété" , v.nom)

            v = Variete.objects.get(nom = variet)
                
            ## mise à jour des variétés qui peuvent ou pas aller avec celle-ci
            for var in l_varAvec:
                v.avec.add(Variete.objects.get( nom = var ))
            for var in l_varSans:
                v.sans.add(Variete.objects.get( nom = var ))

            v.save()

        self.stdout.write("end of command " + self.__doc__)  
        
        
    