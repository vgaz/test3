# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy

from django.template.defaultfilters import random

import sys

from main import forms, constant, planification
import MyTools

import datetime

from main.models import *
from main.forms import PlancheForm

#################################################


def home(request):
    l_planches = Planche.objects.all()
    return render(request,
                 'main/home.html',
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
                                 int(request.POST.get("largeur_cm"))/100, 
                                 bSerre,
                                 s_nom = "%s_%s_%s"%(champOuSerre,
                                                   request.POST.get("prefixe", "PL"),
                                                   str(index) )
                                 )
            s_msg += str(pl)
            print (pl)
    l_planches = Planche.objects.all().order_by('nom')

    return render(request,
                 'main/creation_planches.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "l_planches":l_planches,
                  "s_msg": s_msg
                  })
    
#########################################################"
    
def chronoPlanches(request):

    try:    
        print(request.POST)
        s_msg = ""
        delta12h = datetime.timedelta(hours=12)
        date_du_jour = datetime.datetime.now()
    
        if request.POST.get("date_debut_vue",""):
            date_debut_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_debut_vue", ""))
            date_fin_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_fin_vue", "")) + delta12h
        else:
            delta = datetime.timedelta(days=60)
            date_debut_vue = date_du_jour - delta
            date_fin_vue = date_du_jour + delta + delta12h
            
        decalage_j = int(request.POST.get("decalage_j", 10))
        delta = datetime.timedelta(days = decalage_j)
        if request.POST.get("direction", "") == "avance":
            date_debut_vue += delta 
            date_fin_vue += delta
            
        if request.POST.get("direction", "") == "recul":
            date_debut_vue -= delta 
            date_fin_vue -= delta
        
        
        if not request.POST.get("date_debut_vue",""):
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
        
        s_id_planches = request.POST.get("id_planches", request.GET.get("id_planches", ""))
#         if s_noms:
#             l_noms = [int(num.strip()) for num in s_noms.strip(',').split(",")]
#             l_planches = Planche.objects.filter(num__in = l_noms).order_by('nom')

    except:
        s_msg += str(sys.exc_info())
        return render(request, 'main/erreur.html',  
                      {"appVersion":constant.APP_VERSION, 
                       "appName":constant.APP_NAME, 
                       "message":s_msg}
                      )
    ## juste pour test wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
#     l_planches = Planche.objects.filter(id__in=[1,3,5,6,7])
    
    ## ajout des séries présentes pour chaque planche
    for laPlanche in l_planches:
        laPlanche.l_series = Serie.objects.activesSurPeriode(date_debut_vue, date_fin_vue, laPlanche)
        ## ajout de l'implation spécifique à cette planche (il ne peut y avoir qu'une implantation de serie par planche)
        for serie in laPlanche.l_series:
            serie.implantationPlanche = serie.implantations.get(planche_id=laPlanche.id)
            
            
    return render(request,
                 'main/chrono_planches.html',
                 {
                    "appVersion": constant.APP_VERSION,
                    "appName": constant.APP_NAME,
                    "l_planches": l_planches,
                    "selection_serres":bSerres,
                    "selection_champs":bChamps,
                    "d_evtTypes": Evenement.D_NOM_TYPES,
                    "codeEvtDivers":Evenement.TYPE_DIVERS,
                    "l_especes": Espece.objects.all(),
                    "l_vars": Variete.objects.all(),                  
                    "date_debut_vue": date_debut_vue,
                    "date_fin_vue": date_fin_vue,
                    "date_du_jour": date_du_jour,
                    "decalage_j": decalage_j,
                    "s_msg":s_msg
                  })
        
