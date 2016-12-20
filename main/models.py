# -*- coding: utf-8 -*-
from django.db import models
import datetime, logging
import sys

from main import constant
import MyTools

################################################################
#### controle des models

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
                         id_leg, 
                         bSerre,
                         id_implantation, 
                         quantite_implantation, 
                         intra_rang_m, 
                         nb_rangs, 
                         date_debut, 
                         date_fin=None):
    """Création ou edition d'une série de plants
    si id_serie == 0, c'est une demande de création, sinon , d'édition/modification
    """
    assert id_leg, '%s pas de valeur pour var'%__name__
    leg = Legume.objects.get(id=id_leg)
    if id_serie == 0:
        serie = Serie() ## nelle serie
    else:
        serie = Serie.objects.get(id=id_serie)
    serie.legume_id = leg.id
    if intra_rang_m:
        serie.intra_rang_m = intra_rang_m
    else:
        serie.intra_rang_m = leg.intra_rang_m
    serie.bSerre = bSerre
    
    if nb_rangs:
        serie.nb_rangs = nb_rangs
    else:
        ## selon la planche sur laquelle on atterira, on fixera le nb de rangs en fonction 
        ## de l'inter rang du legume et de la largeur de planche
        serie.nb_rangs = 0 
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
            if serie.enPlaceEnDatedu(jour):
                cumul_m2 += serie.surfaceOccupee_m2(planche)

        print (jour, cumul_m2, "m2 occupés sur ", planche.surface_m2(), "m2 (cumul max =", cumul_max_m2, ")" )
    
        cumul_max_m2 = max((cumul_max_m2, cumul_m2))
        
    libre_m2 = planche.surface_m2() - cumul_max_m2
    return libre_m2
    
def quantitePourSurface(largeurPlanche_m, surface_m2, nbRangs, intraRang_m):
    """ estimation de la quantité de pieds implantables sur une planche
    quantité  =  (surface / largeur) x nbRangs / intra """
    return int(surface_m2 / largeurPlanche_m * nbRangs / intraRang_m)

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
    ## pas d'imlantation 
    return serie2

def supprimeSerie(id):
    """ supression de la série et de ses champs liés"""
    try:
        serie = Serie.objects.get(id=id)
        ##print("Demande de suppression série %s"%serie.__str__())
        ## supression des évenements associés
        for obj in serie.evenements.all():
            print ("Suppression ", obj)
            obj.delete()
        ## supression des implantations
        for obj in serie.implantations.all():
            print ("Suppression ", obj)
            obj.delete()
         
        serie.delete()      
        print ("Série supprimée")
        return True
    except:
        print(str(sys.exc_info()))
        return False
    
    
def derniereDateFamilleSurPlanche(idFamille, idPlanche):
    """retourne la date de la dernière implantation d'un légume d'une faimlle donnée sur une planche donnée"""
    ## récup des implantations sur cette planche
    l_implantations = Implantation.objects.filter(planche_id=idPlanche)
    ## récup des séries associées à ces implantations et à cette famille
    l_series = Serie.objects.filter(implantations__in = l_implantations, legume__espece__famille_id=idFamille).order_by('evt_fin')
    ## on prend la plus recente des dates de fin
    qte = len(l_series)
    if not qte:
        date =  MyTools.getDateFrom_d_m_y("1/1/2000")   ## une vielle date
    else:
        date = l_series[qte-1].evt_fin.date
    return date

def respecteRotation(dateDebutImplantation, espece, planche):
    """retourne vrai ou faux selon que le temps de rotation souhaitable est respecté"""
    if derniereDateFamilleSurPlanche(espece.famille.id, planche.id) + datetime.timedelta(years=espece.delai_avant_retour_an) < dateDebutImplantation:
        return True
    return False
    
    

