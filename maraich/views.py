# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy

from django.template.defaultfilters import random

import os, sys

from maraich import forms, constant, settings
from maraich.settings import log
import MyTools, MyHttpTools
from MyHttpTools import getFloatInPost
import datetime

from maraich.models import *
from maraich.forms import PlancheForm

 
def donnePeriodeVue(reqPost):
    
    infoPeriode = MyTools.MyEmptyObj()
    infoPeriode.date_aujourdhui = datetime.datetime.now()
    infoPeriode.periode = reqPost.get("periode","mois")
    infoPeriode.decalage_j = MyHttpTools.getIntInPost(reqPost, "decalage_j", 15)
    delta = datetime.timedelta(days = 0)    
    direc = reqPost.get("direction", "")
    
    if direc == "avance":
        infoPeriode.periode = "specifique"
        delta = datetime.timedelta(days = infoPeriode.decalage_j)    
    elif direc == "recul":
        infoPeriode.periode = "specifique"
        delta = datetime.timedelta(days = -1 * infoPeriode.decalage_j)    
   
    if infoPeriode.periode == "specifique":
        infoPeriode.date_debut_vue = MyTools.getDateFrom_d_m_y(reqPost.get("date_debut_vue", "")) +  delta
        infoPeriode.date_fin_vue = MyTools.getDateFrom_d_m_y(reqPost.get("date_fin_vue", "")) + delta
    elif infoPeriode.periode == "annee":
        date_premierJour = MyTools.getDateFrom_d_m_y("1/1/%s"%infoPeriode.date_aujourdhui.year)
        delta = datetime.timedelta(days=365)
        infoPeriode.date_debut_vue = date_premierJour
        infoPeriode.date_fin_vue = date_premierJour + delta
        infoPeriode.decalage_j = 365
    elif infoPeriode.periode == "mois":
        date_premierJour = MyTools.getDateFrom_d_m_y("1/%s/%s"%(infoPeriode.date_aujourdhui.month, infoPeriode.date_aujourdhui.year))
        delta = datetime.timedelta(days=30)
        infoPeriode.date_debut_vue = date_premierJour
        infoPeriode.date_fin_vue = date_premierJour + delta
        infoPeriode.decalage_j = 30
    elif infoPeriode.periode == "semaine":
        delta = datetime.timedelta(days=6)
        infoPeriode.date_debut_vue =  infoPeriode.date_aujourdhui - datetime.timedelta(days=infoPeriode.date_aujourdhui.weekday())
        infoPeriode.date_fin_vue = infoPeriode.date_debut_vue + delta
        infoPeriode.decalage_j = 7
    elif infoPeriode.periode == "aujourdhui":
        infoPeriode.date_debut_vue =  infoPeriode.date_aujourdhui
        infoPeriode.date_fin_vue = infoPeriode.date_aujourdhui + datetime.timedelta(hours=12)  ## car on part de 0h
    else:
        assert False, "pas de periode trouvee"
    
    return(infoPeriode)  

#################################################


def home(request):
    l_planches = Planche.objects.all()
    return render(request,
                 'maraich/home.html',
                 {
                  "appVersion":constant.APP_VERSION,
                  "appName":constant.APP_NAME,
                  "l_planches":l_planches
                  })
#################################################

def creationPlanches(request):
    """gestion de la requete de post """
    s_msg = "Création planche "
    if request.POST:
        
        quantite = int(request.POST.get("quantite", 0))        
        numPl = int(request.POST.get("num_prem"))           
        s_msg = ""
        for index in range(numPl, numPl + quantite):
            bSerre = request.POST.get("bSerre") == "on"
            if bSerre : 
                champOuSerre = "S"
            else:
                champOuSerre = "C"
            pl = creationPlanche(int(request.POST.get("longueur_m")), 
                                 float(request.POST.get("largeur_m").replace(",",".")), 
                                 bSerre,
                                 s_nom = "%s_%s_%s"%(champOuSerre,
                                                   request.POST.get("prefixe", "PL"),
                                                   str(index) )
                                 )
            s_msg += str(pl)
            print (pl)
    l_planches = Planche.objects.all().order_by('nom')

    return render(request,
                 'maraich/creation_planches.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "l_planches":l_planches,
                  "s_msg": s_msg
                  })
    
#########################################################"
    
