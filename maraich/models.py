# -*- coding: utf-8 -*-
from django.db import models as djangoModels
import datetime, sys
from django.utils import timezone
from maraich import constant
from maraich.settings import log
import MyTools
 
###############################################################
### contrôle des models
 
def creationEvtAbs(e_date, e_type, nom="", duree_j=1):
    """création d'un evenement avec une date absolue
    retourne l'instance de l'évènement""" 
    evt = Evenement()
    ## on ajoute 12 h à l'evt de debut pour eviter les pbs d'encadrement
    evt.date = e_date + datetime.timedelta(hours=12)
    evt.eRef_id = 0
    evt.type = e_type
    evt.duree_j = duree_j
    evt.nom = nom
    evt.save()
    return evt
 
def creationEvtRel(eRef, delta_j, e_type, nom="", duree_j=1):
    """création d'un evenement relatif
    retourne l'instance de l'évènement""" 
    
    assert isinstance(eRef, Evenement) , "Pas de reference pour la création d'un evt relatif"
    evt = Evenement()
    evt.eRef_id = eRef.id
    evt.delta_j = delta_j
    evt.type = e_type
    evt.duree_j = duree_j
    evt.nom = nom
    evt.save()
    return evt
 
 
def creationEditionSerie(d_req):
    """Création ou edition d'une série de plants sur planche virtuelle
    si id_serie == 0, c'est une demande de création, sinon , d'édition/modification
    """
    id_serie = MyTools.getIntInDict(d_req, "id_serie", "0", log)
    intra_rang_m = MyTools.getFloatInDict(d_req, "intra_rang_cm", "0", log)/100
    nb_rangs = MyTools.getIntInDict(d_req, "nb_rangs", "0", log)
    id_leg = MyTools.getIntInDict(d_req, "id_legume", "0", log)
    assert id_leg, '%s pas de valeur pour id_leg'
    bSerre = d_req.get("b_serre","false")=="true"
    nb_pieds = MyTools.getIntInDict(d_req, "nb_pieds", "0", log)
    s_dateEnTerre = d_req.get("date_debut")
    duree_fab_plants_j = MyTools.getIntInDict(d_req, "duree_fab_plants_j","0", log)
    duree_avant_recolte_j = MyTools.getIntInDict(d_req, "duree_avant_recolte_j","0", log)
    assert duree_avant_recolte_j != 0, 'duree avant recolte = 0'
    etalement_recolte_j = MyTools.getIntInDict(d_req, "etalement_recolte_j", "0", log)
    assert etalement_recolte_j != 0, 'étalement recolte = 0'
    
    leg = Legume.objects.get(id=id_leg)
    bNelleSerie = id_serie == 0 or d_req.get("cde","")=="clone_serie"
    if bNelleSerie:
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
    
    serie.save()
    serie.fixeDates(s_dateEnTerre, duree_avant_recolte_j, etalement_recolte_j, duree_fab_plants_j)
    
    if bNelleSerie:
        ## implantation nouvelle pour nelle série
        impl = Implantation()
        if bSerre:
            impl.planche = Planche.objects.get(nom=constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS)
        else:
            impl.planche = Planche.objects.get(nom=constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP)
        impl.nbPieds = nb_pieds
        impl.save()
        serie.implantations.add(impl)
        
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
    l_series_presentes = Serie.objects.activesSurPeriode(date_debut, date_fin, planche)
    
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
    """ estimation de la surface pour une quantité de pieds implantables sur une planche """
    return int(quantite * intraRang_m / nbRangs * largeurPlanche_m)
    
    
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

class Famille(djangoModels.Model):
    """famille associée à une ou plusieurs espèces"""
    nom = djangoModels.CharField("Nom de la famille", max_length=100)
    
    class Meta: 
        ordering = ['id']
        
    def __unicode__(self):
        return self.nom

    def __str__(self):
        return self.__unicode__()
    
    def especes(self):
        """retourne la liste des espèces concernées par cette famille"""
        return self.espece_set.all()


