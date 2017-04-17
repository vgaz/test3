"""maraich URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve

from maraich import settings, views, serveRequest

urlpatterns = [
    url(r'^tab_legumes/', views.tab_legumes, name="tab_legumes"),
    url(r'^request/', serveRequest.serveRequest),
    url(r'^quiz_familles/', views.quizFamilles, name="quiz_familles"),
    url(r'^suivi_implantations/', views.suiviImplantations, name="suivi_implantations"),        
    url(r'^recolte/', views.recolte, name="recolte"),
    url(r'^utilisation_planches/', views.utilisationPlanches, name="utilisation_planches"),
    url(r'^suivi_plants/', views.suiviPlants, name="suivi_plants"),
    url(r'^evenements/', views.evenementsPlanches, name="evenements"),
    url(r'^creation_planches/', views.creationPlanches, name="creation_planches"),    
    url(r'^admin/', admin.site.urls),
    url(r'^home', views.home, name="home"),
    url(r'^$', views.home),
]

## ajout special pour prise en compte des fichiers images et media
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns.append(url('^media/(?P<path>.*)$', serve))