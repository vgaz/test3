# -*- coding: utf-8 -*-

from django import forms
from maraich.models import Famille, Planche

class FormFamilyQuiz(forms.Form):
    l_choices = [(fam.pk, fam.nom) for fam in Famille.objects.all().order_by('nom')]
    famChoice = forms.ChoiceField(  label = "Liste des familles",
                                    choices = l_choices, 
                                    widget = forms.RadioSelect())
    
    def clean(self):
        """controle, correction , ajout eventuel des champs du formulaire)"""
#         log.debug("cleaned data %s"%str(self.cleaned_data))
#         pkResp = self.cleaned_data.get('famChoices')
#         msg = "rep = %s"%str(pkResp)
#         log.debug(msg)
        return self.cleaned_data

class PlancheForm(forms.ModelForm):

    class Meta:
        model = Planche
        exclude = ()## on garde tous les champs pour le moment

    def clean(self):
#         nom = self.cleaned_data.get('nom')
#         num = self.cleaned_data.get('num')
#         self.cleaned_data['num'] = 554455  ici, on retouche eventuellement les champs
        if False:
            msg = "I'm sure you didn't do this task before its deadline!"
            self._errors["done"] = self.error_class([msg])

        
        return self.cleaned_data

    
