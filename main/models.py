# -*- coding: utf-8 -*-
from django.db import models
import datetime

from main import constant  
from main.Tools import MyTools

## fabrique d'éléments et enregistrement dans la base

def creationEvt(e_date, e_type, id_serie, duree_j=1, nom=""):
    """création d'une evenement en base
    retourne l'instance de l'évènement"""
    if isinstance(e_date, str):
        e_date = MyTools.getDateFrom_d_m_y(e_date)
        
    evt = Evenement()
    evt.type = e_type
    evt.date = e_date
    evt.duree_j = duree_j
    evt.nom = nom
    evt.plant_base_id = id_serie
    evt.save()
    return evt

 
def creationSerie(id_planche, id_var, quantite, intra_rang_cm, nb_rangs, date_debut, date_fin):
    """Création d'une série de plants ou graines"""
    serie = Plant()
    serie.variete_id = id_var
    serie.intra_rang_cm = intra_rang_cm
    serie.nb_rangs = nb_rangs
    serie.planche_id = id_planche
    serie.quantite = quantite
    serie.save()
    serie.evt_debut_id = creationEvt(date_debut, Evenement.TYPE_DEBUT, serie.id, 1, "Début %s"%serie.variete.nom).id
    serie.evt_fin_id = creationEvt(date_fin, Evenement.TYPE_FIN,serie.id,  1, "Fin %s"%serie.variete.nom).id
    serie.save()
    return serie
   
def creationPlanche(longueur_m, largeur_cm, bSerre, s_nom="", num=None): 
    """Création d'une planche"""
    planche  = Planche()
    planche.longueur_m = longueur_m
    planche.largeur_cm = largeur_cm
    planche.bSerre = bSerre
    planche.num = 9999
    if s_nom:
        planche.nom = s_nom
    else:
        planche.nom = "Planche"
        
    planche.save()
    
    if num :
        planche.num = num
    else:
        planche.num = planche.id
    planche.save()
    return planche
           
def recupListePlantsEnDateDu(la_date, id_planche):
    """Filtrage des séries de plants presents à telle date"""
    l_evts_debut = Evenement.objects.filter(type = Evenement.TYPE_DEBUT, date__lte = la_date)
    l_PlantsIds = list(l_evts_debut.values_list('plant_base_id', flat=True))
    ## recup des evenements de fin ayant les mêmes id_plant que les evts de debut 
    l_evts = Evenement.objects.filter(type = Evenement.TYPE_FIN, plant_base_id__in = l_PlantsIds, date__gte = la_date)
    ## récup des id de plants dans cet encarement temporel
    l_PlantsIds = l_evts.values_list('plant_base_id', flat=True)
    l_plants = Plant.objects.filter(id__in = l_PlantsIds)
    if id_planche:
        l_plants = Plant.objects.filter(planche_id = id_planche)
    
    return l_plants


def essai_deplacement_plants(idPlant, numPlancheDest, intraRangCm, nbRangs): 
    """tentative de placement de plants ref <idPlant> sur planche <idPlancheDest> en fonction du nb de rang et distance dans le rang
    retourne le nombre de plants restants à placer ailleurs si le nb de plants est trop important pour la planche (déjà occupée ou trop courte par exemple)
    0 si tout peut etre placé sur la planche 
    """
    plant = Plant.objects.get(id = idPlant)
    planche = Planche.objects.get(num = numPlancheDest)
    
    cumul_max_m = 0
    ## pour chaque jour sur la planche, on calcule la distance de planche restante
    for day in MyTools.jourApresJour(plant.evt_debut.date, plant.evt_fin.date):
        cumul_m = 0
        ## recup des plants sur la planche à cette date et cumul des longeur sur planche    
        l_plants = recupListePlantsEnDateDu(day, planche.id)
        
        for p in l_plants:
            cumul_m += p.longueurSurPlanche_m()

        print (day, cumul_m, "m occupés sur ", planche.longueur_m, "m (cumul max =", cumul_max_m, ")" )
    
        cumul_max_m = max((cumul_max_m, cumul_m))
        
    libre_m = planche.longueur_m - cumul_max_m
    print ("libre=%dm besoin=%dm"%(libre_m, plant.longueurSurPlanche_m( intraRangCm, nbRangs)))

    reste_m = libre_m - plant.longueurSurPlanche_m(intraRangCm, nbRangs)
    if reste_m >=0:
        ## assez de place, on peut caser tous les plants
        return 0
    else:
        ## pas assez de place, on retourne le nb de plants restant à placer apres remplissage du reste de la planche
        return int(plant.nbPlantsPlacables(abs(reste_m), intraRangCm, nbRangs))

