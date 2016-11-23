# -*- coding: utf-8 -*-
from django.db import models
import datetime, logging

from main import constant  
import MyTools

## fabrique d'éléments et enregistrement dans la base


def creationEvt(e_date, e_type, nom="", duree_j=1):
    """création d'une evenement en base
    retourne l'instance de l'évènement"""
    if isinstance(e_date, str): e_date = MyTools.getDateFrom_d_m_y(e_date)
    evt = Evenement()
    evt.type = e_type
    evt.date = e_date
    evt.duree_j = duree_j
    evt.nom = nom
    evt.save()
    return evt


def creationEditionSerie(id_serie, 
                         id_var, 
                         id_implantation, 
                         quantite_implantation, 
                         intra_rang_m, 
                         nb_rangs, 
                         date_debut, 
                         date_fin=None):
    """Création ou edition d'une série de plants
    si id_serie == 0, c'est une demande de création, sinon , d'édition/modification
    """
    print(__name__)
    if id_serie == 0:
        serie = Serie() ## nelle serie
    else:
        serie = Serie.objects.get(id=id_serie)
    serie.variete_id = id_var
    serie.intra_rang_m = intra_rang_m
    serie.nb_rangs = nb_rangs
    try:
        impl = serie.implantations.get(id=id_implantation)
    except:
        impl = Implantation()
    impl.quantite = quantite_implantation
    impl.save()
    serie.save()
    serie.fixeDates(date_debut, date_fin)
    return serie

def creationPlanche(longueur_m, largeur_m, bSerre, s_nom=""): 
    """Création d'une planche"""
    planche  = Planche()
    planche.longueur_m = longueur_m
    planche.largeur_m = largeur_m
    planche.bSerre = bSerre
    if s_nom:
        planche.nom = s_nom
    else:
        planche.nom = "Planche"
                
    planche.save()
    return planche
           



def surfaceLibreSurPeriode(planche, date_debut, date_fin): 
    """retourne la surface dispo de telle date à telle date
    est retenue la plus grande surface dispo sur TOUT l'intervale
    """
    ## recherche de toutes les séries de cette planche présentes sur la même période
    l_series_presentes = Serie.objects.activesSurPeriode(   date_debut,
                                                            date_fin, 
                                                            planche)
    
    ## recherche des dates de tous les changements potentiels de surface dispo
    ## on stocke les dates concernées
    l_dates_planche = [date_debut, date_fin]
    for _serie in l_series_presentes:
        l_dates_planche.append(_serie.evt_debut.date)
        l_dates_planche.append(_serie.evt_fin.date)
    sorted(l_dates_planche)
    
    ## pour chaque période sur la planche, on calcule la surface de planche prise
    
    cumul_max_m2 = 0
    for jour in l_dates_planche:
        cumul_m2 = 0
       
        for serie in l_series_presentes:
            if serie.activeEnDatedu(jour):
                cumul_m2 += serie.surfaceOccupee_m2(planche)

        print (jour, cumul_m2, "m2 occupés sur ", planche.surface_m2(), "m2 (cumul max =", cumul_max_m2, ")" )
    
        cumul_max_m2 = max((cumul_max_m2, cumul_m2))
        
    libre_m2 = planche.surface_m2() - cumul_max_m2
    return libre_m2
    
def quantitePourSurface(largeurPlanche_m, surface_m2, nbRangs, intraRang_m):
    """ estimation de la quantité de pieds implantables sur une planche
    quantité  =  (surface / largeur) x nbRangs / intra """
    return int(surface_m2 / largeurPlanche_m *nbRangs / intraRang_m)

def surfacePourQuantite(largeurPlanche_m, quantite, nbRangs, intraRang_m):
    """ estimation de la surface pour n de pieds implantables sur une planche """
    return int(quantite * intraRang_m / nbRangs * largeurPlanche_m)

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
    nom = models.CharField(max_length=100, blank=True, default="")
    longueur_m = models.IntegerField()
    largeur_m = models.FloatField()
    bSerre = models.BooleanField(default=False)
    
    class Meta: 
        ordering = ['nom']
        
    def surface_m2(self):
        return self.longueur_m * self.largeur_m

    def __str__(self):
        if self.bSerre: s_lieu = "sous serre"
        else:           s_lieu = "plein champ"
        return "%s (%d), %d m x %d m = %d m2; %s" % ( self.nom, self.id, 
                                                     self.longueur_m, 
                                                     self.largeur_m, 
                                                     self.surface_m2(), 
                                                     s_lieu)


