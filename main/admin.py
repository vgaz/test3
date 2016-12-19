# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from main.models import Espece
from main.models import Evenement
from main.models import Famille
from main.models import Implantation
from main.models import Legume
from main.models import Planche
from main.models import Serie

admin.site.register(Espece)
admin.site.register(Evenement)
admin.site.register(Famille)
admin.site.register(Implantation)
admin.site.register(Legume)
admin.site.register(Planche)
admin.site.register(Serie)
