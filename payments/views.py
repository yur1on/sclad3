from datetime import timedelta
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import time
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import PaymentOrder, TARIFF_TYPE_CHOICES
from .utils import compute_wsb_signature, verify_notify_signature

# Webpay.by configuration
WSB_STOREID = "548275588"
WSB_SECRET_KEY = "1q2w3e4r5t6y7u8i9o0"
WSB_VERSION = "2"
WSB_TEST = "0"
WSB_CURRENCY_ID = "BYN"
WSB_LANGUAGE_ID = "russian"
WSB_STORE_NAME = "Mobirazbor"
WSB_PAYMENT_URL = "https://payment.webpay.by/"





# Valid durations for subscriptions
VALID_DURATIONS = [1, 3, 6, 12]

# Base prices per 30 days (halved from original)
BASE_PRICE_PER_30_DAYS = {
    'lite': 10.00,  # Was 20.00
    'standard': 20.00,  # Was 40.00
    'standard2': 35.00,  # Was 70.00
    'standard3': 60.00,  # Was 120.00
    'premium': 150.00  # Was 300.00
}


@login_required
def choose_subscription(request):
    """
    View for selecting a tariff and subscription duration.
    """
    now = timezone.now()
    profile = request.user.profile

    # Auto-switch to free tariff if subscription expired
    if profile.subscription_end and profile.subscription_end < now and profile.tariff != 'free':
        profile.tariff = 'free'
        profile.subscription_start = None
        profile.subscription_end = None
        profile.save()

    current_subscription = profile.subscription_end if profile.subscription_end and profile.subscription_end > now else None
    renew = request.GET.get('renew') == 'true'

    # Tariff options for template
    tariff_options = [
        {
            'type': 'lite',
            'label': 'Базовый (до 500 запчастей)',
            'durations': [
                {'duration': 1, 'price': 10.00, 'label': '30 дней – 10 руб'},
                {'duration': 3, 'price': 30.00, 'label': '90 дней – 30 руб'},
                {'duration': 6, 'price': 60.00, 'label': '180 дней – 60 руб'},
                {'duration': 12, 'price': 120.00, 'label': '360 дней – 120 руб'},
            ]
        },
        {
            'type': 'standard',
            'label': 'Стандартный (до 2000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 20.00, 'label': '30 дней – 20 руб'},
                {'duration': 3, 'price': 60.00, 'label': '90 дней – 60 руб'},
                {'duration': 6, 'price': 120.00, 'label': '180 дней – 120 руб'},
                {'duration': 12, 'price': 240.00, 'label': '360 дней – 240 руб'},
            ]
        },
        {
            'type': 'standard2',
            'label': 'Продвинутый (до 7000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 35.00, 'label': '30 дней – 35 руб'},
                {'duration': 3, 'price': 105.00, 'label': '90 дней – 105 руб'},
                {'duration': 6, 'price': 210.00, 'label': '180 дней – 210 руб'},
                {'duration': 12, 'price': 420.00, 'label': '360 дней – 420 руб'},
            ]
        },
        {
            'type': 'standard3',
            'label': 'Профессиональный (до 15000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 60.00, 'label': '30 дней – 60 руб'},
                {'duration': 3, 'price': 180.00, 'label': '90 дней – 180 руб'},
                {'duration': 6, 'price': 360.00, 'label': '180 дней – 360 руб'},
                {'duration': 12, 'price': 720.00, 'label': '360 дней – 720 руб'},
            ]
        },
        {
            'type': 'premium',
            'label': 'Неограниченный (без ограничений)',
            'durations': [
                {'duration': 1, 'price': 150.00, 'label': '30 дней – 150 руб'},
                {'duration': 3, 'price': 450.00, 'label': '90 дней – 450 руб'},
                {'duration': 6, 'price': 900.00, 'label': '180 дней – 900 руб'},
                {'duration': 12, 'price': 1800.00, 'label': '360 дней – 1800 руб'},
            ]
        },
    ]

    if request.method == 'POST':
        tariff_type = request.POST.get('tariff_type')
        try:
            duration = int(request.POST.get('duration', 1))
        except ValueError:
            duration = 1

        # Validate input
        valid_tariffs = [choice[0] for choice in TARIFF_TYPE_CHOICES]
        if tariff_type not in valid_tariffs:
            messages.error(request, "Недопустимый тариф")
            return redirect('payments:choose_subscription')
        if duration not in VALID_DURATIONS and tariff_type != 'free':
            messages.error(request, "Недопустимый срок подписки")
            return redirect('payments:choose_subscription')

        # Handle free tariff
        if tariff_type == 'free':
            profile.tariff = 'free'
            profile.subscription_start = None
            profile.subscription_end = None
            profile.save()
            messages.success(request, "Бесплатный тариф успешно активирован")
            return redirect('profile')

        # Store payment data in session
        request.session['payment_data'] = {
            'tariff_type': tariff_type,
            'duration': duration
        }
        return redirect('payments:initiate_payment')

    return render(request, 'payments/choose_subscription.html', {
        'tariff_options': tariff_options,
        'current_subscription': current_subscription,
        'now': now,
        'renew': renew,
    })


