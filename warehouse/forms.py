from django import forms
from .models import Part, PartImage
from django.forms import modelformset_factory
from django.forms import modelformset_factory
from .models import PartImage
class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['device', 'brand', 'model', 'part_type', 'color', 'quantity', 'price']

class PartImageForm(forms.ModelForm):
    class Meta:
        model = PartImage
        fields = ['image']



PartImageFormSet = modelformset_factory(PartImage, fields=('image',), extra=5)

