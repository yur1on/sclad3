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

# Конфигурация Webpay.by
WSB_STOREID = "791241990"  # Ваш Billing ID
WSB_SECRET_KEY = "1q2w3e4r5t6y7u8i9o0"  # Ваш секретный ключ
WSB_VERSION = "2"
WSB_TEST = "1"  # Тестовый режим
WSB_CURRENCY_ID = "BYN"
WSB_LANGUAGE_ID = "russian"
WSB_STORE_NAME = "My Shop"  # Название магазина
WSB_PAYMENT_URL = "https://securesandbox.webpay.by/"  # URL тестовой среды

@login_required
def initiate_payment(request):
    tariff_type = request.GET.get('tariff', 'standard')
    try:
        duration = int(request.GET.get('duration', 1))
    except ValueError:
        duration = 1

    profile = request.user.profile
    now = timezone.now()

    # Проверяем, есть ли активная подписка и меняется ли тариф
    if profile.subscription_end and profile.subscription_end > now and profile.tariff != tariff_type and profile.tariff != 'free':
        if request.method == 'POST' and request.POST.get('confirm_change') == 'yes':
            # Пользователь подтвердил смену тарифа, продолжаем
            pass
        else:
            # Показываем предупреждение вместо блокировки
            return render(request, 'payments/confirm_tariff_change.html', {
                'current_tariff': profile.get_tariff_display(),
                'new_tariff': dict(TARIFF_TYPE_CHOICES).get(tariff_type, tariff_type),
                'duration': duration,
                'subscription_end': profile.subscription_end,
                'tariff_type': tariff_type,
            })

    # Цены для тарифов
    if tariff_type == 'standard':
        price_lookup = {1: 30.00, 3: 90.00, 6: 180.00, 12: 360.00}
    elif tariff_type == 'standard2':
        price_lookup = {1: 50.00, 3: 150.00, 6: 300.00, 12: 600.00}
    elif tariff_type == 'premium':
        price_lookup = {1: 100.00, 3: 300.00, 6: 600.00, 12: 1200.00}
    else:
        price_lookup = {1: 0.00}  # Для бесплатного тарифа
    total = price_lookup.get(duration, 30.00)

    order_number = f"ORDER-{uuid.uuid4().hex[:10].upper()}"
    order = PaymentOrder.objects.create(
        user=request.user,
        order_number=order_number,
        total=total,
        duration=duration,
        tariff_type=tariff_type
    )

    wsb_seed = str(int(time.time()))
    wsb_order_num = order.order_number
    wsb_test = WSB_TEST
    wsb_total = f"{total:.2f}"

    wsb_signature = compute_wsb_signature(
        wsb_seed, WSB_STOREID, wsb_order_num, wsb_test, WSB_CURRENCY_ID, wsb_total, WSB_SECRET_KEY, version=2
    )

    user_profile = request.user.profile
    wsb_customer_name = user_profile.full_name if user_profile.full_name else request.user.username
    wsb_customer_address = user_profile.city
    wsb_email = request.user.email
    wsb_phone = user_profile.phone

    wsb_return_url = request.build_absolute_uri(reverse('payments:payment_success'))
    wsb_cancel_return_url = request.build_absolute_uri(reverse('payments:payment_cancel'))
    wsb_notify_url = request.build_absolute_uri(reverse('payments:payment_notify'))

    context = {
        'wsb_payment_url': WSB_PAYMENT_URL,
        'wsb_version': WSB_VERSION,
        'wsb_language_id': WSB_LANGUAGE_ID,
        'wsb_storeid': WSB_STOREID,
        'wsb_store': WSB_STORE_NAME,
        'wsb_order_num': wsb_order_num,
        'wsb_test': wsb_test,
        'wsb_currency_id': WSB_CURRENCY_ID,
        'wsb_seed': wsb_seed,
        'wsb_customer_name': wsb_customer_name,
        'wsb_customer_address': wsb_customer_address,
        'wsb_return_url': wsb_return_url,
        'wsb_cancel_return_url': wsb_cancel_return_url,
        'wsb_notify_url': wsb_notify_url,
        'wsb_email': wsb_email,
        'wsb_phone': wsb_phone,
        'invoice_item_name': "Подписка на платный тариф",
        'invoice_item_quantity': "1",
        'invoice_item_price': wsb_total,
        'wsb_total': wsb_total,
        'wsb_signature': wsb_signature,
    }
    return render(request, 'payments/payment_form.html', context)

