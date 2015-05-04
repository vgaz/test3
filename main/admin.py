# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from main.models import Evenement
from main.models import Famille
from main.models import Variete
from main.models import PlantBase
from main.models import Planche
from main.models import Prevision
from main.models import Production
from main.models import TypeEvenement

admin.site.register(Evenement)
admin.site.register(Famille)
admin.site.register(Variete)
admin.site.register(Planche)
admin.site.register(PlantBase)
admin.site.register(Prevision)
admin.site.register(Production)
admin.site.register(TypeEvenement)