class Espece(models.Model):
    """Espèce de légume"""
    nom = models.CharField(max_length=100)
    varietes = models.ManyToManyField("Variete")
    famille = models.ForeignKey(Famille, null=True, blank=True)
    avec = models.ManyToManyField("self", related_name="avec", blank=True)
    sans = models.ManyToManyField("self", related_name="sans", blank=True)
    intra_rang_m = models.FloatField("distance conseillée dans le rang (m)", default=0)
    inter_rang_m = models.FloatField("distance conseillée entre les rangs (m)", default=0)    
    rendementProduction_kg_m2 = models.FloatField("Rendement de production kg/m2)", default=1)
    unite_prod = models.PositiveIntegerField(default=constant.UNITE_PROD_KG)
    bStokable = models.BooleanField(default=False)
    
    
    class Meta:
        ordering = ['nom']
          
    def intra_rang_cm(self):
        return int(self.intra_rang_m * 100)                    
 
    def inter_rang_cm(self):
        return int(self.inter_rang_m * 100)               
 
    def __str__(self):
        return self.nom                    
 
    def nomUniteProd(self):
        return constant.D_NOM_UNITE_PROD[self.unite_prod]


class Variete(models.Model):
    """Variété"""
    nom = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nom
      
class Legume(models.Model):
    """légume"""
    espece = models.ForeignKey(Espece)
    variete = models.ForeignKey(Variete)
    prod_kg_par_m2 = models.FloatField("Production (kg/m2)", default=0)
    rendement_plants_graines_pourcent = models.IntegerField('Pourcentage plants / graine', default=90)
    rendementGermination = models.FloatField("Rendement germination", default=1)
    poidsParPiece_kg = models.FloatField("Poids estimé par pièce (g)", default=0)  ## sera optionnel si unite_prod = kg
    couleur = models.CharField(max_length=16)
#     duree_avant_recolte_pc_j = models.IntegerField("durée plein champ avant récolte (jours)", default=0)
#     duree_avant_recolte_sa_j = models.IntegerField("durée en serre avant récolte (jours)", default=0)
    
    class Meta:
        ordering = ['espece', 'variete']
            
    def __str__(self):
        return "%s %s"%(self.espece.nom, self.nom) 

    def nom(self):
        return "%s %s"%(self.espece.nom, self.variete.nom) 


    def plantsPourProdHebdo(self, productionDemandee):
        """ A REFAIRE retourne nb de plants en fonction de la prod escomptée (en kg ou en unité
        pour les plantes donnaPositiveIntegerFieldnt sur plusieurs semaines, on prend le rendement de la première semaine"""
        print ("productionDemandee_kg", productionDemandee)
        print ("self.prod_hebdo_moy_g", self.prod_hebdo_moy_g)  
        if self.prod_hebdo_moy_g == "0":
            print ("attention , réponse bidon dans  plantsPourProdHebdo %s"%self.nom)
            return productionDemandee
        
#         if self.unite_prod == constant.UNITE_PROD_PIECE:
#             return productionDemandee
#            d_lines_espece.get("bStockable", "
 
        ret =  int( (float(productionDemandee) * 1000) / float(self.prod_hebdo_moy_g.split(",")[0])  )
        print (ret)
        return (ret)

#     def prodSemaines(self, productionDemandee):
#         """ retourne une liste de production(s) escomptée(s) par semaine (en kg ou en unités)"""
#         if self.prod_kg_par_m2 == "0":
#             assert "rendement /m2 non donnée pour %s"%self.nom
#         
#         l_ret = []
#         
#         for prodSemUnitaire in self.prod_especehebdo_moy_g.split(","):
# 
#             if self.unite_prod == constant.UNITE_PROD_PIECE:
#                 l_ret.append(int(productionDemandee * float(prodSemUnitaire)))
#             else:
#                 l_ret.append(int((float(prodSemUnitaire)/1000) * productionDemandee) + 1)
# 
#         return (l_ret)

  


