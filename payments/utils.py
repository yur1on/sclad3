# payments/utils.py
import hashlib


def compute_wsb_signature(wsb_seed, wsb_storeid, wsb_order_num, wsb_test, wsb_currency_id, wsb_total, secret_key, version=2):
    """
    Вычисляет электронную подпись заказа для формирования формы оплаты.
    Порядок объединения:
      wsb_seed + wsb_storeid + wsb_order_num + wsb_test + wsb_currency_id + wsb_total + SecretKey
    Для версии 2 используется SHA1, иначе MD5.
    """
    data_string = f"{wsb_seed}{wsb_storeid}{wsb_order_num}{wsb_test}{wsb_currency_id}{wsb_total}{secret_key}"
    if version == 2:
        return hashlib.sha1(data_string.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(data_string.encode('utf-8')).hexdigest()


def verify_notify_signature(post_data, secret_key):
    """
    Проверяет подпись, полученную в нотификаторе от Webpay.by.
    Используемые поля (в порядке конкатенации):
      batch_timestamp, currency_id, amount, payment_method, order_id,
      site_order_id, transaction_id, payment_type, rrn,
      [card - если передан]
      + secret_key.

    Функция вычисляет MD5 от конкатенированной строки и сравнивает с переданным wsb_signature.
    """
    fields = [
        post_data.get('batch_timestamp', ''),
        post_data.get('currency_id', ''),
        post_data.get('amount', ''),
        post_data.get('payment_method', ''),
        post_data.get('order_id', ''),
        post_data.get('site_order_id', ''),
        post_data.get('transaction_id', ''),
        post_data.get('payment_type', ''),
        post_data.get('rrn', '')
    ]
    # Если передано поле card – добавляем его в подпись
    card = post_data.get('card', '')
    if card:
        fields.append(card)

    data_string = "".join(fields) + secret_key
    computed_signature = hashlib.md5(data_string.encode('utf-8')).hexdigest()
    provided_signature = post_data.get('wsb_signature', '')
    return computed_signature == provided_signature
