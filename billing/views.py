import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Subscription
from .forms import SubscriptionForm

ALFABANK_API_USER = settings.ALFABANK_API_USER
ALFABANK_API_PASSWORD = settings.ALFABANK_API_PASSWORD
ALFABANK_PAYMENT_URL = settings.ALFABANK_PAYMENT_URL

@login_required
def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            duration = int(form.cleaned_data['duration'])
            amount = 500 * duration  # Например, 500 руб. за каждый месяц

            # Создание заказа в системе Альфа-Банка
            response = requests.post(f"{ALFABANK_PAYMENT_URL}register.do", data={
                'userName': ALFABANK_API_USER,
                'password': ALFABANK_API_PASSWORD,
                'orderNumber': f"{request.user.id}-{timezone.now().timestamp()}",
                'amount': str(amount * 100),  # сумма в копейках
                'returnUrl': 'https://вашсайт/успешная_оплата/',
                'failUrl': 'https://вашсайт/ошибка_оплаты/',
                'description': 'Подписка на сайте'
            })

            data = response.json()
            if data.get('errorCode') == '0':
                # Сохраняем заказ
                Subscription.objects.create(user=request.user, duration=duration)
                return redirect(data['formUrl'])
            else:
                messages.error(request, 'Ошибка при создании платежа. Пожалуйста, попробуйте позже.')
    else:
        form = SubscriptionForm()

    return render(request, 'billing/subscribe.html', {'form': form})

from django.http import HttpResponse

@login_required
def payment_success(request):
    messages.success(request, 'Подписка успешно оформлена!')
    return redirect('user_profile:profile')

@login_required
def payment_failure(request):
    messages.error(request, 'Произошла ошибка при оплате.')
    return redirect('billing:subscribe')
