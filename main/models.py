# -*- coding: utf-8 -*-
from django.db import models
import datetime
import sys, traceback

from main import constant  
from main.Tools import MyTools

import logging

## fabrique d'éléments et enregistrement dans la base


def creationEvt(e_date, e_type, id_serie, duree_j=1, nom=""):
    """création d'une evenement en base
    retourne l'instance de l'évènement"""
    if isinstance(e_date, str): e_date = MyTools.getDateFrom_d_m_y(e_date)
    evt = Evenement()
    evt.type = e_type
    evt.date = e_date
    evt.duree_j = duree_j
    evt.nom = nom
    evt.serie_id = id_serie
    evt.save()
    return evt


def creationEditionSerie(id_serie, id_planche, id_var, quantite, intra_rang_cm, nb_rangs, date_debut, date_fin=None):
    """Création ou edition d'une série de plants"""
    print(__name__)
    if id_serie == 0:
        serie = Serie() ## nelle serie
    else:
        serie = Serie.objects.get(id=id_serie)
    serie.variete_id = id_var
    serie.intra_rang_cm = intra_rang_cm
    serie.nb_rangs = nb_rangs
    serie.planche_id = id_planche
    serie.quantite = quantite
    serie.save()
    serie.fixeDates(date_debut, date_fin)
    return serie

def creationPlanche(longueur_m, largeur_cm, bSerre, s_nom="", num=None): 
    """Création d'une planche"""
    planche  = Planche()
    planche.longueur_m = longueur_m
    planche.largeur_cm = largeur_cm
    planche.bSerre = bSerre
    if s_nom:
        planche.nom = s_nom
    else:
        planche.nom = "Planche"
        
    if num is not None :    planche.num = num
    else:                   planche.num = planche.id
        
    planche.save()
    return planche
           
def recupListeImplantationsEnDateDu(la_date, planche):
    """Filtrage des implantations présents à telle date"""
    ## on ne renvoie que les implantations de cette planche
    l_implantations = Implantation.objects.filter(planche_id = planche.id)##   serie_id__in)
    l_series = Serie.objects.filter(evt_debut__date__lte = la_date,
                                    evt_fin__date__gte = la_date,
                                    implantations__id__in = l_implantations)
    
    ##.values_list("id",flat=True)
    return l_implantations


def essaiDeplacementSeries(idSerie, plancheDest, intraRangCm, nbRangs): 
    """tentative de placement de series ref <idSerie> sur planche <idPlancheDest> en fonction du nb de rang et distance dans le rang
    retourne le nombre de series restants à placer ailleurs si le nb de series est trop important pour la planche (déjà occupée ou trop courte par exemple)
    0 si tout peut etre placé sur la planche 
    """
    serie = Serie.objects.get(id = idSerie)
    
    cumul_max_m2 = 0
    ## pour chaque jour sur la planche, on calcule la surface de planche restante
    for day in MyTools.jourApresJour(serie.evt_debut.date, serie.evt_fin.date):
        cumul_m2 = 0
        ## recup des implantations déjà en place à cette date    
        l_implantations = recupListeImplantationsEnDateDu(day, plancheDest)
        
        for imp in l_implantations:
            cumul_m2 += imp.surface_m2()

        print (day, cumul_m2, "m2 occupés sur ", plancheDest.surface_m2(), "m2 (cumul max =", cumul_max_m2, ")" )
    
        cumul_max_m2 = max((cumul_max_m2, cumul_m2))
        
    libre_m2 = plancheDest.surface_m2 - cumul_max_m2
    print ("libre=%dm besoin=%dm"%(libre_m2, serie.longueurSurPlanche_m( intraRangCm, nbRangs)))

    reste_m = libre_m2 - serie.longueurSurPlanche_m(intraRangCm, nbRangs)
    if reste_m >=0:
        ## assez de place, on peut caser tous les series
        return 0
    else:
        ## pas assez de place, on retourne le nb de series restant à placer apres remplissage du reste de la planche
        return int(serie.nbSeriesPlacables(abs(reste_m), intraRangCm, nbRangs))

def cloneSerie(serie):
    """clonage d'une série"""
    serie2 = Serie.objects.get(id=serie.id)
    serie2.id = None
    serie2.save() ## mode de création d'une nouvelle serie
    ## duplication des évenements
    for evt in Evenement.objects.filter(serie_id=serie.id):
        evt2 = Evenement.objects.get(id=evt.id)
        evt2.id = None
        evt2.serie_id = serie2.id
        evt2.save()
    return serie2

class Famille(models.Model):
    """famille associée à la varieté"""
    nom = models.CharField(max_length=100)
    
    class Meta: 
        ordering = ['nom']
        
    def __unicode__(self):
        return self.nom


class Planche(models.Model):
    """ planche de culture"""
    num = models.PositiveIntegerField(null=True, blank=True, default=0)
    nom = models.CharField(max_length=100, blank=True, default="", unique=True)
    longueur_m = models.IntegerField()
    largeur_cm = models.IntegerField()
    bSerre = models.BooleanField(default=False)

    def __str__(self):
        if self.bSerre: s_lieu = "sous serre"
        else:           s_lieu = "plein champ"
        return "%s : %d m x %d cm; %s (%d)" % ( self.nom, self.longueur_m, self.largeur_cm, s_lieu, self.id)