#################################################################
class Famille(models.Model):
    """famille associée à une ou plusieurs espèces"""
    nom = models.CharField("Nom de la famille", max_length=100)
    
    class Meta: 
        ordering = ['nom']
        
    def __unicode__(self):
        return self.nom

    def __str__(self):
        return self.__unicode__()
    
    def especes(self):
        """retourne la liste des espèces concernées par cette famille"""
        return self.espece_set.all()


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
    unite_prod = models.PositiveIntegerField(default=constant.UNITE_PROD_KG)
    bStockable = models.BooleanField(default=False)
    rendementConservation = models.FloatField("Rendement de conservation", default=0.9)
    rendementGermination = models.FloatField("Rendement germination", default=1)
    consoHebdoParPart = models.FloatField("quantité consommée par semaine par part", default=0)
    nbParts = models.PositiveIntegerField("Nb de parts à servir", default=0)
    couleur = models.CharField(max_length=16, default="yellow")
    delai_avant_retour_an = models.PositiveIntegerField("Délai avant retour de la même culture", default=3)
   
    class Meta:
        ordering = ['nom']              
 
    def __str__(self):
        return self.nom                    
 
    def nomUniteProd(self):
        return constant.D_NOM_UNITE_PROD[self.unite_prod]

    def consoHebdoTotale(self):
        return self.nbParts * self.consoHebdoParPart


class Panniers(models.Model):
    """Quantité de panniers au fil du temps"""
    val = models.PositiveIntegerField("Nb de parts ou panniers à servir par semaine", default=0)
    dateDebut = models.DateTimeField("date d'engagement de cette quantité de panniers")
    
    class Meta: 
        ordering = ['dateDebut'] ## pour lister du plus ancien au plus recent 

    def __str__(self):
        return "%d panniers à partir du %s"%(self.val, self.dateDebut)
    
    def quantiteEnDateDu(self, in_date):
        l_qtes = Panniers.objets.filter(dateDebut__lte = in_date)
        ## on renvoie le dernier
        return l_qtes[-1].val

      
class Variete(models.Model):
    """Variété"""
    nom = models.CharField(max_length=100)
    def __str__(self):
        return self.nom
      
class Legume(models.Model):
    """légume"""
    espece = models.ForeignKey(Espece)
    variete = models.ForeignKey(Variete)
    rendementProduction_kg_m2 = models.FloatField("Rendement de production (kg/m2)", default=1)
    poidsParPiece_kg = models.FloatField("Poids estimé par pièce (Kg)", default=0)  ## optionnel si unite_prod = kg
    nbGrainesParPied = models.PositiveIntegerField("Nb graines par pied", default=1)
    intra_rang_m = models.FloatField("distance dans le rang (m)", default=0)
    inter_rang_m = models.FloatField("distance entre les rangs (m)", default=0)    
    
    class Meta:
        ordering = ['espece', 'variete']
            
    def __str__(self):
        return "%s"%(self.nom())

    def intraRang_cm(self):
        return int(self.intra_rang_m * 100)                    
 
    def interRang_cm(self):
        return int(self.inter_rang_m * 100) 
    
    def nom(self):
        return "%s %s"%(self.espece.nom, self.variete.nom) 

    def poids_kg(self, qte):
        """Retourne la quantité en kg avec conversion éventuelle pièce > Kg
            pour les légumes vendus à la pièce"""
        if self.espece.unite_prod == constant.UNITE_PROD_PIECE:
            return (qte * self.poidsParPiece_kg)
        else:
            return (qte)