def suiviImplantations(request):

    try:   
        s_filtre_planches = ""
        l_planches= []
        bSerres = True
        bChamps = True

        print(request.POST)
        s_msg = ""

        infoPeriode = donnePeriodeVue(request.POST) 
          
        if not request.POST.get("periode",""):
            bSerres = True
            bChamps = True
        else:
            bSerres = request.POST.get("menu_periode_option_serres", )=="on"
            bChamps = request.POST.get("menu_periode_option_champs", )=="on"
        
        if not bSerres and not bChamps: l_planches = Planche.objects.filter(id=0)
        elif bSerres and not bChamps: l_planches = Planche.objects.filter(bSerre = True)
        elif not bSerres and bChamps: l_planches = Planche.objects.filter(bSerre = False)
        else: l_planches = Planche.objects.all()
        l_planches = l_planches.order_by('nom')
        
        s_filtre_planches = request.POST.get("s_filtre_planches", request.GET.get("s_filtre_planches", ""))     
        planchesAExclure = []
        for planche in l_planches:
            if s_filtre_planches not in planche.nom:
                planchesAExclure.append(planche.id)
        l_planches = l_planches.exclude(pk__in=planchesAExclure)         

        filtreLeg = request.POST.get("s_filtre_legume","")

        l_seriesActives = Serie.objects.activesSurPeriode(infoPeriode.date_debut_vue, infoPeriode.date_fin_vue)
        if filtreLeg:
            l_seriesActives = l_seriesActives.filter(legume__espece__nom__icontains = filtreLeg)
        
        for planche in l_planches:
            planche.l_implantations = []
            
            ## ajout de l'implation spécifique à cette planche (il ne peut y avoir qu'une implantation de série par planche)
            for serie in l_seriesActives:
                try:
                    impl = serie.implantations.get(planche_id=planche.id)
                    planche.l_implantations.append(impl)
                except:
                    pass

    except:
        s_msg += str(sys.exc_info())
  
    return render(request,
                 'maraich/suivi_implantations.html',
                 {
                    "appVersion": constant.APP_VERSION,
                    "appName": constant.APP_NAME,
                    "infoPeriode":infoPeriode,
                    "selection_serres":bSerres,
                    "selection_champs":bChamps,
                    "s_filtre_planches":s_filtre_planches,
                    "s_filtre_legume":filtreLeg,
                    "l_planches": l_planches,
                    "l_semaines":MyTools.getListeSemaines(infoPeriode.date_debut_vue, infoPeriode.date_fin_vue),
                    "d_evtTypes": Evenement.D_NOM_TYPES,
                    "codeEvtDivers":Evenement.TYPE_DIVERS,
                    "l_legumes": Legume.objects.all(),
                    "s_msg":s_msg,
                    "doc":constant.DOC_CHRONOVIEW
                  })
        


def evenementsPlanches(request):
    
    s_info=""
    print(request.POST)
    ## récup de la fenetre de temps
    try:
        infoPeriode = donnePeriodeVue(request.POST)
       
        ## recup des evenements
        for k, v in request.POST.items():
            print(k,v)
            if "evt_fin_" in k:
                pk_evt = int(k.split("evt_fin_")[1])
                evt = Evenement.objects.get(pk = pk_evt).b_fini = True
                evt.save()
                
        ## on prend tous les evts de l'encadrement
        l_evts = Evenement.objects.filter(date__gte = infoPeriode.date_debut_vue, date__lte = infoPeriode.date_fin_vue)
        
        bEncours = request.POST.get("bEncours", "on")=="on"
        if bEncours:
            l_evts = l_evts.exclude(b_fini = True)
        
        ics_txt = constant.ICS_HEAD
        
        for evt in l_evts:
            ## on ajoute le commentaire sur la série
            serie = evt.serie_set.all()[0]
            evt.txt = serie.__str__()
            ics_txt += constant.ICS_ITEM%(evt.nom,
                                          evt.txt, 
                                          str(evt.date).split(" ")[0].replace("-","")+"T080000",
                                          str(evt.date).split(" ")[0].replace("-","")+"T090000")
        ics_txt += constant.ICS_QUEUE
        
        if request.POST.get("vers_fichier", ""):
            MyTools.strToFic(os.path.join(settings.BASE_DIR, "cultures.ics"), ics_txt)
    except:
        s_info += str(sys.exc_info())
            
    return render(request,
                 'maraich/evenements.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "l_evts": l_evts,
                  "infoPeriode": infoPeriode,
                  "bEncours":bEncours,
                  "info":s_info

                })
    
#################################################

class CreationPlanche(CreateView):
    
    model = Planche
    form_class = PlancheForm
    template_name = 'maraich/creation_planche.html'
    success_url = reverse_lazy('creation_planche')
    http_method_names = ['get', 'post']
    
    def get_initials(self):
        return {  "appVersion":constant.APP_VERSION,
                  "appName":constant.APP_NAME
                }
    
    def dispatch(self, *args, **kwargs):
        return super(CreationPlanche, self).dispatch(*args, **kwargs)