#########################################################"
#     
# def placementSeries(request):
# 
#     try:    
#         print(request.POST)
#         s_msg = ""
#         delta12h = datetime.timedelta(hours=12)
#         date_du_jour = datetime.datetime.now()
#     
#         if request.POST.get("date_debut_vue",""):
#             date_debut_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_debut_vue", ""))
#             date_fin_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_fin_vue", "")) + delta12h
#         else:
#             delta = datetime.timedelta(days=60)
#             date_debut_vue = date_du_jour - delta
#             date_fin_vue = date_du_jour + delta + delta12h
#             
#         decalage_j = int(request.POST.get("decalage_j", 10))
#         delta = datetime.timedelta(days = decalage_j)
#         if request.POST.get("direction", "") == "avance":
#             date_debut_vue += delta 
#             date_fin_vue += delta
#             
#         if request.POST.get("direction", "") == "recul":
#             date_debut_vue -= delta 
#             date_fin_vue -= delta
#         
#         
#         if not request.POST.get("date_debut_vue",""):
#             bSerres = True
#             bChamps = True
#         else:
#             bSerres = request.POST.get("serres", )=="on"
#             bChamps = request.POST.get("champs", )=="on"
#         
#         if not bSerres and not bChamps: l_planches = Planche.objects.filter(id=0)
#         elif bSerres and not bChamps: l_planches = Planche.objects.filter(bSerre = True)
#         elif not bSerres and bChamps: l_planches = Planche.objects.filter(bSerre = False)
#         else: l_planches = Planche.objects.all()
#         
#         l_planches = l_planches.order_by('nom')
#         
#         s_id_planches = request.POST.get("id_planches", request.GET.get("id_planches", ""))
# 
#     except:
#         s_msg += str(sys.exc_info())
#         return render(request, 'main/erreur.html',  
#                       {"appVersion":constant.APP_VERSION, 
#                        "appName":constant.APP_NAME, 
#                        "message":s_msg}
#                       )
# 
#     ## ajout des séries présentes pour chaque planche
#     for laPlanche in l_planches:
#         laPlanche.l_series = Serie.objects.activesSurPeriode(date_debut_vue, date_fin_vue, laPlanche)
#         ## ajout de l'implation spécifique à cette planche (il ne peut y avoir qu'une implantation de serie par planche)
#         for serie in laPlanche.l_series:
#             serie.implantationPlanche = serie.implantations.get(planche_id=laPlanche.id)
#             
#     return render(request,
#                  'main/placement_series.html',
#                  {
#                     "appVersion": constant.APP_VERSION,
#                     "appName": constant.APP_NAME,
#                     "l_planches": l_planches,
#                     "selection_serres":bSerres,
#                     "selection_champs":bChamps,
#                     "d_evtTypes": Evenement.D_NOM_TYPES,
#                     "codeEvtDivers":Evenement.TYPE_DIVERS,
#                     "l_especes": Espece.objects.all(),
#                     "l_vars": Variete.objects.all(),                  
#                     "date_debut_vue": date_debut_vue,
#                     "date_fin_vue": date_fin_vue,
#                     "date_du_jour": date_du_jour,
#                     "decalage_j": decalage_j,
#                     "s_msg": s_msg
#                   })

def evenementsPlanches(request):

    delta20h = datetime.timedelta(hours=20)
    date_du_jour = datetime.datetime.now()
    if request.POST.get("aujourdhui","off") == "on":
        date_debut_vue = date_du_jour
        date_fin_vue = date_du_jour
        print(date_debut_vue, date_fin_vue)
    elif request.POST.get("date_debut_vue",""):
        date_debut_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_debut_vue", ""))
        date_fin_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_fin_vue", "")) + delta20h
    else:
        delta = datetime.timedelta(days=60)
        date_debut_vue = date_du_jour - delta
        date_fin_vue = date_du_jour + delta + delta20h
    
    decalage_j = int(request.POST.get("decalage_j", 10))
    delta = datetime.timedelta(days = decalage_j)
    if request.POST.get("direction", "") == "avance":
        date_debut_vue += delta 
        date_fin_vue += delta
    if request.POST.get("direction", "") == "recul":
        date_debut_vue -= delta 
        date_fin_vue -= delta        
    
    ## on prend tous les evts de l'encadrement
    l_evts = Evenement.objects.filter(date__gte = date_debut_vue, 
                                      date__lte = date_fin_vue)
    for evt in l_evts:
        ## on ajoute les numeros de planche
        serie = evt.serie_set.all()[0]
        evt.l_planches = [imp.planche for imp in serie.implantations.all()]
        for pl in evt.l_planches:
            print (evt, pl.nom)

    return render(request,
                 'main/evenements.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "l_evts": l_evts,
                  "date_debut_vue": date_debut_vue,
                  "date_fin_vue": date_fin_vue,
                  "date_du_jour": date_du_jour,
                  "decalage_j": decalage_j
                  })
    
#################################################

class CreationPlanche(CreateView):
    
    model = Planche
    form_class = PlancheForm
    template_name = 'main/creation_planche.html'
    success_url = reverse_lazy('creation_planche')
    http_method_names = ['get', 'post']
    
    def get_initials(self):
        return {  "appVersion":constant.APP_VERSION,
                  "appName":constant.APP_NAME
                }
    
    def dispatch(self, *args, **kwargs):
        return super(CreationPlanche, self).dispatch(*args, **kwargs)

#################################################
# 
# def editionPlanche(request):
# 
#     planche = Planche.objects.get(id = int(request.GET.get("id_planche", 0)))
#     s_date = request.POST.get("date", "")
#     if s_date:
#         dateVue = datetime.datetime.strptime(s_date, constant.FORMAT_DATE)
#     else:
#         dateVue = datetime.datetime.now()
#         
#     if request.POST.get("delta", "") == "+1":
#         dateVue += datetime.timedelta(days=1)
#     if request.POST.get("delta", "") == "-1":
#         dateVue += datetime.timedelta(days=-1)
#     if request.POST.get("delta", "") == "+10":
#         dateVue += datetime.timedelta(days=10)
#     if request.POST.get("delta", "") == "-10":
#         dateVue += datetime.timedelta(days=-10)
# 
#     l_series = recupListeSeriesEnDateDu(dateVue, planche.id)
# 
#     return render(request,
#                  'main/edition_planche.html',
#                  {
#                   "appVersion":constant.APP_VERSION,
#                   "planche":planche,
#                   "l_vars":Variete.objects.all(),
#                   "l_evtTypes":Evenement.D_NOM_TYPES.items(),
#                   "d_evtTypes":Evenement.D_NOM_TYPES,
#                   "l_series":l_series,
#                   "date":dateVue
#                   })