# 
#     def plantsPourProdHebdo(self, productionDemandee):
#         """ A REFAIRE retourne nb de plants en fonction de la prod escomptée (en kg ou en unité
#         pour les plantes donnaPositiveIntegerFieldnt sur plusieurs semaines, on prend le rendement de la première semaine"""
#         print ("productionDemandee_kg", productionDemandee)
#         print ("self.prod_hebdo_moy_g", self.prod_hebdo_moy_g)  
#         if self.prod_hebdo_moy_g == "0":
#             print ("attention , réponse bidon dans  plantsPourProdHebdo %s"%self.nom)
#             return productionDemandee
#         
#         ret =  int( (float(productionDemandee) * 1000) / float(self.prod_hebdo_moy_g.split(",")[0])  )
#         print (ret)
#         return (ret)

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
        return "Implantation %d, %d pieds (%d m2) sur planche %s (%d)"%( self.id, 
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
    date = models.DateTimeField("date de l'évenement")
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
        verbose_name = "Série de plants d'un même légume"

    legume = models.ForeignKey(Legume)
    dureeAvantRecolte_j = models.IntegerField("durée min avant début de récolte (jours)", default=0)
    etalementRecolte_j = models.IntegerField("durée étalement possible de la récolte (jours)", default=0)
    nb_rangs = models.PositiveIntegerField("nombre de rangs", default=0)
    intra_rang_m = models.FloatField("distance dans le rang (m)", default=0)
    bSerre = models.BooleanField(default=False)
    implantations = models.ManyToManyField(Implantation)
    evenements = models.ManyToManyField(Evenement)
    evt_debut = models.ForeignKey(Evenement, related_name="+", null=True, default=0)
    evt_fin = models.ForeignKey(Evenement, related_name="+", null=True, default=0)
    objects = SerieManager()
    
    def enPlaceEnDatedu(self, date):  
        """retourne True ou False si série encore en terre à telle date"""
        if date >= self.evt_debut.date and date <= self.evt_fin.date:
            return True
        else:
            return False
        
    def intraRang_cm(self):
        return int(self.intra_rang_m *100)
    
    def fixeDates(self, dateDebut, dateFin=None):
        """Crée les evts de début et fin de vie des plants en terre"""
        if isinstance(dateDebut, str): 
            dateDebut = MyTools.getDateFrom_d_m_y(dateDebut)
            
        evt_debut = creationEvt(dateDebut, Evenement.TYPE_DEBUT, "début de %s"%(self.legume.nom()))
        self.evenements.add(evt_debut)
        self.evt_debut_id = evt_debut.id

        if not dateFin:
            dateFin = evt_debut.date + datetime.timedelta(days = self.dureeAvantRecolte_j) + datetime.timedelta(days = self.etalementRecolte_j)
        
        if isinstance(dateFin, str): 
            dateFin = MyTools.getDateFrom_d_m_y(dateFin)
            
        evt_fin = creationEvt(dateFin, Evenement.TYPE_FIN, "fin %s"%(self.legume.nom()))       
        self.evt_fin_id = evt_fin.id
        self.evenements.add(evt_fin)

        ## ajout evt de début de récolte
        dateRecolte = evt_debut.date + datetime.timedelta(days = self.dureeAvantRecolte_j)
        evt_recolte = creationEvt(dateRecolte, Evenement.TYPE_DIVERS, "Récolte %s"%(self.legume.nom()))       
        self.evenements.add(evt_recolte)
        
        self.save()
 
    def nbGraines(self):
        """ retourne le nb de graines nécesaires en fonction du nb de pieds souhaité"""
        return int(self.quantite / self.legume.rendementGermination)

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

    def quantiteEstimee_kg_ou_piece(self):
            """Retourne la quantité totale escomptée (kg ou  pièces)""" 
            if self.legume.espece.unite_prod == constant.UNITE_PROD_KG:
                return self.legume.rendementProduction_kg_m2 * self.surfaceOccupee_m2()
            else:
                return self.quantiteTotale()
    
    
    def prodHebdo(self, dateDebutSem):
        """ renvoi la production estimée de cette semaine
        soit le stock lissé sur le nombre de semaines de consommation pour les legumes de garde
        soit le stock lissé sur la durée de la récolte pour les légumes en terre"""
        if self.legume.espece.bStockable: 
            nbSemEcoulementStock = int(self.quantiteEstimee_kg_ou_piece() / (self.legume.espece.consoHebdoTotale()))
            dateFinStock = self.evt_fin.date + datetime.timedelta(weeks = nbSemEcoulementStock)
            if dateDebutSem > self.evt_fin.date and dateDebutSem < dateFinStock :
                return self.quantiteEstimee_kg_ou_piece()/nbSemEcoulementStock
            else:
                return 0
        else:
            ## legume frais 
            if self.enPlaceEnDatedu(dateDebutSem):
                return self.quantiteEstimee_kg_ou_piece() / (self.etalementRecolte_j / 7)
            else:
                return 0
            
    
    
    def quantiteTotale(self):
        """cumul de toutes les quantités des implantations"""
        qte = sum(self.implantations.all().values_list("quantite",flat=True))
        return qte
               
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



class Production(models.Model):
    """Enregisrement des productions réelles"""
    dateDebutSemaine = models.DateTimeField("date de début de semaine")
    prod = models.PositiveIntegerField("quantité produite", default=0)
    legume = models.ForeignKey(Legume)
    
    class Meta: 
        ordering = ['dateDebutSemaine']
        
    def __unicode__(self):
        return "Production de %s, semaine du %s, %d %s"%(self.dateDebutSemaine, 
                                                         self.legume.nom(),
                                                         self.prod, 
                                                         self.legume.espece.nomUniteProd())
