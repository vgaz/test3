# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from main.models import Evenement
from main.models import Famille
from main.models import Variete
from main.models import Plant
from main.models import Planche
from main.models import Production

admin.site.register(Evenement)
admin.site.register(Famille)
admin.site.register(Variete)
admin.site.register(Planche)
admin.site.register(Plant)
admin.site.register(Production)
