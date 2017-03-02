# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from maraich.models import Famille
from maraich.models import Espece
from maraich.models import Evenement
from maraich.models import Implantation
from maraich.models import Legume
from maraich.models import Planche
from maraich.models import Serie

admin.site.register(Famille)
admin.site.register(Espece)
admin.site.register(Evenement)
admin.site.register(Implantation)
admin.site.register(Legume)
admin.site.register(Planche)
admin.site.register(Serie)
