from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    agreement = forms.BooleanField(
        required=True,
        label=mark_safe('Я принимаю условия <a href="/user-agreement/" target="_blank">Пользовательского соглашения</a>'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'display:inline-block;'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    error_messages = {
        'password_mismatch': 'Пароли не совпадают.',
    }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Такое имя пользователя уже занято.')
        return username