# class Production(models.Model):
#     """Prévision hebdomadaire des productions pour une variété"""
#     variete = models.ForeignKey(Variete)
#     date_semaine = models.DateField("date de début de semaine")
#     qte_dde = models.PositiveIntegerField("quantité demandée", default=0)
#     qte_prod = models.PositiveIntegerField("quantité produite", default=0)
#     
#     d_line.get("bStockable", "

#     class Meta: 
#         ordering = ["date_semaine"]
#             
#     def __str__(self):
#         return "semaine du %s : %s : dde=%d prod=%d (%s)"%(  self.date_semaine, 
#                                                              self.variete.nom, 
#                                                              self.qte_dde, 
#                                                              self.qte_prod, 
#                                                              self.variete.espece.nomUniteProd())

class Implantation(models.Model):
    planche = models.ForeignKey("Planche")
#     debut_m = models.FloatField("Début de la culture (m)", default=0)
#     fin_m = models.FloatField("Début de la culture (m)", default=0)
    quantite = models.IntegerField("nombre de pieds", default=0) ## en attendant le placement plus précis...@todo

    def longueur_m(self):
        return self.fin_m - self.debut_m

    def serie(self):
        """ retourne la série (unique) d'appartenance"""
        return self.serie_set.all()[0]
    
    def surface_m2(self):
        serie = self.serie()
        return surfacePourQuantite(self.planche.largeur_m, 
                            self.quantite, 
                            serie.nb_rangs, 
                            serie.intra_rang_m)
    def __str__(self):
        return "Implantation %d, %d pieds (%d m2) sur planche %s (%d)"%(  self.id, 
                                                                     self.quantite, 
                                                                     self.surface_m2(), 
                                                                     self.planche.nom,
                                                                     self.planche.id)

class SerieManager(models.Manager):
    
    def activesEnDateDu(self, la_date, planche=None):
        """Filtrage des séries présentes à telle date, sur telle planche"""
        l_series = Serie.objects.filter(evt_debut__date__lte = la_date, 
                                        evt_fin__date__gte = la_date).distinct()
        if planche:
            l_series = l_series.filter(implantations__planche_id = planche.id)
        
        return l_series

    def activesSurPeriode(self, date_debut, date_fin, planche=None):
        """Filtrage des séries présentes, au moins partiellement, dans un encadrement de dates
        on ne renvoie que les implantations de cette planche"""
        if planche:
            l_series = Serie.objects.filter(implantations__planche_id = planche.id)
        else:
            l_series = Serie.objects.all()
            
        l_series = l_series.distinct() ## évite les séries reprises plusieurs fois car présentes sur plusieurs planches  
        l_series = l_series.exclude(evt_debut__date__gt = date_fin)
        l_series = l_series.exclude(evt_fin__date__lt = date_debut)
        return l_series


class Evenement(models.Model):
    TYPE_DEBUT = 1
    TYPE_FIN = 2
    TYPE_DIVERS = 3
    D_NOM_TYPES = {TYPE_DEBUT:"Début", TYPE_FIN:"Fin", TYPE_DIVERS:"Divers"}

    type =  models.PositiveIntegerField()
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
        return "Evt %s (%s) %s pour %d j"%(self.nomType(), 
                                           self.id or "?", 
                                           self.date, 
                                           self.duree_j )
             


