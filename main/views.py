# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy

from django.template.defaultfilters import random

import sys

from main import forms, constant, planification
import main.Tools.MyTools as MyTools

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
                prefixe = "S_"
            else:
                prefixe = "C_"
            pl = creationPlanche(int(request.POST.get("longueur_m")), 
                                 int(request.POST.get("largeur_cm"))/100, 
                                 bSerre,
                                 s_nom = "%s%s%s"%(prefixe,
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
        delta20h = datetime.timedelta(hours=20)
        date_du_jour = datetime.datetime.now()
    
        if request.POST.get("date_debut_vue",""):
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
            
        s_noms = request.POST.get("nom_planches", request.GET.get("nom_planches", ""))
        if s_noms:
            l_noms = [int(num.strip()) for num in s_noms.strip(',').split(",")]
            l_planches = Planche.objects.filter(num__in = l_noms).order_by('nom')
        else:
            l_planches = Planche.objects.all().order_by('nom')
    except:
        s_msg += str(sys.exc_info())
        return render(request, 'main/erreur.html',  {"appVersion":constant.APP_VERSION, "appName":constant.APP_NAME, "message":s_msg})
    
    ## ajout des séries 
    for laPlanche in l_planches:
        laPlanche.l_series = Serie.objects.activesSurPeriode(date_debut_vue, date_fin_vue, laPlanche)

    return render(request,
                 'main/chrono_planches.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "l_planches": l_planches,
                  "d_evtTypes":Evenement.D_NOM_TYPES,
                  "l_vars": Variete.objects.all(),                  
                  "date_debut_vue": date_debut_vue,
                  "date_fin_vue": date_fin_vue,
                  "date_du_jour": date_du_jour,
                  "decalage_j": decalage_j,
                  "s_msg":s_msg
                  })
        

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

def editionPlanche(request):

    planche = Planche.objects.get(id = int(request.GET.get("id_planche", 0)))
    s_date = request.POST.get("date", "")
    if s_date:
        dateVue = datetime.datetime.strptime(s_date, constant.FORMAT_DATE)
    else:
        dateVue = datetime.datetime.now()
        
    if request.POST.get("delta", "") == "+1":
        dateVue += datetime.timedelta(days=1)
    if request.POST.get("delta", "") == "-1":
        dateVue += datetime.timedelta(days=-1)
    if request.POST.get("delta", "") == "+10":
        dateVue += datetime.timedelta(days=10)
    if request.POST.get("delta", "") == "-10":
        dateVue += datetime.timedelta(days=-10)

    l_series = recupListeSeriesEnDateDu(dateVue, planche.id)

    return render(request,
                 'main/edition_planche.html',
                 {
                  "appVersion":constant.APP_VERSION,
                  "planche":planche,
                  "l_vars":Variete.objects.all(),
                  "l_evtTypes":Evenement.D_NOM_TYPES.items(),
                  "d_evtTypes":Evenement.D_NOM_TYPES,
                  "l_series":l_series,
                  "date":dateVue
                  })

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
    planification.enregistrePrevisions(request)
        
    if request.POST.get("option_planif", ""):
        planification.planif(date_debut_sem_vue, date_fin_sem_vue)
    
    ## création de la liste des semaines     
    # on recadre sur le lundi pour démarrer en debut de semaine
    l_semaines = []
    date_debut_sem = date_debut_sem_vue
    while True:
        date_fin_sem = date_debut_sem + datetime.timedelta(days=6)
        l_semaines.append((date_debut_sem.isocalendar(), date_debut_sem, date_fin_sem))
        if date_fin_sem >= date_fin_vue: 
            break
        date_debut_sem = date_fin_sem + datetime.timedelta(days=1)
    
    tab_previsions = "[" 
    for prod in Production.objects.filter(date_semaine__gte = date_debut_sem_vue, date_semaine__lte = date_fin_sem_vue):
        print (prod)
        tab_previsions += "['%s', %d, %d, %d],"%(MyTools.getYMDFromDate(prod.date_semaine), prod.variete_id, prod.qte_dde, prod.qte_prod)
    tab_previsions += "]" 

    ## calcul des productions à partir des séries dont la prodution est dans la fenetre étudiée
    l_series = Serie.objects.filter(evt_debut_date__gte = date_debut_sem_vue,
                                    evt_fin_date__lte = date_fin_sem_vue)
    
    return render(request,
                 'main/prevision_recolte.html',
                 {
                  "appVersion":constant.APP_VERSION,
                  "date_debut_vue": date_debut_vue,
                  "date_fin_vue": date_fin_vue,
                  "l_vars":Variete.objects.all(),
                  "l_semaines":l_semaines,
                  "tab_previsions":tab_previsions,
                  "info":""
                  })
    
#################################################

def tab_varietes(request):
    s_info = ""
    l_vars = []
    try:
        l_vars = Variete.objects.all()##filter(b_choisi=True)
        if request.POST:
            for v in l_vars:
                s_pk = "v_%s_"% str(v.pk)
                print(s_pk)
                v.prod_kg_par_m2 = float(request.POST.get(s_pk + "prod_kg_par_m2",0))
                v.rendement_plants_graines_pourcent = int(request.POST.get(s_pk + "rendement_plants_graines_pourcent",100))
                v.intra_rang_m = request.POST.get(s_pk + "intra_rang_cm",10)/100
                v.save()
      
    
#         for v in l_vars:
#             v.nomUniteProd = constant.D_NOM_UNITE_PROD[v.unite_prod]
#     
    except:
        s_info += str(sys.exc_info()[1])
        
    return render(request,
                 'main/tab_varietes.html',
                 {
                  "l_vars":l_vars,
                  "l_fams":Famille.objects.all(),
                  "appVersion":constant.APP_VERSION,
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
