from django.conf.urls import include, url

from django.contrib import admin
from django.views.static import serve
from django.core.urlresolvers import reverse_lazy

admin.autodiscover()
from main import settings, views, serveRequest

urlpatterns = [
    url(r'^tab_legumes/', views.tab_legumes, name="tab_legumes"),
    url(r'^request/', serveRequest.serveRequest),
    url(r'^quiz_familles/', views.quizFamilles, name="quiz_familles"),
    url(r'^suivi_implantations/', views.suiviImplantations, name="suivi_implantations"),        
    url(r'^recolte/', views.recolte, name="recolte"),
    url(r'^evenements/', views.evenementsPlanches, name="evenements"),
    url(r'^creation_planches/', views.creationPlanches, name="creation_planches"),    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home', views.home, name="home"),
    url(r'^$', views.home),
]

## ajout special pour prise en compte des fichiers images et media
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns.append(url('^media/(?P<path>.*)$', serve))