def clonePlant(plant):
    plant2 = Plant.objects.get(id=plant.id)
    plant2.id = None
    plant2.save() ## creation d'un nouveau plant
    ## duplication des évenements
    for evt in Evenement.objects.filter(plant_base_id=plant.id):
        evt2 = Evenement.objects.get(id=evt.id)
        evt2.id = None
        evt2.plant_base_id = plant2.id
        evt2.save()
    return plant2
    
class Famille(models.Model):
    """famille associée à la plante"""
    nom = models.CharField(max_length=100)
    
    class Meta: 
        ordering = ['nom']
        
    def __unicode__(self):
        return self.nom


class Planche(models.Model):
    """ planche de culture"""
    num = models.PositiveIntegerField(null=True, blank=True)
    nom = models.CharField(max_length=100, blank=True, default="")
    longueur_m = models.IntegerField()
    largeur_cm = models.IntegerField()
    bSerre = models.BooleanField(default=False)

    def __str__(self):
        if self.bSerre: s_lieu = "sous serre"
        else:           s_lieu = "plein champ"
        return "%s %d, %d m x %d cm; %s" % ( self.nom, self.num, self.longueur_m, self.largeur_cm, s_lieu)
    

class Variete(models.Model):
    """variété de plante"""
    nom = models.CharField(max_length=100)
    famille = models.ForeignKey(Famille, null=True, blank=True)
    avec = models.ManyToManyField("self", related_name="avec", blank=True)
    sans = models.ManyToManyField("self", related_name="sans", blank=True)
    date_min_plantation = models.CharField("date (jj/mm) de début de plantation", max_length=10, default="0/0")
    date_max_plantation = models.CharField("date (jj/mm) de fin de plantation", max_length=10, default="0/0")
    duree_avant_recolte_j = models.IntegerField("durée en terre avant récolte (jours)", default=0)
    prod_hebdo_moy_g = models.CommaSeparatedIntegerField("suite de production hebdomadaire moyenne (grammes) pour un plant", max_length=20, default="0") ##attention, pour les légumes "à la pièce" ( choux, salades..), ne saisir qu'une valeur 
    rendement_plants_graines_pourcent = models.IntegerField('Pourcentage plants / graine', default=90)
    intra_rang_cm = models.IntegerField("distance dans le rang (cm)", default=10)
    unite_prod = models.PositiveIntegerField(default=constant.UNITE_PROD_KG)
    ##image = models.ImageField()
    
    class Meta:
        ordering = ['nom']
            
    def __str__(self):
        return(self.nom) 

    def nomUniteProd(self):
        return constant.D_NOM_UNITE_PROD[self.unite_prod]  

    def plantsPourProdHebdo(self, productionDemandee):
        """ retourne nb de plants en fonction de la prod escomptée (en kg ou en unité
        pour les plantes donnant sur plusieurs semaines, on prend le rendement de la première semaine"""
        print ("productionDemandee_kg", productionDemandee)
        print ("self.prod_hebdo_moy_g", self.prod_hebdo_moy_g)  
        if self.prod_hebdo_moy_g == "0":
            print ("attention , réponse bidon dans  plantsPourProdHebdo %s"%self.nom)
            return productionDemandee
        
        if self.unite_prod == constant.UNITE_PROD_PIECE:
            return productionDemandee
        
        ret =  int( (float(productionDemandee) * 1000) / float(self.prod_hebdo_moy_g.split(",")[0])  )
        print (ret)
        return (ret)

    def prodSemaines(self, productionDemandee):
        """ retourne une liste de production(s) escomptée(s) par semaine (en kg ou en unités)"""
        if self.prod_hebdo_moy_g == "0":
            assert "prod hebdo non donnée pour %s"%self.prod_hebdo_moy_g.variete.nom
        
        l_ret = []
        
        for prodSemUnitaire in self.prod_hebdo_moy_g.split(","):

            if self.unite_prod == constant.UNITE_PROD_PIECE:
                l_ret.append(int(productionDemandee * float(prodSemUnitaire)))
            else:
                l_ret.append(int((float(prodSemUnitaire)/1000) * productionDemandee) + 1)

        return (l_ret)

  

class Production(models.Model):
    """Prévision hebdomadaire des productions pour une variété"""
    variete = models.ForeignKey(Variete)
    date_semaine = models.DateField("date de début de semaine")
    qte_dde = models.PositiveIntegerField("quantité demandée", default=0)
    qte_prod = models.PositiveIntegerField("quantité produite", default=0)
    

    class Meta: 
        ordering = ["date_semaine"]
            
    def __str__(self):
        return "semaine du %s : %s : dde=%d prod=%d (%s)"%(  self.date_semaine, 
                                                             self.variete.nom, 
                                                             self.qte_dde, 
                                                             self.qte_prod, 
                                                             self.variete.nomUniteProd())

