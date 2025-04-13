from datetime import timedelta
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import time, uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import PaymentOrder, TARIFF_TYPE_CHOICES
from .utils import compute_wsb_signature, verify_notify_signature

# Конфигурация Webpay.by (оставляем для возможного восстановления)
WSB_STOREID = "791241990"
WSB_SECRET_KEY = "1q2w3e4r5t6y7u8i9o0"
WSB_VERSION = "2"
WSB_TEST = "1"
WSB_CURRENCY_ID = "BYN"
WSB_LANGUAGE_ID = "russian"
WSB_STORE_NAME = "My Shop"
WSB_PAYMENT_URL = "https://securesandbox.webpay.by/"

@login_required
def initiate_payment(request):
    # Временно отключаем обработку оплаты
    messages.error(request, "Оплата временно недоступна. Пожалуйста, используйте бесплатный тариф.")
    return redirect('payments:choose_subscription')

@login_required
def payment_success(request):
    messages.info(request, "Оплата временно приостановлена.")
    return redirect('payments:choose_subscription')

@login_required
def payment_cancel(request):
    messages.info(request, "Оплата временно приостановлена.")
    return redirect('payments:choose_subscription')

@csrf_exempt
def payment_notify(request):
    return HttpResponse("Оплата временно приостановлена.", status=403)

@login_required
def choose_subscription(request):
    now = timezone.now()
    profile = request.user.profile

    # Автоматическая конвертация тарифа на "free", если подписка истекла
    if profile.subscription_end and profile.subscription_end < now and profile.tariff != 'free':
        profile.tariff = 'free'
        profile.save()

    current_subscription = None
    if profile.subscription_end and profile.subscription_end > now:
        current_subscription = profile.subscription_end

    renew = request.GET.get('renew') == 'true'
    tariff = request.GET.get('tariff', profile.tariff) if renew else None

    tariff_options = [
        {
            'type': 'lite',
            'label': 'Базовый (до 500 запчастей)',
            'durations': [
                {'duration': 1, 'price': 20.00, 'label': '30 дней – 20 руб'},
                {'duration': 3, 'price': 60.00, 'label': '90 дней – 60 руб'},
                {'duration': 6, 'price': 120.00, 'label': '180 дней – 120 руб'},
                {'duration': 12, 'price': 240.00, 'label': '360 дней – 240 руб'},
            ]
        },
        {
            'type': 'standard',
            'label': 'Cтандартный (до 2000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 40.00, 'label': '30 дней – 40 руб'},
                {'duration': 3, 'price': 120.00, 'label': '90 дней – 120 руб'},
                {'duration': 6, 'price': 240.00, 'label': '180 дней – 240 руб'},
                {'duration': 12, 'price': 480.00, 'label': '360 дней – 480 руб'},
            ]
        },
        {
            'type': 'standard2',
            'label': 'Продвинутый (до 7000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 70.00, 'label': '30 дней – 70 руб'},
                {'duration': 3, 'price': 210.00, 'label': '90 дней – 210 руб'},
                {'duration': 6, 'price': 420.00, 'label': '180 дней – 420 руб'},
                {'duration': 12, 'price': 840.00, 'label': '360 дней – 840 руб'},
            ]
        },
        {
            'type': 'standard3',
            'label': 'Профессиональный (до 15000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 120.00, 'label': '30 дней – 120 руб'},
                {'duration': 3, 'price': 360.00, 'label': '90 дней – 360 руб'},
                {'duration': 6, 'price': 720.00, 'label': '180 дней – 720 руб'},
                {'duration': 12, 'price': 1440.00, 'label': '360 дней – 1440 руб'},
            ]
        },
        {
            'type': 'premium',
            'label': 'Неограниченный (без ограничений)',
            'durations': [
                {'duration': 1, 'price': 300.00, 'label': '30 дней – 300 руб'},
                {'duration': 3, 'price': 900.00, 'label': '90 дней – 900 руб'},
                {'duration': 6, 'price': 1800.00, 'label': '180 дней – 1800 руб'},
                {'duration': 12, 'price': 3600.00, 'label': '360 дней – 3600 руб'},
            ]
        },
    ]

    if request.method == 'POST':
        tariff_type = request.POST.get('tariff_type', 'free')
        if tariff_type == 'free':
            profile.tariff = 'free'
            profile.subscription_start = now
            profile.subscription_end = None  # Бесплатный тариф не имеет срока окончания
            profile.save()
            messages.success(request, "Бесплатный тариф успешно активирован.")
            return redirect('profile')
        else:
            messages.error(request, "Оплата платных тарифов временно недоступна.")
            return redirect('payments:choose_subscription')

    return render(request, 'payments/choose_subscription.html', {
        'tariff_options': tariff_options,
        'current_subscription': current_subscription,
        'now': now,
        'renew': renew,
    })