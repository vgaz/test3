# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy

from django.template.defaultfilters import random

import sys

from main import forms, constant, planification
import main.Tools.MyTools as MyTools

import datetime

from main.models import Variete, Famille, Evenement, Planche, Plant, Production
from main.models import recupListePlantsEnDateDu, creationPlanche, creationSerie
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
    s_msg = ""
    if request.POST:
        quantite = int(request.POST.get("quantite", 0))        
        numPl = int(request.POST.get("num_prem"))           
        s_msg = ""
        for index in range(numPl, numPl + quantite):
            pl = creationPlanche(int(request.POST.get("longueur_m")), 
                                 int(request.POST.get("largeur_cm")), 
                                 request.POST.get("bSerre") == "on",
                                 s_nom = request.POST.get("prefixe", "Planche"),
                                 num = index
                                 )
            
            s_msg = "Planches créées"
            print (pl)
    
    return render(request,
                 'main/creation_planches.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "s_msg": s_msg
                  })
    
#########################################################"
    
def chronoPlanches(request):
    
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

    try:
        # gestion de la cration d'une nouvelle série de plants
        if int(request.POST.get("editSerie_id", 99999)) == 0:

            snouv = creationSerie(Planche.objects.get(num=int(request.POST.get("editSerie_num_planche"))).id, 
                                 int(request.POST.get("editSerie_id_variete")), 
                                 int(request.POST.get("editSerie_quantite")), 
                                 int(request.POST.get("editSerie_intra_rang_cm")), 
                                 int(request.POST.get("editSerie_nb_rangs")), 
                                 request.POST.get("editSerie_date_debut"), 
                                 request.POST.get("editSerie_date_fin"))
            l_evts = request.POST.get("evt_date[]")
            for index, evt in enumerate(l_evts):
                print(str(evt))
            print(snouv)
            s_msg += "Nouvelle serie créée = %s"%(snouv)
            
            
        s_nums = request.POST.get("num_planches", request.GET.get("num_planches", ""))
        if s_nums:
            l_nums = [int(num.strip()) for num in s_nums.strip(',').split(",")]
            l_planches = Planche.objects.filter(num__in = l_nums).order_by('num')
        else:
            l_planches = Planche.objects.all().order_by('num')
    except:
        s_err = sys.exc_info()[1]
        s_msg += "Planche(s) non trouvée..."
        return render(request, 'main/erreur.html',  { "appVersion":constant.APP_VERSION, "appName":constant.APP_NAME, "message":s_msg})
    
    ## ajout des evts liés à cette planche
    for laPlanche in l_planches:
        ## on prend tous les evts de l'encadrement pour les planches sélectionnées
        l_evts = Evenement.objects.filter(date__gte = date_debut_vue, 
                                          date__lte = date_fin_vue, 
                                          plant_base__in = Plant.objects.filter(planche_id = laPlanche))

        ## on en deduit les plants impliqués, même partiellement
        l_plantsId = list(set([evt.plant_base_id for evt in l_evts]))
        laPlanche.l_plants = Plant.objects.filter(planche_id = laPlanche, id__in = l_plantsId ).order_by('variete_id')
        ## on recupère de nouveau tous les évenements des plants impactés , même ceux hors fenetre temporelle 
        s_evts_plants = ""
        for plant in laPlanche.l_plants:
            plant.l_evts = Evenement.objects.filter(plant_base_id = plant.id, type = Evenement.TYPE_DIVERS).order_by('date')
            
    return render(request,
                 'main/chrono_planches.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "l_planches": l_planches,
                  "s_evts_plants":s_evts_plants,
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
        date_debut_vue = MyTools.getDateFrom_d_m_y(date_du_jour) 
        date_fin_vue = date_debut_vue
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
    
    ## on prend tous les evts de l'encadrement pour la planche courrante
    l_evts = Evenement.objects.filter(date__gte = date_debut_vue, date__lte = date_fin_vue)
    for evt in l_evts:
        plant = Plant.objects.get(id = evt.plant_base_id)
        planche = Planche.objects.get(id = plant.planche_id)
        evt.planche_num = planche.num

#     plant_base__in = Plant.objects.filter(planche_id = laPlanche))

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

    planche = Planche.objects.get(num = int(request.GET.get("num_planche", 0)))
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

    l_plants = recupListePlantsEnDateDu(dateVue, planche.id)

    
    return render(request,
                 'main/edition_planche.html',
                 {
                  "appVersion":constant.APP_VERSION,
                  "planche":planche,
                  "l_vars":Variete.objects.all(),
                  "l_evtTypes":Evenement.D_NOM_TYPES.items(),
                  "d_evtTypes":Evenement.D_NOM_TYPES,
                  "l_plants":l_plants,
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
    
    l_vars = Variete.objects.filter(famille__isnull=False)
    for v in l_vars:
        v.nomUniteProd = constant.D_NOM_UNITE_PROD[v.unite_prod]
     
    return render(request,
                 'main/tab_varietes.html',
                 {
                  "l_vars":l_vars,
                  "l_fams":Famille.objects.all(),
                  "appVersion":constant.APP_VERSION,
                  })
    
#################################################

def quizFamilles(request):
    message = ""
    
    form = forms.FormFamilyQuiz(request.POST or None)

    if form.is_valid():
        
        idVarAsked = request.POST.get('variete')
        
        varAsked = Variete.objects.get(id=idVarAsked)
     
        print("var ", varAsked.id, varAsked.nom, varAsked.famille)
        
        repIdFam = int(request.POST.get('famChoice', -1))
        
        print('rep', repIdFam)
         
        if repIdFam == varAsked.famille.id:
            message = "BRAVO"
        else:
            message = "PERDU"

        message += ", %s est de la famille des %ss " % (varAsked.nom, varAsked.famille.nom)

        ## restart a new form
        form = forms.FormFamilyQuiz()

    form.var = random(Variete.objects.filter(famille__isnull=False).values("nom", "id"))

    return render(request, 'main/quizFamilles.html',
            {
             "message" : message,
             "form": form,
             "appVersion": constant.APP_VERSION
            }
          )  
    
    


#################################################
