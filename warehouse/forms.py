from django import forms
from .models import Part, PartImage
from django.forms import modelformset_factory

class PartForm(forms.ModelForm):
    price = forms.IntegerField(min_value=0, label="Цена")
    chip_label = forms.CharField(
        max_length=200,
        required=False,
        label="Маркировка микросхемы",
        widget=forms.TextInput(attrs={'class': 'chip-label', 'style': 'display:none;'})
    )

    class Meta:
        model = Part
        fields = ['device', 'brand', 'model', 'part_type', 'condition', 'color', 'quantity', 'price', 'note', 'chip_label']


class PartImageForm(forms.ModelForm):
    class Meta:
        model = PartImage
        fields = ['image']


PartImageFormSet = modelformset_factory(PartImage, fields=('image',), extra=5)
