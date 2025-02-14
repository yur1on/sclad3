import hashlib
import time
import uuid
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Subscription, Payment

@login_required
def subscription_page(request):
    """
    Страница выбора подписки.
    Здесь пользователь выбирает план подписки.
    """
    return render(request, "payments/subscription.html")

@login_required
def create_payment(request):
    """
    Обработка формы выбора подписки и создание платежа.
    Формируются все необходимые поля для WebPay, затем рендерится шаблон редиректа.
    """
    if request.method == "POST":
        # Получаем выбранный план из формы
        plan_name = request.POST.get("plan_name")
        # Определяем цену подписки в зависимости от плана
        if plan_name == "Basic":
            price = "10.00"
        elif plan_name == "Premium":
            price = "20.00"
        else:
            price = "10.00"

        # Создаем запись подписки (будет активирована после успешной оплаты)
        subscription = Subscription.objects.create(
            user=request.user,
            plan_name=plan_name,
            price=price,
            is_active=False
        )

        # Генерируем уникальный идентификатор заказа (используем UUID)
        order_id = str(uuid.uuid4())
        # Используем текущее время как seed (можно использовать Unix Timestamp)
        seed = str(int(time.time()))
        # Поле wsb_test: "1" для тестовой оплаты
        test_mode = "1" if settings.WEBPAY_TEST_MODE else "0"

        # Расчет электронной подписи заказа.
        # Согласно документации для версии 1 (если не указан wsb_version) используется MD5.
        # Объединяем значения в следующем порядке:
        # wsb_seed + wsb_storeid + wsb_order_num + wsb_test + wsb_currency_id + wsb_total + SecretKey
        data_to_sign = f"{seed}{settings.WEBPAY_STORE_ID}{order_id}{test_mode}BYN{price}{settings.WEBPAY_SECRET_KEY}"
        signature = hashlib.md5(data_to_sign.encode("utf-8")).hexdigest()

        # Сохраняем платеж с первоначальным статусом "pending"
        Payment.objects.create(
            subscription=subscription,
            amount=price,
            transaction_id=order_id,
            status="pending"
        )

        # Формируем словарь с параметрами для WebPay
        # Обязательные поля (см. документацию):
        # *scart – поле не содержит значения (можно оставить пустым)
        # wsb_storeid, wsb_order_num, wsb_currency_id, wsb_seed, wsb_signature, wsb_return_url, wsb_cancel_return_url, wsb_test
        payment_data = {
            "*scart": "",  # Поле пустое
            "wsb_storeid": settings.WEBPAY_STORE_ID,
            "wsb_order_num": order_id,
            "wsb_currency_id": "BYN",
            "wsb_seed": seed,
            "wsb_signature": signature,
            "wsb_return_url": request.build_absolute_uri("/payments/pay/success/"),
            "wsb_cancel_return_url": request.build_absolute_uri("/payments/pay/cancel/"),
            "wsb_test": test_mode,
            # Дополнительные поля можно добавить при необходимости, например, wsb_version, wsb_language_id и т.д.
        }

        # Рендерим шаблон, который автоматически отправит форму на WebPay
        return render(request, "payments/webpay_redirect.html", {
            "webpay_url": settings.WEBPAY_URL,
            "payment_data": payment_data
        })

    return redirect("subscription_page")

def payment_success(request):
    """
    Страница, отображаемая после успешной оплаты.
    Здесь можно обновить статус подписки на активный.
    """
    # Здесь можно извлечь параметр wsb_order_num из GET-параметров и обновить статус соответствующего платежа.
    return render(request, "payments/success.html")

def payment_cancel(request):
    """
    Страница, отображаемая, если оплата отменена.
    """
    return render(request, "payments/cancel.html")
