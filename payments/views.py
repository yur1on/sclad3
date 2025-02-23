
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .utils import compute_wsb_signature, verify_notify_signature
import time, uuid
from .models import PaymentOrder
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Конфигурация Webpay.by
WSB_STOREID = "791241990"  # Ваш Billing ID
WSB_SECRET_KEY = "1q2w3e4r5t6y7u8i9o0"  # Ваш секретный ключ
WSB_VERSION = "2"
WSB_TEST = "1"  # Тестовый режим
WSB_CURRENCY_ID = "BYN"
WSB_LANGUAGE_ID = "russian"
WSB_STORE_NAME = "My Shop"  # Название магазина

# URL платежной системы:
WSB_PAYMENT_URL = "https://securesandbox.webpay.by/"  # Для тестирования


@login_required
def initiate_payment(request):
    tariff_type = request.GET.get('tariff', 'standard')
    try:
        duration = int(request.GET.get('duration', 1))
    except ValueError:
        duration = 1
    if tariff_type == 'standard':
        price_lookup = {1: 30.00, 3: 90.00, 6: 180.00, 12: 360.00}
    elif tariff_type == 'premium':
        price_lookup = {1: 100.00, 3: 300.00, 6: 600.00, 12: 1200.00}
    else:
        price_lookup = {1: 30.00, 3: 90.00, 6: 180.00, 12: 360.00}
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
    wsb_storeid = "791241990"  # Ваш Billing ID
    wsb_order_num = order.order_number
    wsb_test = "1"
    wsb_currency_id = "BYN"
    wsb_total = f"{total:.2f}"

    wsb_signature = compute_wsb_signature(
        wsb_seed, wsb_storeid, wsb_order_num, wsb_test, wsb_currency_id, wsb_total, "1q2w3e4r5t6y7u8i9o0", version=2
    )

    user_profile = request.user.profile
    wsb_customer_name = user_profile.full_name if user_profile.full_name else request.user.username
    wsb_customer_address = user_profile.city
    wsb_email = request.user.email
    wsb_phone = user_profile.phone

    wsb_return_url = request.build_absolute_uri(reverse('payments:payment_success'))
    wsb_cancel_return_url = request.build_absolute_uri(reverse('payments:payment_cancel'))
    wsb_notify_url = request.build_absolute_uri(reverse('payments:payment_notify'))

    invoice_item_name = "Подписка на платный тариф"
    invoice_item_quantity = "1"
    invoice_item_price = wsb_total

    context = {
        'wsb_payment_url': "https://securesandbox.webpay.by/",
        'wsb_version': "2",
        'wsb_language_id': "russian",
        'wsb_storeid': wsb_storeid,
        'wsb_store': "My Shop",
        'wsb_order_num': wsb_order_num,
        'wsb_test': wsb_test,
        'wsb_currency_id': wsb_currency_id,
        'wsb_seed': wsb_seed,
        'wsb_customer_name': wsb_customer_name,
        'wsb_customer_address': wsb_customer_address,
        'wsb_return_url': wsb_return_url,
        'wsb_cancel_return_url': wsb_cancel_return_url,
        'wsb_notify_url': wsb_notify_url,
        'wsb_email': wsb_email,
        'wsb_phone': wsb_phone,
        'invoice_item_name': invoice_item_name,
        'invoice_item_quantity': invoice_item_quantity,
        'invoice_item_price': invoice_item_price,
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
        profile.subscription_start = now
        profile.subscription_end = now + relativedelta(months=order.duration)
        profile.tariff = order.tariff_type  # обновляем тариф согласно заказу
        profile.save()
        return render(request, 'payments/payment_success.html', {'order': order})
    except PaymentOrder.DoesNotExist:
        return HttpResponse("Заказ не найден или уже обработан.", status=404)


@login_required
def payment_cancel(request):
    """
    Обрабатывает возврат при отмене платежа.
    """
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
    """
    Обрабатывает POST-нотификатор от Webpay.by.

    В нотификаторе передаются поля:
      batch_timestamp, currency_id, amount, payment_method, order_id,
      site_order_id, transaction_id, payment_type, rrn, [card], wsb_signature, и другие.

    Функция проверяет подпись и, если всё корректно, обновляет заказ и тариф пользователя.

    Если оповещение не получено в течение 20 минут, рекомендуется использовать API get_transaction_status.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Метод не поддерживается")

    # Проверяем подпись нотификатора
    if not verify_notify_signature(request.POST, WSB_SECRET_KEY):
        return HttpResponse("Неверная подпись", status=400)

    # Предполагаем, что наш заказ идентифицируется через поле order_id (сайтский идентификатор заказа)
    order_num = request.POST.get('site_order_id')  # или используйте другой параметр, если он передаётся
    try:
        order = PaymentOrder.objects.get(order_number=order_num, status='pending')
        # Проверяем тип транзакции, успешной оплате соответствуют payment_type 1, 4, 10, 23
        payment_type = request.POST.get('payment_type', '')
        if payment_type in ['1', '4', '10', '23']:
            order.status = 'paid'
            order.transaction_id = request.POST.get('transaction_id', '')
            order.invoice_number = request.POST.get('order_id', '')
            order.save()
            order.user.profile.tariff = 'paid'
            order.user.profile.save()
            # Возвращаем корректный ответ – для POST-запроса достаточно статус 200 и текст "OK"
            return HttpResponse("OK", status=200)
        else:
            order.status = 'cancelled'
            order.save()
            return HttpResponse("Платеж неуспешный", status=400)
    except PaymentOrder.DoesNotExist:
        return HttpResponse("Заказ не найден", status=404)


@login_required
def choose_subscription(request):
    tariff_options = [
        {
            'type': 'standard',
            'label': 'Стандарт (до 1000 запчастей)',
            'durations': [
                {'duration': 1, 'price': 30.00, 'label': '1 месяц – 30 руб'},
                {'duration': 3, 'price': 90.00, 'label': '3 месяца – 90 руб'},
                {'duration': 6, 'price': 180.00, 'label': '6 месяцев – 180 руб'},
                {'duration': 12, 'price': 360.00, 'label': '12 месяцев – 360 руб'},
            ]
        },
        {
            'type': 'premium',
            'label': 'Премиум (без ограничений)',
            'durations': [
                {'duration': 1, 'price': 100.00, 'label': '1 месяц – 100 руб'},
                {'duration': 3, 'price': 300.00, 'label': '3 месяца – 300 руб'},
                {'duration': 6, 'price': 600.00, 'label': '6 месяцев – 600 руб'},
                {'duration': 12, 'price': 1200.00, 'label': '12 месяцев – 1200 руб'},
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
    return render(request, 'payments/choose_subscription.html', {'tariff_options': tariff_options})