class Planche(djangoModels.Model):
    """ planche de culture"""
    nom = djangoModels.CharField(max_length=100, blank=True, default="")
    longueur_m = djangoModels.IntegerField()
    largeur_m = djangoModels.FloatField()
    bSerre = djangoModels.BooleanField(default=False)
    
    class Meta: 
        ordering = ['nom']
        
    def surface_m2(self):
        return self.longueur_m * self.largeur_m

    def __str__(self):
        if self.bSerre: s_lieu = "sous serre"
        else:           s_lieu = "plein champ"
        return "%s (%d), %d m x %.1f m = %d m2; %s" % ( self.nom, 
                                                        self.id, 
                                                        self.longueur_m, 
                                                        self.largeur_m,
                                                        self.surface_m2(), 
                                                        s_lieu)

class VarieteManager(djangoModels.Manager):
    
    def create_variete(self, nom):
        variete = self.create(nom=nom)
        # do something if needed
        return variete
          
class Variete(djangoModels.Model):
    """Variété"""
    nom = djangoModels.CharField(max_length=100)
    objects = VarieteManager()
    
    class Meta: 
        ordering = ['nom']
            
    def __str__(self):
        return self.nom
    
class Espece(djangoModels.Model):
    """Espèce de légume"""
    nom = djangoModels.CharField(max_length=100)
    varietes = djangoModels.ManyToManyField(Variete)
    famille = djangoModels.ForeignKey("Famille", null=True, blank=True)
    avec = djangoModels.ManyToManyField("self", related_name="avec", blank=True)
    sans = djangoModels.ManyToManyField("self", related_name="sans", blank=True)
    unite_prod = djangoModels.PositiveIntegerField(default=constant.UNITE_PROD_KG)
    bStockable = djangoModels.BooleanField(default=False)
    nbGrainesParPied = djangoModels.PositiveIntegerField("Nb graines par pied", default=0)
    rendementPousseEtConservation = djangoModels.FloatField("Rendement de pousse et conservation", default=0)
    rendementGermination = djangoModels.FloatField("Rendement germination", default=0)
    consoHebdoParPart = djangoModels.FloatField("quantité consommée par semaine par part", default=0)
    nbParts = djangoModels.PositiveIntegerField("Nb de parts à servir", default=0)
    couleur = djangoModels.CharField(max_length=16, default="yellow")
    delai_avant_retour_an = djangoModels.PositiveIntegerField("Délai avant retour de la même culture", default=3)
    volume_motte_cm3 = djangoModels.PositiveIntegerField("volume de la motte ou alvéole associée", default=0)           ### 0 = semis
    
    class Meta:
        ordering = ['nom']
 
    def __str__(self):
        return self.nom                    
 
    def nomUniteProd(self):
        return constant.D_NOM_UNITE_PROD[self.unite_prod]

    def consoHebdoTotale(self):
        return self.nbParts * self.consoHebdoParPart
    
    def bEnMottes(self):
        return self.volume_motte_cm3 != 0

class Panniers(djangoModels.Model):
    """Quantité de panniers au fil du temps"""
    val = djangoModels.PositiveIntegerField("Nb de parts ou panniers à servir par semaine", default=0)
    dateDebut = djangoModels.DateTimeField("date d'engagement de cette quantité de panniers")
    
    class Meta: 
        ordering = ['dateDebut'] ## pour lister du plus ancien au plus recent 

    def __str__(self):
        return "%d panniers à partir du %s"%(self.val, self.dateDebut)
    
    def quantiteEnDateDu(self, in_date):
        l_qtes = Panniers.objets.filter(dateDebut__lte = in_date)
        ## on renvoie le dernier
        return l_qtes[-1].val

      
