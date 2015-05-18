# -*- coding: utf-8 -*-
from django.db import models
from main import constant
import datetime

class Famille(models.Model):
    """famille associée à la plante"""
    nom = models.CharField(max_length=100)
    
    class Meta: 
        ordering = ['nom']
        
    def __unicode__(self):
        return self.nom


    
class Planche(models.Model):
    """ planche de culture"""
    
    num = models.PositiveIntegerField()
    nom = models.CharField(max_length=100, blank=True, default="")
    longueur_m = models.IntegerField()
    largeur_cm = models.IntegerField()
    
    def __unicode__(self):
        return "Planche %d : %s, %d m x %d cm" % (self.num, self.nom, self.longueur_m, self.largeur_cm)


class Variete(models.Model):
    """variété de plante"""
    nom = models.CharField(max_length=100)
    famille = models.ForeignKey(Famille, null=True, blank=True)
    avec = models.ManyToManyField("self", related_name="avec", null=True, blank=True)
    sans = models.ManyToManyField("self", related_name="sans", null=True, blank=True)
    date_min_plantation = models.CharField("date (jj/mm) de début de plantation", max_length=10, default="0/0")
    date_max_plantation = models.CharField("date (jj/mm) de fin de plantation", max_length=10, default="0/0")
    duree_avant_recolte_j = models.IntegerField("durée en terre avant récolte (jours)", default=0)
    prod_hebdo_moy_g = models.CommaSeparatedIntegerField("suite de production hebdomadaire moyenne (grammes) pour un plant", max_length=20, default="0,0") ##attention, pour les légumes "à la pièce" ( choux, salades..), ne saisir qu'une valeur 
    rendementPlantsGraines = models.FloatField('graines Pour 1 Plant', default=2)
    diametre_cm = models.IntegerField("diamètre (cm)", default=0)
    unite_prod = models.PositiveIntegerField(default=constant.UNITE_PROD_KG)
    ##image = models.ImageField()
    
    class Meta: 
        ordering = ['nom']
            
    def __str__(self):
        return(self.nom) 
    
    def nomUniteProd(self):
        return constant.D_NOM_UNITE_PROD[self.unite_prod]  

        
    def plantsPourProdHebdo(self, productionDemandee_kg):
        """ retourne nb de plants en fonction de la prod escomptée (en kg ou en unité
        pour les plantes donnant sur plusieurs semaines, on prend le rendement de la première semaine"""
        print ("productionDemandee_kg", productionDemandee_kg)
        print ("self.prod_hebdo_moy_g", self.prod_hebdo_moy_g)  
        if self.prod_hebdo_moy_g =="0,0":
            return 55#@todo
        ret =  int(productionDemandee_kg * 1000 / float(self.prod_hebdo_moy_g.split(",")[0]))
        print (ret)
        return (ret)

    def prodSemaines(self, productionDemandee):
        """ retourne une liste de production(s)escomptée par semaine (en kg ou en unité)"""
        if self.prod_hebdo_moy_g =="0,0":
            return [55]#@todo
        l_ret = []
        if self.unite_prod == constant.UNITE_PROD_KG:
            for prodSemUnitaire_g in self.prod_hebdo_moy_g.split(","):
                l_ret.append(int(productionDemandee * prodSemUnitaire_g))

        return (l_ret)

    

class TypeEvenement(models.Model):
    
    nom = models.CharField(max_length=20)
    
    def __str__(self):
        return self.nom
  
    

class Production(models.Model):
    """Prévision hebdomadaire des productions pour une variété"""
    variete = models.ForeignKey(Variete)
    date_semaine = models.DateTimeField("date de début de semaine")
    qte_dde = models.PositiveIntegerField("quantité demandée", default=0)
    qte_prod = models.PositiveIntegerField("quantité produite", default=0)

    class Meta: 
        ordering = ["date_semaine"]
            
    def __str__(self):
        return "sem du %s : %s : dde=%d prod=%d (%s)"%(self.date_semaine, 
                                                     self.variete.nom, 
                                                     self.qte_dde, 
                                                     self.qte_prod, 
                                                     self.variete.nomUniteProd())

class Plant(models.Model):
    
    class Meta:
        verbose_name = "Plant ou série de plants"
        
    variete = models.ForeignKey(Variete)
    nb_graines = models.IntegerField(default=1)
    largeur_cm = models.PositiveIntegerField("largeur cm", default=0)
    hauteur_cm = models.PositiveIntegerField("hauteur cm", default=0)
    coord_x_cm = models.PositiveIntegerField("pos x cm", default=0)
    coord_y_cm = models.PositiveIntegerField("pos y cm", default=0)
    planche = models.ForeignKey("Planche", null=True, blank=True)
    quantite = models.PositiveIntegerField(default=1)
    production = models.ForeignKey(Production)
   
    def __init__(self, variete_id, nb_plants):
        super(Plant, self).__init__()
        self.variete_id = variete_id
        self.quantite = nb_plants
        
    def nbGraines(self, nbPlants):
        """ retourne le nb de graines à planter en fonction du nb de plants installés"""
        return(self.quantite / self.variete.rendementPlantsGraines)

    def surface(self):
        """ retourne la surface prise, em m2, par la série de plants
        on prend le principe de 1 plant carré decoté = diametre variété"""
        return (self.quantite * float(self.variete.diametre_cm *self.variete.diametre_cm) / 10000 )
       
              
    def __str__(self):
        return "plant %d %s (%d gr), %d x %d, pos: %d %d sur planche %d" %(  self.id,  self.variete.nom, 
                                                                    self.nb_graines, 
                                                                    self.largeur_cm, 
                                                                    self.hauteur_cm, 
                                                                    self.coord_x_cm, 
                                                                    self.coord_y_cm, 
                                                                    self.planche.num)

        
        
class Evenement(models.Model):

    plant_base = models.ForeignKey(Plant)
    date_creation = models.DateTimeField(default=datetime.datetime.now())
    date = models.DateTimeField()
    duree = models.PositiveIntegerField("nb jours d'activité", default=1)
    nom = models.CharField(max_length=100, default="")
    texte = models.TextField(default="")
    bFini = models.BooleanField(default=False)
    type =  models.ForeignKey(TypeEvenement)

    class Meta: 
        ordering = ['date']
        
    def __unicode__(self):
        return "%d %s %s"%(self.plant_base_id, self.date, self.type)