class Plant(models.Model):
    
    class Meta:
        verbose_name = "Plant ou série de plants"

    variete = models.ForeignKey(Variete)
    nb_rangs = models.PositiveIntegerField("nombre de rangs", default=0)
    intra_rang_cm = models.PositiveIntegerField("distance dans le rang", default=0)
    planche = models.ForeignKey("Planche", default=0, blank=True)
    quantite = models.PositiveIntegerField(default=1)
    evt_debut = models.ForeignKey("Evenement", related_name="+", null=True, default=0)
    evt_fin = models.ForeignKey("Evenement", related_name="+", null=True, default=0)
    
    
    def donneSurface(self):
        if not intraRangCm:
            intraRangCm = self.intra_rang_cm
        assert intraRangCm, Exception("intraRangCm non défini")
        if not nbRangs:
            nbRangs = self.nb_rangs
        assert nbRangs, Exception("nbRangs non défini")
        return longueurDePlanche_m * 100 * nbRangs / intraRangCm
     
    def nbGraines(self):
        """ retourne le nb de graines à planter en fonction du nb de plants installés"""
        return(self.quantite * self.variete.rendement_plants_graines_pourcent / 100)

    def longueurSurPlanche_m(self, intra_rang_cm=None, nb_rangs=None):
        """ retourne la longueur occupée sur la planche en fonction des distances inter-rang et dans le rang
        intra_rang_cm et nb_rangs peuvent etre forcés si pas encore définis, autrement on prend ceux du plant défini"""
        if not intra_rang_cm:
            intra_rang_cm = self.intra_rang_cm
        if not nb_rangs:
            nb_rangs = self.nb_rangs
        if nb_rangs == 0:
            return 0                
        return ((self.quantite * intra_rang_cm)/nb_rangs)/100
    
    def surfaceSurPlanche_m2(self, intra_rang_cm=None, nb_rangs=None):
        """ retourne la longueur occupée sur la planche en fonction des distances inter-rang et dans le rang
        intra_rang_cm et nb_rangs peuvent etre forcés si pas encore définis, autrement on prend ceux du plant défini"""
        if not intra_rang_cm:
            intra_rang_cm = self.intra_rang_cm
        if not nb_rangs:
            nb_rangs = self.nb_rangs
                        
        return (self.longueurSurPlanche_m() * self.planche.largeur_cm/100)
    
    def nbPlantsPlacables(self, longueurDePlanche_m, intraRangCm=None, nbRangs=None):
        if not intraRangCm:
            intraRangCm = self.intra_rang_cm
        assert intraRangCm, Exception("intraRangCm non défini")
        if not nbRangs:
            nbRangs = self.nb_rangs
        assert nbRangs, Exception("nbRangs non défini")
        return longueurDePlanche_m * 100 * nbRangs / intraRangCm
     
    def fixeDates(self, dateDebut, dateFin=None):
        """ crée les evts de debut et fin de vie du/des plants"""
        e = Evenement()
        e.type = Evenement.TYPE_DEBUT
        e.date = dateDebut
        e.plant_base_id = self.id
        e.nom = "début %s"%self.variete.nom
        e.save()
        self.evt_debut_id = e.id
        print ("evt debut", e)
        e = Evenement()
        e.type = Evenement.TYPE_FIN
        if dateFin:
            e.date = dateFin
        else:
            e.date = dateDebut + datetime.timedelta(days = self.variete.duree_avant_recolte_j)
        e.plant_base_id = self.id
        e.nom = "fin %s"%self.variete.nom
        e.save()
        self.evt_fin_id = e.id
        self.save()
   
    def __str__(self):
        return "Série (%d) de %d plant(s) de %s sur planche %d, %d cm dans le rang sur %d rangs, du %s au %s" %(  self.id, self.quantite, self.variete.nom, 
                                                                                                        self.planche.num,
                                                                                                        self.intra_rang_cm, 
                                                                                                        self.nb_rangs, 
                                                                                                        self.evt_debut.date,
                                                                                                        self.evt_fin.date)

      
        #             print("nouvelle serie ", plants)

class Evenement(models.Model):
    
    TYPE_DEBUT = 1
    TYPE_FIN = 2
    TYPE_DIVERS = 3
    D_NOM_TYPES = {TYPE_DEBUT:"Début", TYPE_FIN:"Fin", TYPE_DIVERS:"Divers"}

    type =  models.PositiveIntegerField()
    plant_base = models.ForeignKey(Plant)
    date = models.DateTimeField()
    date_creation = models.DateTimeField(default=datetime.datetime.now())
    duree_j = models.PositiveIntegerField("nb jours d'activité", default=1)
    nom = models.CharField(max_length=100, default="")
    texte = models.TextField(default="")
    bFini = models.BooleanField(default=False)

    class Meta: 
        ordering = ['date']
    
    def nomType(self):
        return self.D_NOM_TYPES[self.type]  

                    
    def __str__(self):
        return "Evt %s %s pour plant %d, %s pour %d j"%(self.nomType(), self.id or "?", self.plant_base_id, self.date, self.duree_j )
             