class Serie(models.Model):
    
    class Meta:
        verbose_name = "Série de plants"

    legume = models.ForeignKey(Legume)
    dureeAvantDebutRecolte_j = models.IntegerField("durée min avant début de récolte (jours)", default=0)
    etalementRecolte_seriej = models.IntegerField("durée étalement possible de la récolte (jours)", default=0)

    nb_rangs = models.PositiveIntegerField("nombre de rangs", default=0)
    intra_rang_m = models.FloatField("distance dans le rang (m)", default=0)
    bSerre = models.BooleanField(default=False)
    implantations = models.ManyToManyField(Implantation)
    evenements = models.ManyToManyField(Evenement)
    evt_debut = models.ForeignKey(Evenement, related_name="+", null=True, default=0)
    evt_fin = models.ForeignKey(Evenement, related_name="+", null=True, default=0)
    l_prelevement = []
    objects = SerieManager()
    
    def intraRang_cm(self):
        return int(self.intra_rang_m *100)
    
    def prodEstimee_kg(self):
        """Retourne le poids (kg) de production escomptée""" 
        return self.legume.prod_kg_par_m2 * self.surfaceOccupee_m2()
    
    def nbGraines(self):
        """ retourne le nb de graines à planter en fonction du nb de plants installés"""
        return(self.quantite * self.legume.rendement_plants_graines_pourcent / 100)

    def longueurSurPlanche_m(self, intra_rang_m=None, nb_rangs=None):
        """ retourne la longueur occupée sur la planche en fonction des distances inter-rang et dans le rang
        intra_rang_m et nb_rangs peuvent etre forcés si pas encore définis, autrement on prend les parametres prédéfinis"""
        if not intra_rang_m:
            intra_rang_m = self.intra_rang_m
        if not nb_rangs:
            nb_rangs = self.nb_rangs
        assert intra_rang_m, Exception("intra_rang_m non défini")
        assert nb_rangs, Exception("nb_rangs non défini")
        
        if nb_rangs == 0:
            return 0                
        return self.quantite * intra_rang_m / nb_rangs
    
    def surfaceOccupee_m2(self, planche=None):
        """ retourne la surface occupée de toutes ou d'une implantation
        si planche != None, retourne juste l'implantation sur cette planche """
        surface = 0
        for impl in self.implantations.all():
            if planche and impl.planche.id != planche.id:
                continue
            surface += impl.surface_m2()
        
        return surface
    
    def quantiteTotale(self):
        """cumul de toutes les quantités des implantations"""
        qte = sum(self.implantations.all().values_list("quantite",flat=True))
        return qte
    
    def fixeDates(self, dateDebut, dateFin=None):
        """Crée les evts de début et fin de vie des plants en terre"""
        if isinstance(dateDebut, str): 
            dateDebut = MyTools.getDateFrom_d_m_y(dateDebut)
            
        evt_debut = creationEvt(dateDebut, Evenement.TYPE_DEBUT, "début de %s"%(self.legume.nom()))
        self.evenements.add(evt_debut)
        self.evt_debut_id = evt_debut.id

        if not dateFin:
            dateFin = evt_debut.date + datetime.timedelta(days = self.dureeAvantDebutRecolte_j) + datetime.timedelta(days = self.etalementRecolte_seriej)
        
        if isinstance(dateFin, str): 
            dateFin = MyTools.getDateFrom_d_m_y(dateFin)
            
        evt_fin = creationEvt(dateFin, Evenement.TYPE_FIN, "fin %s"%(self.legume.nom()))       
        self.evt_fin_id = evt_fin.id
        self.evenements.add(evt_fin)
        
        ## ajout evt de début de récolte
        dateRecolte = evt_debut.date + datetime.timedelta(days = self.dureeAvantDebutRecolte_j)
        evt_recolte = creationEvt(dateRecolte, Evenement.TYPE_DIVERS, "Récolte %s"%(self.legume.nom()))       
        self.evenements.add(evt_recolte)
        
        self.save()
                
    def activeEnDatedu(self, date):  
        """retourneTrue ou False si série encore en terre à telle date"""
        if date >= self.evt_debut.date and date <= self.evt_fin.date:
            return True
        else:
            return False
    
    def s_listeNomsPlanches(self):
        """retourne la liste des planches de la série"""
        return ",".join(impl.planche.nom for impl in self.implantations.all())
         
    def __str__(self):       
        return "%s (N°%d), quantité %d, %d m2 sur planche(s) [%s], du %s au %s" %(self.legume.nom(),
                                                                                    self.id, 
                                                                                    self.quantiteTotale(),
                                                                                    self.surfaceOccupee_m2(), 
                                                                                    self.s_listeNomsPlanches(),
                                                                                    MyTools.getDMYFromDate(self.evt_debut.date),
                                                                                    MyTools.getDMYFromDate(self.evt_fin.date))