#################################################

def recolte(request):
    """affiche les previsions et récoltes réelles hebdo"""
    try:
        s_info = ""
        ## récup de la fenetre de temps
        infoPeriode = donnePeriodeVue(request.POST) 
        s_filtre_espece = request.POST.get("s_filtre_espece","")
        bDetailVar = request.POST.get("detail_variete", "") != ""
        nbPanniers = Espece.objects.get(nom="ail").nbParts
        l_semaines = MyTools.getListeSemaines(infoPeriode.date_debut_vue, infoPeriode.date_fin_vue)

        ## on ne garde que la fenetre de temps étudiée
        l_seriesActives = Serie.objects.activesSurPeriode(infoPeriode.date_debut_vue, infoPeriode.date_fin_vue) 
    
        ## recherche des productions par semaine et par légume
        l_especes = Espece.objects.all()
        l_legumes = Legume.objects.all()
        if s_filtre_espece:
            l_especes = l_especes.filter(nom__icontains = s_filtre_espece)
            l_legumes = l_legumes.filter(espece__in = l_especes)
        
        for leg in l_legumes:
 
            ## calcul des productions de légumes
            l_series = l_seriesActives.filter(legume_id = leg.id)

            ## Pour chaque semaine étudiée, on calcule la récolte possible de chaque série 
            ## selon le stock et la conso hebdo
            leg.l_prod = []

            for sem in l_semaines:
                qteHebdo = 0
              
                l_seriesMemeEspece = l_seriesActives.filter(legume__espece_id=leg.espece.id)
                nbSeriesMemeEspece = len(l_seriesMemeEspece)
                for serie in l_series:
                    qteHebdo += serie.prodHebdo(sem.date_debut, nbSeriesMemeEspece)
                
                if qteHebdo == 0:
                    couleur = "white"
                else:
                    couleur = leg.espece.couleur
                
                try: 
                    prodReelle = Production.objects.get(legume_id=leg.id, dateDebutSemaine = sem.date_debut).qte
                except:
                    prodReelle = 0
                    
                leg.l_prod.append((sem.date_debut, 
                                       qteHebdo, 
                                       leg.poids_kg(qteHebdo),
                                       leg.espece.nomUniteProd(),
                                       couleur,
                                       prodReelle))

    except:
        s_info += str(sys.exc_info()[1])
        log.error(s_info)
        
    return render(request,'maraich/recolte.html',
                    {
                    "appVersion":constant.APP_VERSION,
                    "infoPeriode":infoPeriode,
                    "l_semaines":l_semaines,
                    "l_legumes":l_legumes,
                    "l_especes" : l_especes,
                    "bDetailVar":bDetailVar,
                    "nbPanniers":nbPanniers,
                    "s_filtre_espece":s_filtre_espece,
                    "info":s_info
                    })
#################################################

def utilisationPlanches(request):
    """affiche les surfaces occupées par planche"""
    try:
        s_info = ""
        ## récup de la fenetre de temps
        infoPeriode = donnePeriodeVue(request.POST)  
        l_jours = MyTools.getListeJours(infoPeriode.date_debut_vue, infoPeriode.date_fin_vue)

        ## on retire les planches virtuelles
        l_planches = Planche.objects.filter(nom__in = [constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP, constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS])
        bSerres = request.POST.get("menu_periode_option_serres", "")=="on"
        if not bSerres:
            l_planches = l_planches.exclude(bSerre = True)
        bChamps = request.POST.get("menu_periode_option_champs", "")=="on"
        if not bChamps:
            l_planches = l_planches.exclude(bSerre = False)
        
        ## recup de tous les évenements de début ou fin de série 
        l_evts = Evenement.objects.filter(type__in=[Evenement.TYPE_DEBUT, Evenement.TYPE_FIN])
        l_evts = l_evts.filter(date__gte=infoPeriode.date_debut_vue, date__lte=infoPeriode.date_fin_vue)

        for pl in l_planches:        
            ## Pour chaque semaine étudiée, on calcule la surface
            pl.l_infoJours = []
            for j in l_jours:
                l_series = Serie.objects.activesEnDateDu(j)
                surface_occ_m2 = 0
                ## ajout de l'implation spécifique à cette planche
                for serie in l_series:
                    surface_occ_m2 += serie.surfaceOccupee_m2(pl)
                ratioLibre = int(100 - surface_occ_m2*100/pl.surface_m2())
                pl.l_infoJours.append((j, int(surface_occ_m2), ratioLibre))
            
    except:
        log.error(s_info)
        s_info += str(sys.exc_info()[1])
        
    return render(request,'maraich/utilisation_planches.html',
                    {
                    "appVersion":constant.APP_VERSION,
                    "infoPeriode":infoPeriode,
                    "l_jours":l_jours,
                    "l_planches":l_planches,
                    "selection_serres":bSerres,
                    "selection_champs":bChamps,
                    "info":s_info
                    })
    