class Legume(djangoModels.Model):
    """légume"""
    espece = djangoModels.ForeignKey(Espece)
    variete = djangoModels.ForeignKey(Variete)
    prodParPied_kg = djangoModels.FloatField("Production par pied (kg)")
    poidsParPiece_kg = djangoModels.FloatField("Poids estimé par pièce (Kg)", default=0)
    intra_rang_m = djangoModels.FloatField("distance dans le rang (m)", default=0)
    
    class Meta:
        ordering = ['espece', 'variete']
            
    def __str__(self):
        return "%s"%(self.nom())

    def intraRang_cm(self):
        return int(self.intra_rang_m * 100)                    
 
    def nom(self):
        return "%s %s"%(self.espece.nom, self.variete.nom)

    def poids_kg(self, qte):
        """Retourne la quantité en kg avec conversion éventuelle pièce > Kg
            pour les légumes vendus à la pièce"""
        if self.espece.unite_prod == constant.UNITE_PROD_PIECE:
            return (qte * self.poidsParPiece_kg)
        else:
            return (qte)

    def poidsParPiece_g(self):
        return int(self.poidsParPiece_kg*1000)


class Implantation(djangoModels.Model):
    """Implantation sur une planche donnée"""
    planche = djangoModels.ForeignKey("Planche")
    nbPieds = djangoModels.IntegerField("nombre de pieds", default=0)

    def longueur_m(self):
        return self.fin_m - self.debut_m

    def serie(self):
        """ retourne la série (unique) d'appartenance"""
        return self.serie_set.all()[0]
    
    def surface_m2(self):
        serie = self.serie()
        return surfacePourQuantite( self.planche.largeur_m, 
                                                   self.nbPieds, 
                                                   serie.nb_rangs, 
                                                   serie.intra_rang_m)
    def __str__(self):
        return "Implantation %d, %d pieds de %s (%d m2) sur planche %s (%d)"%( self.id, 
                                                                         self.nbPieds, 
                                                                         self.serie().legume.nom(),
                                                                         self.surface_m2(), 
                                                                         self.planche.nom,
                                                                         self.planche.id)
        
class Evenement(djangoModels.Model):
    """Evenement ayant une date relative ou absolue"""
    TYPE_DEBUT = 1
    TYPE_FIN = 2
    TYPE_RECOLTE = 3
    TYPE_DIVERS = 4
    TYPE_PREPA_PLANTS = 5
    D_NOM_TYPES = {TYPE_DEBUT:"Début", 
                   TYPE_FIN:"Fin", 
                   TYPE_RECOLTE:"Début Récolte",
                   TYPE_DIVERS:"Divers",
                   TYPE_PREPA_PLANTS:"Prépa plants en mottes"
                   }
    type =  djangoModels.PositiveIntegerField()
    eRef = djangoModels.ForeignKey("Evenement", default=0) 
    delta_j =  djangoModels.PositiveIntegerField("nb jours de decalage pour les évenements relatifs", default=0)
    date = djangoModels.DateTimeField("date de l'évenement")
    date_creation = djangoModels.DateTimeField(default=timezone.now)
    duree_j = djangoModels.PositiveIntegerField("nb jours d'activité", default=1)
    nom = djangoModels.CharField(max_length=100, default="")
    texte = djangoModels.TextField(default="")
    b_fini = djangoModels.BooleanField(default=False)

    class Meta: 
        ordering = ['date']
    
    def nomType(self):
        return self.D_NOM_TYPES[self.type]  

    def save(self,*args,**kwargs):
        self._majDelta_j()
        super(Evenement,self).save(*args,**kwargs)

    def _majDelta_j(self, delta_j=None):
        """Ajustement de la date par rapport à un decalage en jours pour les évenements relatifs"""
        if self.eRef_id:
            if delta_j:
                self.delta_j = delta_j
            self.date = self.eRef.date + datetime.timedelta(days = self.delta_j)

    def decale(self, delta_j):
        """decalage de la date de l'evt absolu ou relatif"""
        if self.eRef_id:
            self.delta_j += delta_j
        else:
            self.date += datetime.timedelta(days = delta_j)
        self.save()

    def __str__(self):
        if self.eRef_id:
            s_mode = "relatif"
        else:
            s_mode= "absolu"
        
        return "Evt %s %s (%s) %s pour %d j"%( s_mode, self.nomType(), self.id,  self.date, self.duree_j )
             
