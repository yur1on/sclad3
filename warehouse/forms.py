
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Part





class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['device', 'brand', 'model', 'part_type', 'color', 'quantity', 'price', 'image']
