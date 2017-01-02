from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

admin.autodiscover()
from main.views import CreationPlanche
from main import constant, settings

urlpatterns = patterns('',

    url(r'^tab_legumes/', 'main.views.tab_legumes', name='tab_legumes'),
    url(r'^request/', 'main.serveRequest.serveRequest'),
    url(r'^quizFamilles/', 'main.views.quizFamilles', name='quizFamilles'),
    
#     url(r'^edition_planche/', 'main.views.editionPlanche', name='edition_planche'),
    url(r'^suivi_implantations/', 'main.views.suiviImplantations', name='suivi_implantations'),    
#     url(r'^placement_series/', 'main.views.placementSeries', name='placement_series'),
    
    url(r'^recolte/', 'main.views.recolte', name='recolte'),
    url(r'^evenements/', 'main.views.evenementsPlanches', name='evenements'),

    url(r'^creation_planche/', CreationPlanche.as_view() ,  
        {"appName":constant.APP_NAME, "appVersion":constant.APP_VERSION}, 
        name='creation_planche'),
    
    url(r'^creation_planches/', 'main.views.creationPlanches', name='creation_planches'),    
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^home', 'main.views.home',  name='home'),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('home'))),
)

## ajout special pour prise en compte des fichiers images et media
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))