class SerieManager(djangoModels.Manager):
    
    def activesEnDateDu(self, la_date, planche=None):
        """Filtrage des séries présentes à telle date, sur telle planche"""
        l_series = Serie.objects.filter(evt_debut__date__lte = la_date, evt_fin__date__gte = la_date).distinct()
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

    def enSerreAPlantsSurPeriode(self, date_debut_vue, date_fin_vue):
        """Filtrage des séries en phase de semis en serre à plants"""
        ## recup de toutes les séries ayant un evt "plants"
        l_series = Serie.objects.filter(evenements__type = Evenement.TYPE_PREPA_PLANTS)
        l_series = l_series.exclude(evt_debut__date__lt = date_debut_vue)
        l_suppr = []
        for serie in l_series: 
            if serie.dateDebutPlants() > date_fin_vue:
                l_suppr.append(serie.id)
        l_series = l_series.exclude(id__in = l_suppr)   
        return l_series


    def supprime(self, id_serie):
        """ supression de la série et de ses champs liés"""
        try:
            serie = Serie.objects.get(id=id_serie)
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


class Serie(djangoModels.Model):
    
    class Meta:
        verbose_name = "Série de plants d'un même légume installée sur une ou plusieurs implantations"

    legume = djangoModels.ForeignKey(Legume)
    dureeAvantRecolte_j = djangoModels.IntegerField("durée min avant début de récolte (jours)", default=0)
    etalementRecolte_j = djangoModels.IntegerField("durée étalement possible de la récolte (jours)", default=0)
    nb_rangs = djangoModels.PositiveIntegerField("nombre de rangs", default=0)
    intra_rang_m = djangoModels.FloatField("distance dans le rang (m)", default=0)
    bSerre = djangoModels.BooleanField("sous serre", default=False)
    remarque = djangoModels.TextField(default="")
    implantations = djangoModels.ManyToManyField(Implantation)
    evenements = djangoModels.ManyToManyField(Evenement)
    evt_debut = djangoModels.ForeignKey(Evenement, related_name="+", null=True, default=0)
    evt_fin = djangoModels.ForeignKey(Evenement, related_name="+", null=True, default=0)
    objects = SerieManager()
    
    def dateDebutPlants(self):  
        """retourne la date de debut de fab des plants ou None"""
        try:
            return self.evenements.get(type=Evenement.TYPE_PREPA_PLANTS).date
        except:
            return None
        
    def duree_fab_plants_j(self):
        """retourne la durée de fab des plants ou None
        on inverse le signe car le delta est negatif par rapport à la date en terre"""
        try:
            return -1*self.evenements.get(type=Evenement.TYPE_PREPA_PLANTS).delta_j
        except:
            return None
    
    def enPlaceEnDatedu(self, date):  
        """retourne True ou False si série encore en terre à telle date"""
        if date >= self.evt_debut.date and date <= self.evt_fin.date:
            return True
        else:
            return False

    def dateDebutRecolte(self):  
        """retourne la date min de récolte"""
        return self.evt_debut.date + datetime.timedelta(days = self.dureeAvantRecolte_j)
        
    def recoltePossibleEnDatedu(self, date):  
        """retourne True ou False si série encore en terre à telle date"""
        if date >= self.dateDebutRecolte() and date <= self.evt_fin.date:
            return True
        else:
            return False
        
    def intraRang_cm(self):
        return int(self.intra_rang_m *100)
    
    def fixeDates(self, dateDebut, dureeAvantRecolte_j, etalementRecolte_j, delaiCroissancePlants_j=0):
        """Crée les evts de début et fin de vie des plants en terre"""
        if isinstance(dateDebut, str): 
            dateDebut = MyTools.getDateFrom_d_m_y(dateDebut)
        
        if  self.evt_debut_id == 0: 
            """création des evts de série seul l'evt de début est absolu, les autres sont calés sur evt_debut
            """
            if delaiCroissancePlants_j:
                evt_debut = creationEvtAbs(dateDebut, Evenement.TYPE_DEBUT, "plantation %s"%(self.legume.nom()))
            else:
                evt_debut = creationEvtAbs(dateDebut, Evenement.TYPE_DEBUT, "semis %s"%(self.legume.nom()))
                
            self.evenements.add(evt_debut)
            self.evt_debut_id = evt_debut.id
            
            evt_recolte = creationEvtRel(evt_debut, dureeAvantRecolte_j, Evenement.TYPE_RECOLTE, "début récolte %s"%(self.legume.nom()))
            self.evenements.add(evt_recolte)
                        
            evt_fin = creationEvtRel(evt_recolte, etalementRecolte_j, Evenement.TYPE_FIN, "fin %s"%(self.legume.nom()))
            self.evt_fin_id = evt_fin.id
            self.evenements.add(evt_fin)   

            if delaiCroissancePlants_j:     
                evt_semisMotte = creationEvtRel(evt_debut, -1 * delaiCroissancePlants_j, Evenement.TYPE_PREPA_PLANTS, "semi motte %s"%(self.legume.nom()))
                self.evenements.add(evt_semisMotte)                
        else:
            ## mise à jour des evts
            self.evt_debut.date = dateDebut
            self.evt_debut.save()
            
            evt = self.evenements.get(type=Evenement.TYPE_RECOLTE)
            evt.delta_j = dureeAvantRecolte_j
            evt.save()  
                      
            evt = self.evenements.get(type=Evenement.TYPE_FIN)
            evt.delta_j= etalementRecolte_j
            evt.save()

            try:
                evt = self.evenements.get(type=Evenement.TYPE_PREPA_PLANTS)
                evt.delta_j = ( -1 * delaiCroissancePlants_j)
                evt.save()
            except: 
                pass ## pas forcement de plants 
            
        self.dureeAvantRecolte_j = dureeAvantRecolte_j
        self.etalementRecolte_j = etalementRecolte_j            
        self.save()
 
    def nbGraines(self):
        """ retourne le nb de graines nécesaires en fonction du nb de pieds souhaité"""
        return int(self.nbPieds() * self.legume.espece.nbGrainesParPied / self.legume.espece.rendementGermination)

    def longueurRangTotal(self, intra_rang_m=None):
        """ retourne la longueur totale de tous les rangs en fonction de l'intra rang"""
        if not intra_rang_m:
            intra_rang_m = self.intra_rang_m
        assert intra_rang_m, Exception("intra_rang_m non défini")
        if self.legume.espece.bEnMottes():        
            return self.nbPieds() * intra_rang_m
        else:
            return self.nbGraines() * intra_rang_m
    
    def longueurSurPlanche_m(self, intra_rang_m=None, nb_rangs=None):
        """ retourne la longueur occupée sur la planche en fonction des distances inter-rang et dans le rang
        intra_rang_m et nb_rangs peuvent etre forcés si pas encore définis, autrement on prend les parametres prédéfinis"""
        if not intra_rang_m:
            intra_rang_m = self.intra_rang_m
        if not nb_rangs:
            nb_rangs = self.nb_rangs
        assert intra_rang_m, Exception("intra_rang_m non défini")
        assert nb_rangs, Exception("nb_rangs non défini")

        return self.longueurRangTotal(intra_rang_m) / nb_rangs
    
    def surfaceOccupee_m2(self, planche=None):
        """ retourne la surface occupée de toutes ou d'une implantation (si planche != None)"""
        surface_m2 = 0
        for impl in self.implantations.all():
            if planche and impl.planche.id != planche.id:
                continue
            surface_m2 += impl.surface_m2()
        
        return surface_m2

    def quantiteEstimee_kg_ou_piece(self):
            """Retourne la quantité totale escomptée (en kg ou pièces)""" 
            poids_kg = self.legume.prodParPied_kg * self.legume.espece.rendementPousseEtConservation * self.nbPieds()
            if not self.legume.espece.bEnMottes():
                poids_kg = poids_kg * self.legume.espece.rendementGermination
            if self.legume.espece.unite_prod == constant.UNITE_PROD_KG:
                return poids_kg
            else:
                return poids_kg / self.legume.poidsParPiece_kg
    
    def prodHebdo(self, dateDebutSem, ratio=1):
        """ renvoie la production estimée de cette semaine lissée sur le nombre de semaines de consommation possible"""
        dateDebutRecolte = self.evenements.get(type=Evenement.TYPE_RECOLTE).date
        
        dateMilieuSemaine = dateDebutSem + datetime.timedelta(days=3)## pour gerer pb jours / sem
