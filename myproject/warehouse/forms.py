from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Part
from django import forms
from .models import Part
class UserRegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    city = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'phone', 'city', 'password1', 'password2']



class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['device', 'brand', 'model', 'part_type', 'quantity', 'price', 'image']  # Добавлено поле image