#################################################

def prevision_recolte(request):
    
    ## récup de la fenetre de temps
    delta20h = datetime.timedelta(hours=20)
    date_du_jour = datetime.datetime.now()
    if request.POST.get("date_debut_vue",""):
        date_debut_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_debut_vue", ""))
        date_fin_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_fin_vue", "")) + delta20h
    else:        
        delta = datetime.timedelta(days=30)
        date_debut_vue = date_du_jour - delta
        date_fin_vue = date_du_jour + delta + delta20h
    date_debut_sem_vue = date_debut_vue - datetime.timedelta(days=date_debut_vue.weekday()) 
    date_fin_sem_vue = date_fin_vue + datetime.timedelta(days = 6 - date_fin_vue.weekday()) 
            
    ## sauvegarde des prévisions des récoltes
 ##   planification.enregistrePrevisions(request)
        
#     if request.POST.get("option_planif", ""):
#         planification.planif(date_debut_sem_vue, date_fin_sem_vue)
    
    ## création de la liste des semaines     
    # on recadre sur le lundi pour démarrer en debut de semaine
    l_semaines = []
    date_debut_sem = date_debut_sem_vue
        
    while True:
        sem = MyTools.MyEmptyObj()
        date_fin_sem = date_debut_sem + datetime.timedelta(days=6)
        sem.date_debut_iso = date_debut_sem.isocalendar()
        sem.date_debut = date_debut_sem
        sem.date_fin = date_fin_sem
        l_semaines.append(sem)
        if date_fin_sem >= date_fin_vue: 
            break
        date_debut_sem = date_fin_sem + datetime.timedelta(days=1)

    ## recherche des productions par semaine regroupées par légume
    l_legumes = Legume.objects.all()
    for leg in l_legumes:
        ## calcul des productions de légumes
        l_series = Serie.objects.activesSurPeriode(date_debut_sem_vue, date_fin_sem_vue) ## on ne garde que la fenetre de temps étudiée
        l_series = l_series.filter(legume_id = leg.id) ## on ne garde que les series du legume concerné
        ## Pour chaque semaine étudiée, on calcule le stock cumulé de chaque série 
        ## le stock est lissé 
        ## sur la conso hebdo pour les légumes stockables
        ## ou sur la durée de récolte pour les légumes non stockables
        leg.l_prod = []
        for sem in l_semaines:
            prodHebdo = 0
            for serie in l_series:
                prodHebdo += serie.prodHebdo(date_debut_sem)
            leg.l_prod.append((sem.date_debut, prodHebdo))
        
        
    return render(request,
                 'main/prevision_recolte.html',
                 {
                  "appVersion":constant.APP_VERSION,
                  "date_debut_vue": date_debut_vue,
                  "date_fin_vue": date_fin_vue,
                  "l_vars":Variete.objects.all().order_by("espece"),
                  "l_semaines":l_semaines,
                  "l_legumes":l_legumes,
                  "info":""
                  })
    
#################################################

def tab_legumes(request):
    s_info = ""
    try:
        l_legumes = Legume.objects.all()
        if request.POST:
            for leg in l_legumes:
                s_pk = "leg_%s_"% str(leg.pk)
                print(s_pk)
                leg.rendementProduction_kg_m2 = float(request.POST.get(s_pk + "rendementProduction_kg_m2", 0))
                leg.rendement_plants_graines_pourcent = int(request.POST.get(s_pk + "rendement_plants_graines_pourcent",100))
                leg.intra_rang_m = float(request.POST.get(s_pk + "intra_rang_cm", 0)/100)
                leg.inter_rang_m = float(request.POST.get(s_pk + "inter_rang_cm", 0)/100)
                leg.save()
        
        l_fams = Famille.objects.all()
        for fam in l_fams:
            l_esp = Espece.objects.filter(famille_id = fam.id)
            fam.l_especes = l_esp

    except:
        s_info += str(sys.exc_info()[1])
        
    return render(request,
                 'main/tab_legumes.html',
                 {
                  "appVersion":constant.APP_VERSION,
                  "l_legumes":l_legumes,
                  "l_fams":l_fams,
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

        message += "%s, la/le %s est de la famille des %ss" % (s_rep, espece.nom, espece.famille.nom)

        ## restart a new form
        form = forms.FormFamilyQuiz()

    form.esp = random(Espece.objects.filter(famille__isnull=False).values("nom", "id"))

    return render(request, 'main/quizFamilles.html',
            {
             "color":color,
             "message" : message,
             "form": form,
             "appVersion": constant.APP_VERSION
            }
          )  
    
    


#################################################
