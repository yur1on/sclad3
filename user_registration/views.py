from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegisterForm
from .utils import send_confirmation_email, verify_email_confirmation_token

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)  # Используем данные из POST
        if form.is_valid():
            new_user = form.save()  # Создаём нового пользователя
            # Отправляем письмо с подтверждением email
            send_confirmation_email(request, new_user)
            # Перенаправляем на страницу-информацию о том, что письмо отправлено
            return render(request, 'user_registration/registration_pending.html', {'email': new_user.email})
    else:
        form = UserRegisterForm()  # Пустая форма для GET-запроса
    return render(request, 'user_registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Если пользователь не суперпользователь, проверяем подтверждение email
            if not user.is_superuser and (not hasattr(user, 'profile') or not user.profile.email_confirmed):
                messages.error(request, "Пожалуйста, подтвердите ваш email перед входом.")
                return redirect('login')
            login(request, user)
            return redirect('warehouse')
        else:
            messages.error(request, "Неверный логин или пароль.")
    return render(request, 'user_registration/login.html')


def confirm_email(request, token):
    data = verify_email_confirmation_token(token)
    if data:
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.profile.email_confirmed = True
        user.profile.save()
        messages.success(request, "Ваш email успешно подтвержден!")
        return redirect('login')
    else:
        messages.error(request, "Неверный или истекший токен подтверждения.")
        return redirect('register')