@login_required
def payment_success(request):
    order_num = request.GET.get('wsb_order_num')
    try:
        order = PaymentOrder.objects.get(order_number=order_num, status='pending')
        order.status = 'paid'
        order.transaction_id = request.GET.get('wsb_tid', '')
        order.save()

        profile = request.user.profile
        now = timezone.now()

        # Новый период в днях
        new_period_days = order.duration * 30

        # Применяем новый тариф сразу
        profile.subscription_start = now
        profile.subscription_end = now + timedelta(days=new_period_days)
        profile.tariff = order.tariff_type
        profile.save()

        return render(request, 'payments/payment_success.html', {'order': order})
    except PaymentOrder.DoesNotExist:
        return HttpResponse("Заказ не найден или уже обработан.", status=404)

@login_required
def payment_cancel(request):
    order_num = request.GET.get('wsb_order_num')
    try:
        order = PaymentOrder.objects.get(order_number=order_num, status='pending')
        order.status = 'cancelled'
        order.save()
        return render(request, 'payments/payment_cancel.html', {'order': order})
    except PaymentOrder.DoesNotExist:
        return HttpResponse("Заказ не найден или уже обработан.", status=404)

@csrf_exempt
def payment_notify(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Метод не поддерживается")
    if not verify_notify_signature(request.POST, WSB_SECRET_KEY):
        return HttpResponse("Неверная подпись", status=400)
    order_num = request.POST.get('site_order_id')
    try:
        order = PaymentOrder.objects.get(order_number=order_num, status='pending')
        payment_type = request.POST.get('payment_type', '')
        if payment_type in ['1', '4', '10', '23']:
            order.status = 'paid'
            order.transaction_id = request.POST.get('transaction_id', '')
            order.invoice_number = request.POST.get('order_id', '')
            order.save()
            order.user.profile.tariff = order.tariff_type
            order.user.profile.save()
            return HttpResponse("OK", status=200)
        else:
            order.status = 'cancelled'
            order.save()
            return HttpResponse("Платеж неуспешный", status=400)
    except PaymentOrder.DoesNotExist:
        return HttpResponse("Заказ не найден", status=404)

@login_required
def choose_subscription(request):
    now = timezone.now()
    current_subscription = None
    if request.user.profile.subscription_end and request.user.profile.subscription_end > now:
        current_subscription = request.user.profile.subscription_end

    # Проверяем, является ли это продлением
    renew = request.GET.get('renew') == 'true'
    tariff = request.GET.get('tariff', request.user.profile.tariff) if renew else None

    tariff_options = [
        {
            'type': 'standard',
            'label': 'Стандарт (до 1000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 30.00, 'label': '30 дней – 30 руб'},
                {'duration': 3, 'price': 90.00, 'label': '90 дней – 90 руб'},
                {'duration': 6, 'price': 180.00, 'label': '180 дней – 180 руб'},
                {'duration': 12, 'price': 360.00, 'label': '360 дней – 360 руб'},
            ]
        },
        {
            'type': 'standard2',
            'label': 'Стандарт 2 (до 10000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 50.00, 'label': '30 дней – 50 руб'},
                {'duration': 3, 'price': 150.00, 'label': '90 дней – 150 руб'},
                {'duration': 6, 'price': 300.00, 'label': '180 дней – 300 руб'},
                {'duration': 12, 'price': 600.00, 'label': '360 дней – 600 руб'},
            ]
        },
        {
            'type': 'premium',
            'label': 'Премиум (без ограничений)',
            'durations': [
                {'duration': 1, 'price': 100.00, 'label': '30 дней – 100 руб'},
                {'duration': 3, 'price': 300.00, 'label': '90 дней – 300 руб'},
                {'duration': 6, 'price': 600.00, 'label': '180 дней – 600 руб'},
                {'duration': 12, 'price': 1200.00, 'label': '360 дней – 1200 руб'},
            ]
        },
    ]
    if request.method == 'POST':
        tariff_type = request.POST.get('tariff_type', 'standard')
        try:
            duration = int(request.POST.get('duration', 1))
        except ValueError:
            duration = 1
        return redirect(f"{reverse('payments:initiate_payment')}?tariff={tariff_type}&duration={duration}")
    return render(request, 'payments/choose_subscription.html', {
        'tariff_options': tariff_options,
        'current_subscription': current_subscription,
        'now': now,
        'renew': renew,
    })