class Espece(models.Model):
    """Espèce de légume"""
    nom = models.CharField(max_length=100)
    famille = models.ForeignKey(Famille, null=True, blank=True)
    avec = models.ManyToManyField("self", related_name="avec", blank=True)
    sans = models.ManyToManyField("self", related_name="sans", blank=True)
    unite_prod = models.PositiveIntegerField(default=constant.UNITE_PROD_KG)
    prod_kg_par_m2 = models.FloatField("Production (kg/m2)", default=0)     
        
    class Meta:
        ordering = ['nom']
        
    def __str__(self):
        return self.nom                    


class Variete(models.Model):
    """variété de légume"""
    nom = models.CharField(max_length=100)    
    espece = models.ForeignKey(Espece, null=True, blank=True)
    prod_kg_par_m2 = models.FloatField("Production (kg/m2)", default=0)     ## peut etre different de l'espece
    rendement_plants_graines_pourcent = models.IntegerField('Pourcentage plants / graine', default=90)
    intra_rang_cm = models.IntegerField("distance dans le rang (cm)", default=10)
    couleur = models.CharField(max_length=16)
    date_min_plantation_pc = models.CharField(verbose_name="date (jj/mm) de début de plantation en plein champ", max_length=10, default="0/0")
    date_max_plantation_pc = models.CharField(verbose_name="date (jj/mm) de fin de plantation en plein champ", max_length=10, default="0/0")
    date_min_plantation_sa = models.CharField(verbose_name="date (jj/mm) de début de plantation sous abris", max_length=10, default="0/0")
    date_max_plantation_sa = models.CharField(verbose_name="date (jj/mm) de fin de plantation sous abris", max_length=10, default="0/0")
    duree_avant_recolte_pc_j = models.IntegerField("durée plein champ avant récolte (jours)", default=0)
    duree_avant_recolte_sa_j = models.IntegerField("durée en serre avant récolte (jours)", default=0)
    
    class Meta:
        ordering = ['nom']
            
    def __str__(self):
        return "%s %s"%(self.espece.nom, self.nom)

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
        return ret

    def prodSemaines(self, productionDemandee):
        """ retourne une liste de production(s) escomptée(s) par semaine (en kg ou en unités)"""
        
        if self.prod_kg_par_m2 == "0":
            assert "rendement /m2 non donnée pour %s"%self.nom
        
        l_ret = []
        
        for prodSemUnitaire in self.prod_especehebdo_moy_g.split(","):

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

class Implantation(models.Model):
    planche = models.ForeignKey("Planche")
#     debut_m = models.FloatField("Début de la culture (m)", default=0)
#     fin_m = models.FloatField("Début de la culture (m)", default=0)
    surface_m2 = models.FloatField("surface en m2)", default=0)## en attendant le placement plus précis...@todo

    def longueur_m(self):
        return self.fin_m - self.debut_m
    
    def surface_m2(self):
        return self.surface_m2
#         try:
#             return self.longueur_m() * self.planche.largeur_cm/100
#         except:
#             traceback.print_tb(sys.exc_info())
#             return 0

    def __str__(self):
        return "implantation N°%d de %d m2 sur planche %d)"%(self.id, self.surface_m2, self.planche.id)


class SerieManager(models.Manager):
    
    def surPlancheDansPeriode(self, idPlanche, dateDebut, dateFin):
        """retourne les séries de la planche contenues dans un interval de temps donné"""
        l_allSeries = super(SerieManager, self).get_queryset()
        l_ids = []
        
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
#         logging.getLogger('console').setLevel(logging.INFO)
        
        for serie in l_allSeries:
            ## list des id d'implantations de cette série
            l_impIds = list(eval(serie.l_implantation))
            ## recup des implantations et de leur planche associée
            l_planches_imp = Implantation.objects.filter(id__in=l_impIds).values_list('planche_id', flat=True)
                
            if idPlanche not in l_planches_imp:
                continue
            
            debutSerie = MyTools.getDateFrom_y_m_d(str(serie.evt_debut.date).split(" ")[0])
            finSerie = MyTools.getDateFrom_y_m_d(str(serie.evt_fin.date).split(" ")[0])
            if  (debutSerie > dateDebut and debutSerie < dateFin) \
               or (finSerie > dateDebut and finSerie < dateFin):
                l_ids.append(serie.id)
        
        l_series = super(SerieManager, self).get_queryset().filter(id__in=l_ids)
        return l_series           

class Evenement(models.Model):
    
    TYPE_DEBUT = 1
    TYPE_FIN = 2
    TYPE_DIVERS = 3
    D_NOM_TYPES = {TYPE_DEBUT:"Début", TYPE_FIN:"Fin", TYPE_DIVERS:"Divers"}

    type =  models.PositiveIntegerField()
