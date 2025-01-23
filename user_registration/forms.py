from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    error_messages = {
        'password_mismatch': 'Пароли не совпадают.',  # Сообщение об ошибке на русском
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




urlpatterns = [
    # URL для начала процесса восстановления пароля (ввод email)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='user_registration/password_reset_form.html'), name='password_reset'),

    # URL для успешной отправки email
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='user_registration/password_reset_done.html'), name='password_reset_done'),

    # URL для ввода нового пароля по токену из email
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='user_registration/password_reset_confirm.html'), name='password_reset_confirm'),

    # URL для успешного сброса пароля
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='user_registration/password_reset_complete.html'), name='password_reset_complete'),
]