#################################################

def suiviPlants(request):
    """affiche les périodes de semis et utilisation de la serre à plants"""
    class ModelePlaque(object):
        def __init__(self, t_nbAlvMax__volumeAlv_cm3):
            self.nbAlvMax = t_nbAlvMax__volumeAlv_cm3[0]
            self.volume_cm3 = t_nbAlvMax__volumeAlv_cm3[1]
            self.nbAlv = 0
        def qte(self):
            qte = self.nbAlv/self.nbAlvMax
            i_qte = int(qte)
            if qte > i_qte: 
                return i_qte+1
            return i_qte

    try:
        s_info = ""
        ## récup de la fenetre de temps
        infoPeriode = donnePeriodeVue(request.POST)  
        l_seriesIds = []
        l_semaines = []
        for sem in MyTools.getListeSemaines(infoPeriode.date_debut_vue, infoPeriode.date_fin_vue):        
            ## Pour chaque semaine étudiée, on calcule la surface
            qte = 0
            txt = "<hr/>"
            plaq24 = ModelePlaque(constant.PLAQUE_24_230)
            plaq77 = ModelePlaque(constant.PLAQUE_77_55)
            l_plaques = [plaq24, plaq77]
            
            for serie in Serie.objects.enSerreAPlantsSurPeriode(sem.date_debut, sem.date_fin):
                l_seriesIds.append(serie.id)
                qte += serie.nbPieds()
                txt += "P:%s<br/>T:%s <div class='serie' serie_id='%d' title=''>%s (S%d)</div><hr/>"%(MyTools.getDMYFromDate(serie.dateDebutPlants()),
                                             MyTools.getDMYFromDate(serie.evt_debut.date),
                                             serie.id, serie.legume.espece.nom, serie.id)
                ## calcul qté alvéoles 
                for plaq in l_plaques:
                    if plaq.volume_cm3 == serie.legume.espece.volume_motte_cm3:
                        plaq.nbAlv += serie.nbPieds()

            sem.l_plaquesSem = l_plaques
            sem.totalPlaques = sum([plaque.qte() for plaque in l_plaques])
            sem.qte = qte
            sem.txt = txt
            l_semaines.append(sem)
            
    except:
        log.error(s_info)
        s_info += str(sys.exc_info()[1])
        
    return render(request,'maraich/suivi_plants.html',
                    {
                    "appVersion":constant.APP_VERSION,
                    "infoPeriode.":infoPeriode,
                    "l_semaines":l_semaines,
                    "l_series":Serie.objects.filter(id__in = list(set(l_seriesIds))),
                    "info": s_info
                    })
    

#########################################################
def tab_legumes(request):
    """liste des légumes en base et parametres"""
    s_info = ""

    l_legumes = Legume.objects.all()
        
    return render(request,
                 'maraich/tab_legumes.html',
                 {
                  "appVersion":constant.APP_VERSION,
                  "l_legumes":l_legumes,
                  "l_fams":Famille.objects.all(),
                  "d_up":constant.D_NOM_UNITE_PROD,
                  "info":s_info
                  })
    
#################################################

def quizFamilles(request):
    
    message = ""
    color= "white"
    
    form = forms.FormFamilyQuiz(request.POST or None)

    if form.is_valid():
        
        s_espDemandee = request.POST.get('espece')
             
        repIdFam = int(request.POST.get('famChoice', -1))
        
        print('rep', repIdFam)
        
        espece = Espece.objects.get(id=s_espDemandee)

        if repIdFam == espece.famille.id:
            s_rep = "BRAVO"
            color = 'lime'
        else:
            s_rep = "PERDU"
            color= 'red'

        message = "%s, la/le %s est de la famille des %ss" % (s_rep, 
                                                               espece.nom, 
                                                               espece.famille.nom)

        ## restart a new form
        form = forms.FormFamilyQuiz()
    else:
        message = "form invalide"
        
    form.esp = random(Espece.objects.filter(famille__isnull=False).values("nom", "id"))

    return render(request, 'maraich/quiz_familles.html',
            {
             "color":color,
             "message" : message,
             "form": form,
             "appVersion": constant.APP_VERSION
            })
      
    
    


#################################################
