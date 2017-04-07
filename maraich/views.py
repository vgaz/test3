# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy

from django.template.defaultfilters import random

import os, sys

from maraich import forms, constant, settings
from maraich.settings import log
import MyTools
from MyHttpTools import getFloatInPost
import datetime

from maraich.models import *
from maraich.forms import PlancheForm

 
def donnePeriodeVue(reqPost):

    date_aujourdhui = datetime.datetime.now()
    periode = reqPost.get("periode","mois")
    if periode == "specifique":
        date_debut_vue = MyTools.getDateFrom_d_m_y(reqPost.get("date_debut_vue", ""))
        date_fin_vue = MyTools.getDateFrom_d_m_y(reqPost.get("date_fin_vue", ""))
    elif periode == "annee":
        date_premierJour = MyTools.getDateFrom_d_m_y("1/1/%s"%date_aujourdhui.year)
        delta = datetime.timedelta(days=365)
        date_debut_vue = date_premierJour
        date_fin_vue = date_premierJour + delta
    elif periode == "mois":
        date_premierJour = MyTools.getDateFrom_d_m_y("1/%s/%s"%(date_aujourdhui.month, date_aujourdhui.year))
        delta = datetime.timedelta(days=30)
        date_debut_vue = date_premierJour
        date_fin_vue = date_premierJour + delta
    elif periode == "semaine":
        delta = datetime.timedelta(days=6)
        date_debut_vue =  date_aujourdhui - datetime.timedelta(days=date_aujourdhui.weekday())
        date_fin_vue = date_debut_vue + delta
    else:
        assert False, "pas de periode trouvee"
        
    decalage_j = reqPost.get("decalage_j","")
    if not decalage_j:
        decalage_j = 30
    else:
        decalage_j = int(decalage_j)
    delta = datetime.timedelta(days = decalage_j)
    if reqPost.get("direction", "") == "avance":
        date_debut_vue += delta 
        date_fin_vue += delta
        periode = "specifique"
        
    if reqPost.get("direction", "") == "recul":
        date_debut_vue -= delta 
        date_fin_vue -= delta   
        periode = "specifique"
          
    return(periode, date_debut_vue, date_fin_vue, decalage_j)

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
        decalage_j = 0
        date_aujourdhui = datetime.datetime.now()
        
        print(request.POST)
        s_msg = ""

        periode, date_debut_vue, date_fin_vue, decalage_j = donnePeriodeVue(request.POST) 
          
        if not request.POST.get("periode",""):
            bSerres = True
            bChamps = True
        else:
            bSerres = request.POST.get("serres", )=="on"
            bChamps = request.POST.get("champs", )=="on"
        
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

        
        filtreLeg = request.POST.get("s_filtre_legumes","")

        for planche in l_planches:
            planche.l_implantations = []
            l_series = Serie.objects.activesSurPeriode(date_debut_vue, 
                                                        date_fin_vue, 
                                                        planche)
            if filtreLeg:
                l_series = l_series.filter(legume__espece__nom__icontains = filtreLeg)
            ## ajout de l'implation spécifique à cette planche (il ne peut y avoir qu'une implantation de série par planche)
            for serie in l_series:
                planche.l_implantations.append(serie.implantations.get(planche_id=planche.id))

    except:
        s_msg += str(sys.exc_info())
  
    return render(request,
                 'maraich/suivi_implantations.html',
                 {
                    "appVersion": constant.APP_VERSION,
                    "appName": constant.APP_NAME,
                    "periode":periode,
                    "date_debut_vue": date_debut_vue,
                    "date_fin_vue": date_fin_vue,
                    "decalage_j": decalage_j,
                    "selection_serres":bSerres,
                    "selection_champs":bChamps,
                    "s_filtre_planches":s_filtre_planches,
                    "s_filtre_legumes":filtreLeg,
                    "l_planches": l_planches,
                    "l_semaines":MyTools.getListeSemaines(date_debut_vue, date_fin_vue),
                    "d_evtTypes": Evenement.D_NOM_TYPES,
                    "codeEvtDivers":Evenement.TYPE_DIVERS,
                    "l_legumes": Legume.objects.all(),
                    "date_du_jour": date_aujourdhui,
                    "s_msg":s_msg,
                    "doc":constant.DOC_CHRONOVIEW
                  })
        