#     serie = models.ForeignKey(Serie)
    date = models.DateTimeField()
    date_creation = models.DateTimeField(default=datetime.datetime.now())
    duree_j = models.PositiveIntegerField("nb jours d'activité", default=1)
    nom = models.CharField(max_length=100, default="")
    texte = models.TextField(default="")
    b_fini = models.BooleanField(default=False)

    class Meta: 
        ordering = ['date']
    
    def nomType(self):
        return self.D_NOM_TYPES[self.type]  

                    
    def __str__(self):
        return "Evt %s %s pour serie %d, %s pour %d j"%(self.nomType(), self.id or "?", self.serie_id, self.date, self.duree_j )
             


class Serie(models.Model):
    
    class Meta:
        verbose_name = "Série de plants"

    variete = models.ForeignKey(Variete)
    dureeAvantDebutRecolte_j = models.IntegerField("durée min avant début de récolte (jours)", default=0)
    etalementRecolte_j = models.IntegerField("durée étalement possible de la récolte (jours)", default=0)
    nb_rangs = models.PositiveIntegerField("nombre de rangs", default=0)
    intra_rang_cm = models.PositiveIntegerField("distance dans le rang", default=0)
    bSerre = models.BooleanField(default=False)
    implantations = models.ManyToManyField(Implantation)
    quantite = models.PositiveIntegerField(default=1)
    evt_debut = models.ForeignKey(Evenement, related_name="+", null=True, default=0)
    evt_fin = models.ForeignKey(Evenement, related_name="+", null=True, default=0)
    l_prelevement = []
    
    objects = SerieManager()
    
    def prodEstimee_kg(self):
        """Retourne le poids (kg) de production escomptée""" 
        return self.variete.espece.prod_kg_par_m2 * self.surfaceSurPlanche_m2()
    
    def nbGraines(self):
        """ retourne le nb de graines à planter en fonction du nb de plants installés"""
        return(self.quantite * self.variete.rendement_plants_graines_pourcent / 100)

    def longueurSurPlanche_m(self, intra_rang_cm=None, nb_rangs=None):
        """ retourne la longueur occupée sur la planche en fonction des distances inter-rang et dans le rang
        intra_rang_cm et nb_rangs peuvent etre forcés si pas encore définis, autrement on prend les parametres prédéfinis"""
        if not intra_rang_cm:
            intra_rang_cm = self.intra_rang_cm
        if not nb_rangs:
            nb_rangs = self.nb_rangs
        assert intra_rang_cm, Exception("intra_rang_cm non défini")
        assert nb_rangs, Exception("nb_rangs non défini")
        
        if nb_rangs == 0:
            return 0                
        return ((self.quantite * intra_rang_cm)/nb_rangs)/100
    
    def surfaceSurPlanche_m2(self, intra_rang_cm=None, nb_rangs=None):
        """ retourne la surface occupée sur la planche en fonction des distances inter-rang et dans le rang
        intra_rang_cm et nb_rangs peuvent etre forcés si pas encore définis, autrement on prend ceux prédéfinis"""
        if not intra_rang_cm:
            intra_rang_cm = self.intra_rang_cm
        if not nb_rangs:
            nb_rangs = self.nb_rangs
                        
        return (self.longueurSurPlanche_m() * self.planche.largeur_cm/100)
    
    def nbSeriesPlacables(self, longueurDePlanche_m, intraRangCm=None, nbRangs=None):
        if not intraRangCm:
            intraRangCm = self.intra_rang_cm
        assert intraRangCm, Exception("intraRangCm non défini")
        if not nbRangs:
            nbRangs = self.nb_rangs
        assert nbRangs, Exception("nbRangs non défini")
        return longueurDePlanche_m * 100 * nbRangs / intraRangCm
     
    def fixeDates(self, dateDebut, dateFin=None):
        """Crée les evts de début et fin de vie des plants en terre"""
        if isinstance(dateDebut, str): 
            dateDebut = MyTools.getDateFrom_d_m_y(dateDebut)
            
        self.evt_debut_id = creationEvt(dateDebut, 
                                        Evenement.TYPE_DEBUT, 
                                        self.id, 
                                        1, 
                                        "début %s"%self.variete.nom).id
        
        if dateFin and isinstance(dateFin, str): 
            dateFin = MyTools.getDateFrom_d_m_y(dateFin)

        if not dateFin:
            dateFin = self.evt_debut.date + datetime.timedelta(days = self.dureeAvantDebutRecolte_j + self.etalementRecolte_seriej)

        self.evt_fin_id = creationEvt(dateFin, 
                                      Evenement.TYPE_DEBUT, 
                                      self.id, 1, 
                                      "fin %s"%self.variete.nom).id        

        self.save()
   
    def __str__(self):
        return "Série N°%d de %d plants de %s %s sur planche xxxx, %d cm dans le rang sur %d rangs, du %s au %s" %(  self.id, self.quantite, 
                                                                                                                   self.variete.espece.nom,
                                                                                                                   self.variete.nom, 
                                                                                                                   #"self.planche.num",
                                                                                                                   self.intra_rang_cm, 
                                                                                                                   self.nb_rangs, 
                                                                                                                   self.evt_debut.date,
                                                                                                                   self.evt_fin.date)