#         dateFinSemaine = dateDebutSem + datetime.timedelta(days=6)

        prelevHebdo = self.legume.espece.consoHebdoTotale()/ratio
        ## prelevement continu selon besoin de livraison
        nbJoursEcoulementStock = max([1, int(self.quantiteEstimee_kg_ou_piece() / (prelevHebdo/7))])
        dateFinStock = self.evenements.get(type=Evenement.TYPE_RECOLTE).date + datetime.timedelta(days = nbJoursEcoulementStock) 
        if dateDebutRecolte <= dateMilieuSemaine and dateMilieuSemaine < dateFinStock :
            return prelevHebdo
        else:
            return 0        

    def nbSemainesDeRecolte(self):
        dd = (self.evt_fin.date - self.evenements.get(type=Evenement.TYPE_RECOLTE).date).days
        return dd/7
    
    def nbPieds(self):
        """cumul de tous les pieds de toutes des implantations"""
        return sum(self.implantations.all().values_list("nbPieds",flat=True))
               
    def s_listeNomsPlanches(self):
        """retourne la liste des planches de la série"""
        return ",".join(impl.planche.nom for impl in self.implantations.all())
         
    def __str__(self):       
        return "(s%d), %s, %d pieds, %d graines, %d m linéaire, %d m2 sur planche(s) [%s], tous les %d cm sur %d rangs , du %s au %s. Qté estimée : %d %ss" %( self.id,
                                                                                        self.legume.nom(),
                                                                                        self.nbPieds(),
                                                                                        self.nbGraines(),
                                                                                        self.longueurRangTotal(), 
                                                                                        self.surfaceOccupee_m2(), 
                                                                                        self.s_listeNomsPlanches(),
                                                                                        self.intraRang_cm(), self.nb_rangs,
                                                                                        MyTools.getDMYFromDate(self.evt_debut.date),
                                                                                        MyTools.getDMYFromDate(self.evt_fin.date),
                                                                                        self.quantiteEstimee_kg_ou_piece(),
                                                                                        self.legume.espece.nomUniteProd())
    def descriptif(self):
        """retourne une descriptioin complète de la série"""
        l_rep = []
        l_rep.append(self.__str__())
        if  self.dateDebutPlants():
            l_rep.append("Fabrication plants : %s"%MyTools.getDMYFromDate(self.dateDebutPlants()))
        for evt in self.evenements.all():
            l_rep.append(evt.__str__())
        for impl in self.implantations.all():
            l_rep.append(impl.__str__())
        
        l_rep.append("surface Occupée : %s m2"%(self.surfaceOccupee_m2()))
        l_rep.append("quantité estimée : %d %ss"%(self.quantiteEstimee_kg_ou_piece(), self.legume.espece.nomUniteProd()))
        l_rep.append("remarque : %s"%self.remarque)
        return "\n".join(l_rep)
    
        
    def info(self):
        return(self.__str__())

class Production(djangoModels.Model):
    """Enregisrement des productions réelles"""
    dateDebutSemaine = djangoModels.DateTimeField("Date de début de semaine")
    qte = djangoModels.PositiveIntegerField("Quantité produite", default=0)
#     legume = djangoModels.ForeignKey(Legume)
    espece = djangoModels.ForeignKey(Espece)
    
    class Meta: 
        ordering = ['dateDebutSemaine']
        
    def __unicode__(self):
        return "Production de %s, semaine du %s, %d %s"%(self.dateDebutSemaine, 
                                                         self.espece.nom(),
                                                         self.qte, 
                                                         self.espece.nomUniteProd())