@login_required
def initiate_payment(request):
    """
    Initiate payment using session data.
    """
    payment_data = request.session.get('payment_data')
    if not payment_data:
        messages.error(request, "Данные о платеже не найдены")
        return redirect('payments:choose_subscription')

    tariff_type = payment_data['tariff_type']
    duration = payment_data['duration']

    # Re-validate for security
    valid_tariffs = [choice[0] for choice in TARIFF_TYPE_CHOICES]
    if tariff_type not in valid_tariffs:
        messages.error(request, "Недопустимый тариф")
        return redirect('payments:choose_subscription')
    if duration not in VALID_DURATIONS:
        messages.error(request, "Недопустимый срок подписки")
        return redirect('payments:choose_subscription')

    profile = request.user.profile
    now = timezone.now()

    # Check for tariff change with active subscription
    if profile.subscription_end and profile.subscription_end > now and profile.tariff != tariff_type and profile.tariff != 'free':
        if request.method == 'POST' and request.POST.get('confirm_change') == 'yes':
            pass  # Proceed with payment
        else:
            return render(request, 'payments/confirm_tariff_change.html', {
                'current_tariff': profile.get_tariff_display(),
                'new_tariff': dict(TARIFF_TYPE_CHOICES).get(tariff_type, tariff_type),
                'duration': duration,
                'subscription_end': profile.subscription_end,
                'tariff_type': tariff_type,
            })

    # Calculate total based on tariff and duration
    total = BASE_PRICE_PER_30_DAYS.get(tariff_type, 0.00) * duration

    # Create payment order
    order_number = f"ORDER-{uuid.uuid4().hex[:10].upper()}"
    order = PaymentOrder.objects.create(
        user=request.user,
        order_number=order_number,
        total=total,
        duration=duration,
        tariff_type=tariff_type
    )

    # Prepare Webpay.by payment data
    wsb_seed = str(int(time.time()))
    wsb_order_num = order.order_number
    wsb_test = WSB_TEST
    wsb_total = f"{total:.2f}"

    wsb_signature = compute_wsb_signature(
        wsb_seed, WSB_STOREID, wsb_order_num, wsb_test, WSB_CURRENCY_ID, wsb_total, WSB_SECRET_KEY, version=2
    )

    user_profile = request.user.profile
    wsb_customer_name = user_profile.full_name if user_profile.full_name else request.user.username
    wsb_customer_address = user_profile.city if user_profile.city else ""
    wsb_email = request.user.email
    wsb_phone = user_profile.phone if user_profile.phone else ""

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

    # Clear session data after initiating payment
    request.session.pop('payment_data', None)
    return render(request, 'payments/payment_form.html', context)


@login_required
def payment_success(request):
    """
    Handle successful payment.
    """
    order_num = request.GET.get('wsb_order_num')
    try:
        order = PaymentOrder.objects.get(order_number=order_num, status='pending')
        order.status = 'paid'
        order.transaction_id = request.GET.get('wsb_tid', '')
        order.save()

        profile = request.user.profile
        now = timezone.now()
        new_period_days = order.duration * 30

        profile.subscription_start = now
        profile.subscription_end = now + timedelta(days=new_period_days)
        profile.tariff = order.tariff_type
        profile.save()

        messages.success(request, "Оплата успешно завершена. Ваш тариф обновлен.")
        return render(request, 'payments/payment_success.html', {'order': order})
    except PaymentOrder.DoesNotExist:
        messages.error(request, "Заказ не найден или уже обработан.")
        return redirect('profile')


@login_required
def payment_cancel(request):
    """
    Handle payment cancellation.
    """
    order_num = request.GET.get('wsb_order_num')
    try:
        order = PaymentOrder.objects.get(order_number=order_num, status='pending')
        order.status = 'cancelled'
        order.save()
        messages.warning(request, "Оплата была отменена.")
        return render(request, 'payments/payment_cancel.html', {'order': order})
    except PaymentOrder.DoesNotExist:
        messages.error(request, "Заказ не найден или уже обработан.")
        return redirect('profile')


@csrf_exempt
def payment_notify(request):
    """
    Handle payment notification from Webpay.by.
    """
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
            profile = order.user.profile
            now = timezone.now()
            new_period_days = order.duration * 30
            profile.tariff = order.tariff_type
            profile.subscription_start = now
            profile.subscription_end = now + timedelta(days=new_period_days)
            profile.save()
            return HttpResponse("OK", status=200)
        else:
            order.status = 'cancelled'
            order.save()
            return HttpResponse("Платеж неуспешный", status=400)
    except PaymentOrder.DoesNotExist:
        return HttpResponse("Заказ не найден", status=404)