def evenementsPlanches(request):

    ## récup de la fenetre de temps
    try:
        periode, date_debut_vue, date_fin_vue, decalage_j = donnePeriodeVue(request.POST)
    except:
        pass 
   
    ## recup des evenements
    for k, v in request.POST.items():
        print(k,v)
        if "evt_fin_" in k:
            pk_evt = int(k.split("evt_fin_")[1])
            evt = Evenement.objects.get(pk = pk_evt)
            evt.b_fini = True
            evt.save()
            
    ## on prend tous les evts de l'encadrement
    l_evts = Evenement.objects.filter(date__gte = date_debut_vue, date__lte = date_fin_vue)
    
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
    
    return render(request,
                 'maraich/evenements.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "l_evts": l_evts,
                  "date_debut_vue": date_debut_vue,
                  "date_fin_vue": date_fin_vue,
                  "date_aujourdhui": datetime.datetime.now(),
                  "decalage_j": decalage_j,
                  "periode":periode,
                  "bEncours":bEncours
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
        bDetailVar = request.POST.get("detail_variete", "") != ""
        ## récup de la fenetre de temps
        periode, date_debut_vue, date_fin_vue, decalage_j = donnePeriodeVue(request.POST) 
        bSerres = request.POST.get("bSerres","")=="on"
        bChamps = request.POST.get("bChamps","")=="on"

        nbPanniers = Espece.objects.get(nom="ail").nbParts
        l_semaines = MyTools.getListeSemaines(date_debut_vue, date_fin_vue)

        ## on ne garde que la fenetre de temps étudiée
        l_seriesActives = Serie.objects.activesSurPeriode(date_debut_vue, date_fin_vue) 
        ## recherche des productions par semaine regroupées par légume ou par espèce
        l_legumes = Legume.objects.all()
        for leg in l_legumes:
 
            ## calcul des productions de légumes
            l_series = l_seriesActives.filter(legume_id = leg.id)
            if bSerres and not bChamps:
                l_series = l_series.filter(bSerre = True)
            elif bChamps and not bSerres:
                l_series = l_series.filter(bSerre = False)

            ## Pour chaque semaine étudiée, on calcule le stock cumulé de chaque série 
            ## le stock est lissé 
            ## soit sur la conso hebdo pour les légumes stockables
            ## ou sur la durée de récolte pour les légumes non stockables
            leg.l_prod = []
            for sem in l_semaines:
                qteHebdo = 0
                for serie in l_series:
                    qteHebdo += serie.prodHebdo(sem.date_debut)
                    print("sem %s ******************* leg %s, %s %f"%(sem.s_dm, leg.nom(), sem.date_debut, qteHebdo))
                  
                if qteHebdo == 0:
                    couleur = "white"
                else:
                    couleur = leg.espece.couleur
                
                try: 
                    prodReelle = Production.objects.get(legume_id=leg.id, dateDebutSemaine = sem.date_debut).qte
                except:
                    prodReelle = 0
                    
                leg.l_prod.append((sem.date_debut, 
                                   int(qteHebdo), 
                                   int(leg.poids_kg(qteHebdo)),
                                   leg.espece.nomUniteProd(),
                                   couleur,
                                   prodReelle))

    except:
        s_info += str(sys.exc_info()[1])
        log.error(s_info)
        
    return render(request,'maraich/recolte.html',
                    {
                    "appVersion":constant.APP_VERSION,
                    "periode":periode,
                    "decalage_j":decalage_j,
                    "date_debut_vue": date_debut_vue,
                    "date_fin_vue": date_fin_vue,
                    "bSerres":bSerres,
                    "bChamps":bChamps,
                    "l_semaines":l_semaines,
                    "l_legumes":l_legumes,
                    "l_especes" : Espece.objects.all(),
                    "bDetailVar":bDetailVar,
                    "nbPanniers":nbPanniers,
                    "info":s_info
                    })
    
#################################################

def utilisationPlanches(request):
    """affiche les surfaces occupées par planche"""
    try:
        s_info = ""
        ## récup de la fenetre de temps
        periode, date_debut_vue, date_fin_vue, decalage_j = donnePeriodeVue(request.POST)  
        l_jours = MyTools.getListeJours(date_debut_vue, date_fin_vue)

        ## on retire les planches virtuelles
 #       l_planches = Planche.objects.filter(nom__in = [constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS])
        l_planches = Planche.objects.filter(nom__in = [constant.NOM_PLANCHE_VIRTUELLE_PLEIN_CHAMP, constant.NOM_PLANCHE_VIRTUELLE_SOUS_ABRIS])
#         l_planches = Planche.objects.all()
        bSerres = request.POST.get("bSerres","")=="on"
        if not bSerres:
            l_planches = l_planches.exclude(bSerre = True)
        bChamps = request.POST.get("bChamps","")=="on"
        if not bChamps:
            l_planches = l_planches.exclude(bSerre = False)
        
        ## recup de tous les évenements de début ou fin de série 
        l_evts = Evenement.objects.filter(type__in=[Evenement.TYPE_DEBUT, Evenement.TYPE_FIN])
        l_evts = l_evts.filter(date__gte=date_debut_vue, date__lte=date_fin_vue)
        print( len(l_evts))
        
#         l_dates= []
#         for evt in l_evts:
#             if evt.date not in l_dates:
#                 l_dates.append(evt.date+datetime.timedelta(days=-1))
# #                 l_dates.append(evt.date)
#                 l_dates.append(evt.date+datetime.timedelta(days=1))
        
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
                    "periode":periode,
                    "decalage_j":decalage_j,
                    "date_debut_vue": date_debut_vue,
                    "date_fin_vue": date_fin_vue,
                    "l_jours":l_jours,
                    "l_planches":l_planches,
                    "bSerres":bSerres,
                    "bChamps":bChamps,
                    "info":s_info
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
