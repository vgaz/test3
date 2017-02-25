# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy

from django.template.defaultfilters import random

import sys

from main import forms, constant
from main.settings import log
import MyTools

import datetime

from main.models import *
from main.forms import PlancheForm


def donnePeriodeVue(reqPost):
    
    date_aujourdhui = datetime.datetime.now()
    periode = reqPost.get("periode","annee")
    if periode == "specifique":
        date_debut_vue = MyTools.getDateFrom_d_m_y(reqPost.get("date_debut_vue", ""))
        date_fin_vue = MyTools.getDateFrom_d_m_y(reqPost.get("date_fin_vue", ""))
    elif periode == "annee":
        date_premierJour = MyTools.getDateFrom_d_m_y("1/1/%s"%date_aujourdhui.year)
        delta = datetime.timedelta(days=365)
        date_debut_vue = date_premierJour
        date_fin_vue = date_premierJour + delta
    elif periode == "mois":
        print ("mois", str(date_aujourdhui.month), " year", date_aujourdhui.year)
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
    return(periode, date_debut_vue, date_fin_vue)

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
        
        periode = request.POST.get("periode","annee")
        if periode == "specifique":
            date_debut_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_debut_vue", ""))
            date_fin_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_fin_vue", ""))
        elif periode == "annee":
            date_premierJour = MyTools.getDateFrom_d_m_y("1/1/%s"%date_aujourdhui.year)
            delta = datetime.timedelta(days=365)
            date_debut_vue = date_premierJour
            date_fin_vue = date_premierJour + delta
        elif periode == "mois":
            print ("mois", str(date_aujourdhui.month), " year", date_aujourdhui.year)
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
        
        
        decalage_j = int(request.POST.get("decalage_j", 10))
        delta = datetime.timedelta(days = decalage_j)
        if request.POST.get("direction", "") == "avance":
            date_debut_vue += delta 
            date_fin_vue += delta
            
        if request.POST.get("direction", "") == "recul":
            date_debut_vue -= delta 
            date_fin_vue -= delta
        
        
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
 
        for planche in l_planches:
            planche.l_implantations = []
            l_series = Serie.objects.activesSurPeriode(date_debut_vue, 
                                                        date_fin_vue, 
                                                        planche)
            
            ## ajout de l'implation spécifique à cette planche (il ne peut y avoir qu'une implantation de série par planche)
            for serie in l_series:
                planche.l_implantations.append(serie.implantations.get(planche_id=planche.id))

    except:
        s_msg += str(sys.exc_info())
  
    return render(request,
                 'main/suivi_implantations.html',
                 {
                    "appVersion": constant.APP_VERSION,
                    "appName": constant.APP_NAME,
                    "periode":periode,
                    "selection_serres":bSerres,
                    "selection_champs":bChamps,
                    "s_filtre_planches":s_filtre_planches,
                    "l_planches": l_planches,
                    "d_evtTypes": Evenement.D_NOM_TYPES,
                    "codeEvtDivers":Evenement.TYPE_DIVERS,
                    "l_legumes": Legume.objects.all(),
                    "date_debut_vue": date_debut_vue,
                    "date_fin_vue": date_fin_vue,
                    "date_du_jour": date_aujourdhui,
                    "decalage_j": decalage_j,
                    "s_msg":s_msg,
                    "doc":constant.DOC_CHRONOVIEW
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
    date_aujourdhui = datetime.datetime.now()
    periode = request.POST.get("periode","cette_semaine")
    bEncours = request.POST.get("bEncours", "on")=="on"
    if periode == "aujourdhui":
        date_debut_vue = date_aujourdhui
        date_fin_vue = date_aujourdhui
    elif periode == "cette_semaine":
        delta = datetime.timedelta(days=6)
        date_debut_vue =  date_aujourdhui - datetime.timedelta(days=date_aujourdhui.weekday())
        date_fin_vue = date_debut_vue + delta
    elif periode == "specifique":
        date_debut_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_debut_vue", ""))
        date_fin_vue = MyTools.getDateFrom_d_m_y(request.POST.get("date_fin_vue", "")) + delta20h
    else:
        delta = datetime.timedelta(days=60)
        date_debut_vue = date_aujourdhui - delta
        date_fin_vue = date_aujourdhui + delta + delta20h

    decalage_j = int(request.POST.get("decalage_j", 10))
    delta = datetime.timedelta(days = decalage_j)
    if request.POST.get("direction", "") == "avance":
        date_debut_vue += delta 
        date_fin_vue += delta
    if request.POST.get("direction", "") == "recul":
        date_debut_vue -= delta 
        date_fin_vue -= delta        

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
    
    print(ics_txt)
    
    return render(request,
                 'main/evenements.html',
                 {
                  "appVersion": constant.APP_VERSION,
                  "appName": constant.APP_NAME,
                  "l_evts": l_evts,
                  "date_debut_vue": date_debut_vue,
                  "date_fin_vue": date_fin_vue,
                  "date_aujourdhui": date_aujourdhui,
                  "decalage_j": decalage_j,
                  "periode":periode,
                  "bEncours":bEncours
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

def recolte(request):
    """affiche les previsions et récoltes réelles hebdo"""
    try:
        s_info = ""
        ## récup de la fenetre de temps
        periode, date_debut_vue, date_fin_vue = donnePeriodeVue(request.POST) 
        date_debut_sem_vue = date_debut_vue - datetime.timedelta(days=date_debut_vue.weekday()) 
        date_fin_sem_vue = date_fin_vue + datetime.timedelta(days = 6 - date_fin_vue.weekday()) 
    
        ## création de la liste des semaines     
        # on recadre sur le lundi pour démarrer en debut de semaine
        l_semaines = []
        date_debut_sem = date_debut_sem_vue
    
        nbPanniers = constant.NB_PANNIERS
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
    
        l_seriesActives = Serie.objects.activesSurPeriode(date_debut_sem_vue, date_fin_sem_vue) ## on ne garde que la fenetre de temps étudiée
        ## recherche des productions par semaine regroupées par légume ou par espèce
        l_legumes = Legume.objects.all()
            
        for leg in l_legumes:
            ## calcul des productions de légumes
            l_series = l_seriesActives.filter(legume_id = leg.id)
            
            ## Pour chaque semaine étudiée, on calcule le stock cumulé de chaque série 
            ## le stock est lissé 
            ## sur la conso hebdo pour les légumes stockables
            ## ou sur la durée de récolte pour les légumes non stockables
            leg.l_prod = []
            print("LEG xxxxxxxxxxxxxxxx", leg.__str__())
            for sem in l_semaines:
                qteHebdo = 0
                for serie in l_series:
                    print('sem.............', sem.date_debut, '.... serie ', serie.__str__())
                    qteHebdo += serie.prodHebdo(sem.date_debut)
                    
                if qteHebdo == 0:
                    couleur = "white"
                else:
                    couleur = leg.espece.couleur
                
                try : 
                    print(sem.date_debut)
                    prodReelle = Production.objects.get(legume_id=leg.id, dateDebutSemaine = sem.date_debut).qte
                except:
                    prodReelle = 0
                    
                leg.l_prod.append((sem.date_debut, 
                                   int(qteHebdo), 
                                   int(leg.poids_kg(qteHebdo)),
                                   leg.espece.nomUniteProd(),
                                   couleur,
                                   prodReelle))
    
        bDetailVar = request.POST.get("detail_variete", "") != ""

    except:
        log.error(s_info)
        s_info += str(sys.exc_info()[1])
        
    return render(request,'main/recolte.html',
                    {
                    "appVersion":constant.APP_VERSION,
                    "periode":periode,
                    "date_debut_vue": date_debut_vue,
                    "date_fin_vue": date_fin_vue,
                    "l_semaines":l_semaines,
                    "l_legumes":l_legumes,
                    "l_especes" : Espece.objects.all(),
                    "bDetailVar":bDetailVar,
                    "nbPanniers":nbPanniers,
                    "info":"s_info"
                    })
    
#################################################

def tab_legumes(request):
    s_info = ""
    try:
        l_legumes = Legume.objects.all()
        if request.POST:
            for leg in l_legumes:
                s_pk = "leg_%d_"%leg.pk
                
                ## lié à l'espece
                ## leg.espece =
      
                leg.nbGrainesParPied = int(request.POST.get(s_pk + "nbGrainesParPied", "1"))
                leg.poidsParPiece_kg = float(request.POST.get(s_pk + "poidsParPiece_kg", "0").replace(",","."))
                leg.rendementProduction_kg_m2 = float(request.POST.get(s_pk + "rendementProduction_kg_m2", "0").replace(",","."))
                leg.rendement_plants_graines_pourcent = int(request.POST.get(s_pk + "rendement_plants_graines_pourcent", "100"))
                leg.intra_rang_m = float(request.POST.get(s_pk + "intra_rang_cm", "0").replace(",","."))/100
                leg.inter_rang_m = float(request.POST.get(s_pk + "inter_rang_cm", "0").replace(",","."))/100
                leg.save()

    except:
        s_info += str(sys.exc_info()[1])
        
    return render(request,
                 'main/tab_legumes.html',
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

        message += "%s, la/le %s est de la famille des %ss" % (s_rep, espece.nom, espece.famille.nom)

        ## restart a new form
        form = forms.FormFamilyQuiz()

    form.esp = random(Espece.objects.filter(famille__isnull=False).values("nom", "id"))

    return render(request, 'main/quiz_familles.html',
            {
             "color":color,
             "message" : message,
             "form": form,
             "appVersion": constant.APP_VERSION
            }
          )  
    
    


#################################################
